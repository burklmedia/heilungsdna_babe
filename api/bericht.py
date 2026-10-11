"""
Vercel Serverless Function: POST /api/bericht (seit 11.10.2026)

Zwei kleine Aktionen am Ende des Berichts:

  {"aktion": "warteliste", "t": "<feedback-token>"}   oder   {"aktion": "warteliste", "email": "..."}
      Haengt das Tag "Warteliste Liebesanalyse" an den BESTEHENDEN Kontakt in ActiveCampaign.
      Der Token kommt ueber den Link in Mail 1 (&t=%FEEDBACK_TOKEN%) und wird wie beim Feedback
      ueber die KV (imh:fbtok:<t>) zur E-Mail aufgeloest. Ohne Token tippt die Leserin ihre
      Adresse ein; getaggt wird nur, wen es schon als Kontakt gibt. Es wird nie jemand angelegt.

  {"aktion": "stand", "k": "<32 Hex-Zeichen>", "erst": <ms>, "nr": <Karte>, "tag": <Tagnummer>}
      Gleicht den Stand der Überraschungen zwischen Geräten ab (Safari, App auf dem Startbildschirm,
      Desktop). k ist ein SHA-256-Hash der Geburtsangaben, den das Gerät selbst bildet; gespeichert
      werden nur dieser Hash, der Zeitpunkt des ersten Öffnens und die zuletzt gezogene Karte (400 Tage).

  {"aktion": "frage", "text": "..."}
      Speichert eine anonyme Frage (ohne Name, ohne E-Mail) in der KV-Liste imh:fragen;
      Denise liest sie in /api/stats. In die Telegram-Gruppe geht nur der Hinweis, nicht der Text.

Grob begrenzt: je Geraet (Hash der IP) hoechstens 20 Aufrufe pro Stunde.
Im Log stehen nie E-Mail, Token oder Fragetext.
"""
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import kv_get, kv_set, kv_incr_ttl, push_feedback
except Exception:  # noqa
    def kv_get(k):
        return None

    def kv_set(k, v, ttl=None):
        return False

    def kv_incr_ttl(k, ttl):
        return None

    def push_feedback(r, key="imh:feedback"):
        return False

from _ac import TAG_WARTELISTE_LIEBE, add_tag  # noqa: E402
import _telegram as telegram  # noqa: E402

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_TOKEN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
FRAGE_MAX = 800
LIMIT_PRO_STUNDE = 20


def _begrenzt(ip):
    h = hashlib.sha256(("imh-bericht|" + (ip or "")).encode("utf-8")).hexdigest()[:20]
    n = kv_incr_ttl("imh:rl:bericht:" + h, 3600)
    return isinstance(n, int) and n > LIMIT_PRO_STUNDE


_STAND_K = re.compile(r"^[a-f0-9]{32}$")
STAND_TTL = 400 * 86400
ERST_MIN = 1767225600000  # 01.01.2026


def _zahl(x, lo, hi):
    try:
        v = int(x)
    except (TypeError, ValueError):
        return None
    return v if lo <= v <= hi else None


def stand(body, ip=""):
    """Stand der Überraschungen geräteübergreifend: frühestes erstes Öffnen, höchste gezogene Karte."""
    k = body.get("k") if isinstance(body.get("k"), str) else ""
    if not _STAND_K.match(k):
        return 400, {"ok": False, "error": "bad_key"}
    h = hashlib.sha256(("imh-stand|" + (ip or "")).encode("utf-8")).hexdigest()[:20]
    n = kv_incr_ttl("imh:rl:stand:" + h, 3600)
    if isinstance(n, int) and n > 240:
        return 429, {"ok": False, "error": "rate_limited"}
    jetzt = int(datetime.now(timezone.utc).timestamp() * 1000)
    erst = _zahl(body.get("erst"), ERST_MIN, jetzt + 86400000)
    nr = _zahl(body.get("nr"), 0, 1000)
    tag = _zahl(body.get("tag"), 0, 100000)
    alt = {}
    roh = kv_get("imh:stand:" + k)
    if roh:
        try:
            alt = json.loads(roh) if isinstance(roh, str) else {}
        except ValueError:
            alt = {}
    neu = {"erst": alt.get("erst"), "nr": alt.get("nr") or 0, "tag": alt.get("tag")}
    if erst and (not neu["erst"] or erst < neu["erst"]):
        neu["erst"] = erst
    if body.get("neu") is True and neu["nr"] >= 180:
        neu["nr"], neu["tag"] = 0, None   # Reise nach allen 180 Karten neu beginnen
    elif nr is not None and nr > neu["nr"]:
        neu["nr"], neu["tag"] = nr, tag
    if neu != {"erst": alt.get("erst"), "nr": alt.get("nr") or 0, "tag": alt.get("tag")}:
        kv_set("imh:stand:" + k, json.dumps(neu), ttl=STAND_TTL)
    return 200, dict(neu, ok=True)


def handle(body, ip=""):
    aktion = body.get("aktion") if isinstance(body.get("aktion"), str) else ""
    if aktion == "stand":
        return stand(body, ip)
    if aktion not in ("warteliste", "frage"):
        return 400, {"ok": False, "error": "unknown_action"}
    if _begrenzt(ip):
        return 429, {"ok": False, "error": "rate_limited",
                     "message": "Das war gerade etwas viel. Bitte versuch es später noch einmal."}

    if aktion == "warteliste":
        t = body.get("t") if isinstance(body.get("t"), str) else ""
        email = ""
        if t and _TOKEN.match(t.strip()):
            email = kv_get("imh:fbtok:" + t.strip()) or ""
        if not email:
            roh = body.get("email") if isinstance(body.get("email"), str) else ""
            roh = roh.strip()[:254]
            if not _EMAIL.match(roh):
                return 400, {"ok": False, "error": "need_email",
                             "message": "Bitte gib die E-Mail-Adresse ein, mit der du deinen Bauplan bekommen hast."}
            email = roh
        ok, grund = add_tag(email, TAG_WARTELISTE_LIEBE)
        if ok:
            return 200, {"ok": True}
        if grund == "kein_kontakt":
            return 404, {"ok": False, "error": "unknown_contact",
                         "message": "Diese Adresse kenne ich noch nicht. Nimm bitte die, mit der du deinen Bauplan bekommen hast."}
        return 502, {"ok": False, "error": "upstream",
                     "message": "Das hat gerade nicht geklappt. Bitte versuch es gleich noch einmal."}

    text = body.get("text") if isinstance(body.get("text"), str) else ""
    text = re.sub(r"\s+", " ", text).strip()[:FRAGE_MAX]
    if len(text) < 3:
        return 400, {"ok": False, "error": "empty", "message": "Schreib mir gern ein paar Worte."}
    gespeichert = push_feedback({"zeit": datetime.now(timezone.utc).isoformat(timespec="seconds"), "frage": text},
                                key="imh:fragen")
    if not gespeichert:
        return 503, {"ok": False, "error": "not_stored",
                     "message": "Das hat gerade nicht geklappt. Bitte versuch es später noch einmal."}
    telegram.melden("Neue Frage aus einem Bauplan ✦ Lesen unter /api/stats")
    return 200, {"ok": True}


class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            length = min(int(self.headers.get("content-length", 0)), 8192)
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                body = {}
            ip = (self.headers.get("x-forwarded-for") or "").split(",")[0].strip()
            code, payload = handle(body, ip)
            self._send(code, payload)
        except Exception as e:  # noqa
            print("[bericht] Fehler", type(e).__name__)
            self._send(500, {"ok": False, "error": "server_error"})
