"""
Vercel Serverless Function: sichere Uebergabe eines abgeleiteten Profil-Subsets
an das Paid Product (Heilungs-DNA).

ADDITIV. Aendert weder Funnel, Berechnung, PDF-Ausgabe noch E-Mail-Versand.
Nutzt ausschliesslich die bestehende Berechnung (analyze.build_result), es gibt
KEINE zweite Engine.

Zwei Schritte:

  POST /api/handoff
      Body: die bekannten Geburtsfelder (wie /api/analyze) + "challenge".
      Rechnet serverseitig, extrahiert NUR das freigegebene Subset, legt es unter
      einem opaken Zufalls-Token mit kurzer TTL im KV ab und gibt den Token zurueck.
      Der Token enthaelt selbst keine Daten.

  POST /api/handoff/claim
      Header: X-Handoff-Secret  (Server-zu-Server, nie im Browser)
      Body:   {"token": ..., "verifier": ...}
      Holt den Eintrag ATOMAR per GETDEL (Einmal-Abholung, kein Replay), prueft
      sha256(verifier) gegen die beim Start hinterlegte challenge und gibt das
      Subset genau einmal zurueck.

Sicherheitsmerkmale:
  - Der Nutzer startet den Vorgang ausdruecklich selbst.
  - Serverseitige Berechnung ist die einzige vertrauenswuerdige Datenquelle;
    vom Browser behauptete Profilwerte werden nie uebernommen.
  - Opaker Zufalls-Token, kurze Gueltigkeit, atomare Einmal-Abholung.
  - Bindung an den startenden Browser ueber challenge/verifier (der Token allein,
    z. B. aus der Browser-History, genuegt nicht).
  - Zusaetzlich Server-zu-Server-Authentisierung ueber ein Shared Secret.
  - Keine Geburtsdaten und keine vollstaendigen Profile in URLs.
  - Keine Tokens, Secrets oder Profildaten in Logs oder Fehlertexten.
  - Payload-Begrenzung, no-store, no-referrer.

Aktivierung (beide muessen gesetzt sein, sonst 503 und die Funktion ist inert):
  HANDOFF_ENABLED        = "1"
  HANDOFF_SHARED_SECRET  = <starkes Zufallsgeheimnis>
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import sys
import hmac
import hashlib
import base64
import secrets

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_IMPORT_ERROR = None
try:
    from analyze import build_result
    from _store import kv_set, kv_getdel, kv_incr_ttl, configured
except Exception:  # noqa
    import traceback
    _IMPORT_ERROR = traceback.format_exc()

# --- Konstanten -------------------------------------------------------------

CONTRACT_VERSION = 1
TOKEN_TTL_SECONDS = 600          # 10 Minuten
MAX_BODY_BYTES = 8 * 1024        # Payload-Begrenzung
KEY_PREFIX = "imh:bp:"

# Rate Limits pro Client und Zeitfenster. Bewusst grosszuegig fuer echte Nutzer,
# aber eng genug gegen automatisiertes Durchprobieren von Tokens.
RATE_WINDOW_SECONDS = 300
RATE_LIMIT_START = 10            # Berechnungen sind teuer
RATE_LIMIT_CLAIM = 30

# Stabile, sprachunabhaengige Codes. Die deutschen Anzeigestrings des Freebies
# bleiben dort; der Vertrag zum Paid Product ist bewusst entkoppelt.
HD_TYPE = {
    "Manifestor": "MANIFESTOR",
    "Generator": "GENERATOR",
    "Manifestierender Generator": "MANIFESTING_GENERATOR",
    "Projektor": "PROJECTOR",
    "Reflektor": "REFLECTOR",
}
HD_AUTHORITY = {
    "Emotionale Autorität": "EMOTIONAL",
    "Sakrale Autorität": "SACRAL",
    "Milz-Autorität (Splenisch)": "SPLENIC",
    "Ego-/Herz-Autorität": "EGO",
    "Selbst-projizierte Autorität": "SELF",
    "Mentale Autorität (Umgebung)": "MENTAL",
    "Mond-Autorität (Reflektor)": "LUNAR",
}
HD_CENTER = {
    "Kopf": "HEAD", "Ajna": "AJNA", "Kehle": "THROAT", "G": "G",
    "Milz": "SPLEEN", "Sakral": "SACRAL", "Herz": "HEART",
    "Solarplexus": "SOLAR_PLEXUS", "Wurzel": "ROOT",
}
SIGN = {
    "Widder": "ARIES", "Stier": "TAURUS", "Zwillinge": "GEMINI", "Krebs": "CANCER",
    "Löwe": "LEO", "Jungfrau": "VIRGO", "Waage": "LIBRA", "Skorpion": "SCORPIO",
    "Schütze": "SAGITTARIUS", "Steinbock": "CAPRICORN", "Wassermann": "AQUARIUS",
    "Fische": "PISCES",
}


def _enabled():
    return os.environ.get("HANDOFF_ENABLED") == "1"


def _secret():
    return os.environ.get("HANDOFF_SHARED_SECRET") or ""


def _b64url_sha256(value):
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _client_key(headers):
    """Grober Client-Schluessel fuer das Rate Limit. Nur der erste Eintrag aus
    X-Forwarded-For; wird ausschliesslich gehasht als Zaehlerschluessel benutzt
    und nirgends gespeichert oder geloggt."""
    raw = (headers.get("x-forwarded-for") or headers.get("x-real-ip") or "unknown")
    first = raw.split(",")[0].strip() or "unknown"
    return hashlib.sha256(first.encode("utf-8")).hexdigest()[:16]


def _rate_limited(headers, bucket, limit):
    """True, wenn das Limit ueberschritten ist. Ohne Speicher: keine Begrenzung
    moeglich, dann wird durchgelassen (die Funktion ist ohne KV ohnehin inert)."""
    key = "imh:rl:%s:%s" % (bucket, _client_key(headers))
    count = kv_incr_ttl(key, RATE_WINDOW_SECONDS)
    if count is None:
        return False
    return count > limit


def _same_origin_ok(headers):
    """Der Start wird von der eigenen Uebergabeseite aufgerufen. Wenn der Browser
    einen Origin schickt, muss er zum eigenen Host passen. Fehlt der Header
    (z. B. serverseitige Aufrufe), greift weiterhin das Rate Limit."""
    origin = headers.get("origin")
    if not origin:
        return True
    host = (headers.get("host") or "").lower()
    try:
        return urlparse(origin).netloc.lower() == host
    except Exception:  # noqa
        return False


def _map_list(values, table):
    out = []
    for v in values or []:
        code = table.get(v)
        if code and code not in out:
            out.append(code)
    return out


def build_subset(result, time_known):
    """Extrahiert AUSSCHLIESSLICH das freigegebene Subset aus dem bereits
    berechneten Ergebnis. Fehlende Werte werden weggelassen, nie geraten.
    Es werden KEINE Geburtsdaten, Tore, Kanaele, Natal-Charts oder Deutungstexte
    uebernommen."""
    full = (result or {}).get("full") or {}
    teaser = (result or {}).get("teaser") or {}
    hd = full.get("hd") or {}

    subset = {"contractVersion": CONTRACT_VERSION, "timeKnown": bool(time_known)}

    hd_out = {}
    t = HD_TYPE.get(hd.get("type"))
    a = HD_AUTHORITY.get(hd.get("authority"))
    if t:
        hd_out["type"] = t
    if a:
        hd_out["authority"] = a
    prof = hd.get("profile")
    if isinstance(prof, str) and 0 < len(prof) <= 40:
        hd_out["profile"] = prof
    defined = _map_list(hd.get("defined_centers"), HD_CENTER)
    opened = _map_list(hd.get("open_centers"), HD_CENTER)
    if defined:
        hd_out["definedCenters"] = defined
    if opened:
        hd_out["openCenters"] = opened
    if hd_out:
        subset["hd"] = hd_out

    astro = {}
    sun = SIGN.get(teaser.get("sun_sign"))
    moon = SIGN.get(teaser.get("moon_sign"))
    if sun:
        astro["sunSign"] = sun
    if moon:
        astro["moonSign"] = moon
    if time_known:
        asc = full.get("ascendant")
        asc_sign = asc.get("sign") if isinstance(asc, dict) else None
        code = SIGN.get(asc_sign)
        if code:
            astro["ascSign"] = code
    if astro:
        subset["astro"] = astro

    intu = full.get("intuition")
    if isinstance(intu, dict):
        arch = intu.get("archetype")
        if isinstance(arch, str) and 0 < len(arch) <= 40:
            subset["intuition"] = {"archetype": arch}

    num = full.get("numerology")
    if isinstance(num, dict):
        n = {}
        lp = num.get("lifepath")
        if isinstance(lp, int) and 1 <= lp <= 33:
            n["lifepath"] = lp
        if isinstance(num.get("is_master"), bool):
            n["isMaster"] = num.get("is_master")
        if n:
            subset["numerology"] = n

    return subset


def _kv_selftest():
    """Synthetischer KV-Rundlauf: schreiben, ATOMAR abholen, pruefen dass der
    Schluessel danach weg ist. Isolierter Zufallsschluessel mit kurzer TTL, raeumt
    sich selbst auf. Gibt ausschliesslich Booleans zurueck, nie Werte oder
    Zugangsdaten. Belegt zugleich, dass GETDEL verfuegbar ist."""
    key = KEY_PREFIX + "selftest:" + secrets.token_urlsafe(8)
    marker = secrets.token_urlsafe(8)
    wrote = bool(kv_set(key, marker, ttl=60))
    got = kv_getdel(key) if wrote else None
    gone = kv_getdel(key) is None
    return {
        "write": wrote,
        "atomic_read": got == marker,
        "deleted_after_read": bool(gone),
        "getdel_supported": got == marker and bool(gone),
    }


class handler(BaseHTTPRequestHandler):
    # --- Antwort-Helfer -----------------------------------------------------
    def _send(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self):
        length = int(self.headers.get("content-length", 0) or 0)
        if length > MAX_BODY_BYTES:
            return None
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        # Nicht-sensitive Diagnose: nur Konfigurationsstatus, keine Werte.
        info = {
            "ok": True,
            "service": "Bauplan-Handoff",
            "enabled": _enabled(),
            "secret_present": bool(_secret()),
            "kv_configured": bool(configured()) if not _IMPORT_ERROR else False,
            "contractVersion": CONTRACT_VERSION,
        }
        # Optionaler, isolierter KV-Rundlauf mit synthetischem Schluessel.
        want = (parse_qs(urlparse(self.path).query).get("selftest") or [""])[0]
        if want == "1" and not _IMPORT_ERROR and configured():
            if _rate_limited(self.headers, "selftest", 5):
                info["kv_selftest"] = {"skipped": "rate_limited"}
            else:
                info["kv_selftest"] = _kv_selftest()
        self._send(200, info)

    def do_POST(self):
        if _IMPORT_ERROR:
            return self._send(500, {"ok": False, "error": "Import fehlgeschlagen."})
        if not _enabled():
            return self._send(503, {"ok": False, "error": "Übergabe ist nicht aktiviert."})
        if not configured():
            return self._send(503, {"ok": False, "error": "Speicher nicht verfügbar."})

        path = urlparse(self.path).path.rstrip("/")
        if path.endswith("/claim"):
            return self._claim()
        return self._start()

    # --- Schritt 1: Start ---------------------------------------------------
    def _start(self):
        if not _same_origin_ok(self.headers):
            return self._send(403, {"ok": False, "error": "Ungültige Herkunft."})
        if _rate_limited(self.headers, "start", RATE_LIMIT_START):
            return self._send(429, {"ok": False, "error": "Zu viele Versuche. Bitte später erneut."})
        try:
            body = self._read_body()
        except Exception:  # noqa
            return self._send(400, {"ok": False, "error": "Ungültige Anfrage."})
        if body is None:
            return self._send(413, {"ok": False, "error": "Anfrage zu groß."})

        challenge = (body.get("challenge") or "").strip()
        # base64url(sha256) ist 43 Zeichen ohne Padding.
        if not (32 <= len(challenge) <= 64):
            return self._send(400, {"ok": False, "error": "Ungültiger Startwert."})

        try:
            time_known = bool((body.get("time") or "").strip())
            result = build_result(body)          # bestehende Berechnung, keine zweite Engine
        except ValueError as e:
            return self._send(400, {"ok": False, "error": str(e)})
        except Exception:  # noqa
            return self._send(500, {"ok": False, "error": "Berechnung fehlgeschlagen."})

        subset = build_subset(result, time_known)
        token = secrets.token_urlsafe(32)
        record = json.dumps({"challenge": challenge, "subset": subset}, ensure_ascii=False)
        if not kv_set(KEY_PREFIX + token, record, ttl=TOKEN_TTL_SECONDS):
            return self._send(503, {"ok": False, "error": "Übergabe konnte nicht vorbereitet werden."})

        # Nur der opake Token verlaesst den Server. Keine Profildaten in der URL.
        return self._send(200, {"ok": True, "token": token, "expiresInSeconds": TOKEN_TTL_SECONDS})

    # --- Schritt 2: Abholung (Server zu Server) -----------------------------
    def _claim(self):
        if _rate_limited(self.headers, "claim", RATE_LIMIT_CLAIM):
            return self._send(429, {"ok": False, "error": "Zu viele Versuche. Bitte später erneut."})
        expected = _secret()
        provided = self.headers.get("X-Handoff-Secret") or ""
        if not expected or not hmac.compare_digest(expected, provided):
            # Bewusst unspezifisch, kein Hinweis auf den Grund.
            return self._send(401, {"ok": False, "error": "Nicht autorisiert."})

        try:
            body = self._read_body()
        except Exception:  # noqa
            return self._send(400, {"ok": False, "error": "Ungültige Anfrage."})
        if body is None:
            return self._send(413, {"ok": False, "error": "Anfrage zu groß."})

        token = (body.get("token") or "").strip()
        verifier = (body.get("verifier") or "").strip()
        if not token or not verifier or len(token) > 128 or len(verifier) > 256:
            return self._send(400, {"ok": False, "error": "Ungültige Übergabe."})

        # ATOMAR: lesen und loeschen in einem Schritt -> kein Replay, kein Race.
        raw = kv_getdel(KEY_PREFIX + token)
        if not raw:
            return self._send(410, {"ok": False, "error": "Übergabe abgelaufen oder bereits verwendet."})

        try:
            record = json.loads(raw)
        except Exception:  # noqa
            return self._send(410, {"ok": False, "error": "Übergabe ungültig."})

        # Bindung an den Browser, der den Vorgang gestartet hat.
        if not hmac.compare_digest(record.get("challenge") or "", _b64url_sha256(verifier)):
            return self._send(403, {"ok": False, "error": "Übergabe gehört nicht zu diesem Vorgang."})

        return self._send(200, {"ok": True, "profile": record.get("subset")})
