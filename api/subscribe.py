"""
Vercel Serverless Function: POST /api/subscribe

Nimmt Vorname, E-Mail und den Bauplan-Parameter d vom Bauplan entgegen und
reicht sie an das ActiveCampaign-Formular "Kosmischer Bauplan" weiter, genau
wie das MUSTER-Quiz.

Warum ueber das Formular und nicht ueber die REST-API:
ActiveCampaign stellt den Double-Opt-in auf FORMULAR-Ebene ein, nicht auf
Listenebene. Und an Kontakte mit Status "unbestaetigt" verschickt AC gar keine
Mails, eine selbstgebaute Bestaetigungsmail per Automation kaeme also nie an.
Der Weg ueber das Formular loest AC's eigene Opt-in-Mail aus. Erst nach dem
Klick wird der Kontakt auf der Liste aktiv, und die Automation (Ausloeser:
abonniert die Liste) schickt Mail 1 mit dem Link zu /mein-bauplan?d=%BAUPLAN_PDF%.

Es wird KEIN API-Key gebraucht. Die Werte unten stehen so im oeffentlichen
Einbettungscode des Formulars. Der Feedback-Token entsteht wie bisher hier,
wird in der KV der E-Mail zugeordnet und als Feld mitgeschickt.

GET liefert nur eine ja/nein-Diagnose.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request

# Damit die Sibling-Imports (_store, _ac) auf Vercel und lokal funktionieren.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from _store import kv_set
except Exception:  # noqa
    def kv_set(*a, **k):
        return False
from _ac import FIELD_BAUPLAN_PDF, FIELD_FEEDBACK_TOKEN, configured as ac_api_configured  # noqa: E402

AC_ENDPOINT = "https://burkl-media.activehosted.com/proc.php"

# Aus dem Einbettungscode des Formulars "Kosmischer Bauplan" (Formular 5,
# Stand 24.09.2026). Aendert sich nur, wenn das Formular in AC neu angelegt
# wird. Sind die Werte leer, nimmt die Funktion keine Anmeldung an (503),
# statt Adressen still zu verlieren.
FORM = {
    "u": "5",
    "f": "5",
    "or": "46147309-8920-4753-8a68-eaae72cc439c",
}

# Feldnummern aus dem Einbettungscode: window.cfields = {"4":"bauplan_pdf","5":"feedback_token"}
# Sie sind zugleich die Feld-IDs in ActiveCampaign (siehe api/_ac.py).
FELD_BAUPLAN_PDF = "field[%s]" % FIELD_BAUPLAN_PDF
FELD_FEEDBACK_TOKEN = "field[%s]" % FIELD_FEEDBACK_TOKEN

# dev.py setzt das auf True: lokal geht nichts an ActiveCampaign, solange
# BAUPLAN_AC_LIVE nicht gesetzt ist.
DRY_RUN = False

# So lange gilt die Zuordnung Feedback-Token -> E-Mail (in der KV).
_FB_TOKEN_TTL = 120 * 24 * 3600

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_D_PARAM = re.compile(r"^[A-Za-z0-9_-]{1,2000}$")


def form_connected():
    return all(FORM.values())


def _feedback_token_for(email):
    """Erzeugt einen opaken Zufalls-Token (kein E-Mail-Bestandteil, nicht
    umkehrbar), legt das Mapping Token->E-Mail serverseitig in der KV ab und gibt
    den Token zurueck. Ohne verbundenen Speicher -> None (dann wird kein Token
    gesetzt, der ohnehin nicht aufloesbar waere)."""
    try:
        token = secrets.token_urlsafe(18)
        if kv_set("imh:fbtok:" + token, email, ttl=_FB_TOKEN_TTL):
            return token
    except Exception:  # noqa
        pass
    return None


def _submit(fields):
    """Schickt die Felder an proc.php. Rueckgabe (ok, fehlercode)."""
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        AC_ENDPOINT, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            text = r.read(8192).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        print("[activecampaign] Formular HTTP", e.code)
        return False, "upstream_http"
    except Exception as e:  # noqa
        print("[activecampaign] Formular nicht erreichbar", type(e).__name__)
        return False, "upstream_unreachable"
    # Mit jsonp=true antwortet proc.php mit JavaScript: _show_thank_you(...) bei
    # Erfolg, _show_error(...) bei einem Problem. Der HTTP-Status ist in beiden
    # Faellen 200, deshalb wird die Antwort selbst geprueft.
    if "_show_error" in text:
        print("[activecampaign] Formular lehnt ab:", re.sub(r"\S+@\S+", "<email>", text)[:200])
        return False, "upstream_rejected"
    if "_show_thank_you" not in text:
        print("[activecampaign] unerwartete Antwort ohne _show_thank_you")
    return True, None


def handle_subscribe(body):
    """Kernlogik. Rueckgabe (http_code, payload_dict). Ohne HTTP-Handler testbar."""
    email = body.get("email") if isinstance(body.get("email"), str) else ""
    email = email.strip()
    if len(email) > 254 or not _EMAIL.match(email):
        return 400, {"ok": False, "error": "invalid_email",
                     "message": "Bitte gib eine gültige E-Mail an."}
    name = body.get("name") if isinstance(body.get("name"), str) else ""
    name = name.strip()[:80]
    # Persoenlicher Bauplan-Parameter (base64url der Geburtsangaben). In der
    # Mail steht dann https://bauplan.intuitionmitherz.de/mein-bauplan?d=%BAUPLAN_PDF%
    d = body.get("d") if isinstance(body.get("d"), str) else ""
    d = d.strip()
    if d and not _D_PARAM.match(d):
        d = ""

    if DRY_RUN:
        return 200, {"ok": True, "stored": True, "dry_run": True}

    if not form_connected():
        print("[activecampaign] Formular noch nicht verbunden (FORM leer)")
        return 503, {"ok": False, "stored": False, "error": "not_configured",
                     "message": "Die Anmeldung ist gerade nicht erreichbar. Bitte versuche es später noch einmal."}

    fields = {
        "u": FORM["u"],
        "f": FORM["f"],
        "s": "",
        "c": "0",
        "m": "0",
        "act": "sub",
        "v": "2",
        "or": FORM["or"],
        "email": email,
        "firstname": name,
        "jsonp": "true",
    }
    if d:
        fields[FELD_BAUPLAN_PDF] = d
    # Opaker Feedback-Token fuer die Links zu /feedback und /thema.
    tok = _feedback_token_for(email)
    if tok:
        fields[FELD_FEEDBACK_TOKEN] = tok

    ok, error = _submit(fields)
    if not ok:
        return 502, {"ok": False, "stored": False, "error": error,
                     "message": "Das hat gerade nicht geklappt. Bitte versuche es noch einmal."}
    # Kontakt liegt jetzt als "unbestaetigt" in AC, die Opt-in-Mail ist raus.
    return 200, {"ok": True, "stored": True}


class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        # Diagnose: ist alles verbunden? (nur ja/nein, keine Werte)
        self._send(200, {
            "ok": True,
            "ac_form_connected": form_connected(),
            "ac_api_configured": ac_api_configured(),
            "mailerlite_key_present": bool(os.environ.get("MAILERLITE_API_KEY")),
        })

    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                body = {}
            code, payload = handle_subscribe(body)
            self._send(code, payload)
        except Exception as e:  # noqa
            print("[subscribe] Fehler", type(e).__name__)
            self._send(500, {"ok": False, "stored": False, "error": "server_error"})
