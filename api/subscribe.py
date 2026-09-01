"""
Vercel Serverless Function: POST /api/subscribe
Nimmt Name + E-Mail entgegen und legt den Kontakt bei deinem Newsletter-
Dienst an. Standardmäßig ist kein Dienst verbunden -> die Funktion nimmt die
Adresse an und antwortet ok (damit der Funnel out-of-the-box läuft).

So aktivierst du MailerLite (empfohlen, mit Double-Opt-in):
  1. Konto bei mailerlite.com anlegen, unter Integrations -> API einen Key erzeugen.
  2. (Optional) In MailerLite eine Gruppe anlegen und ihre ID kopieren.
  3. Double-Opt-in in MailerLite aktivieren:
       Settings -> Subscribe settings -> "Enable double opt-in".
  4. In Vercel unter Settings -> Environment Variables setzen:
       MAILERLITE_API_KEY  = dein_key
       MAILERLITE_GROUP_ID = 123456789   (optional)
  5. Redeploy. Ab dann landet jede Adresse in MailerLite und bekommt automatisch
     die Bestaetigungsmail (Double-Opt-in). Die Analyse wird trotzdem sofort gezeigt.

Alternativ Brevo (kostenloser Tarif):
       BREVO_API_KEY = dein_key
       BREVO_LIST_ID = 2   (optional)
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import secrets
import sys
import urllib.request

# Damit der Sibling-Import (_store) auf Vercel und lokal funktioniert.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from _store import kv_set
except Exception:  # noqa
    def kv_set(*a, **k):
        return False

# (redeploy-trigger, damit Vercel die MailerLite-Env-Variablen zieht)

# So lange gilt die Zuordnung Feedback-Token -> E-Mail (in der KV).
_FB_TOKEN_TTL = 120 * 24 * 3600


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


def _mailerlite(name, email, extra_fields=None):
    key = os.environ.get("MAILERLITE_API_KEY")
    if not key:
        return None  # nicht konfiguriert -> naechster Dienst
    payload = {"email": email}
    fields = {}
    if name:
        fields["name"] = name
    if extra_fields:
        fields.update(extra_fields)
    if fields:
        payload["fields"] = fields
    group_id = os.environ.get("MAILERLITE_GROUP_ID")
    if group_id:
        payload["groups"] = [str(group_id)]
    req = urllib.request.Request(
        "https://connect.mailerlite.com/api/subscribers",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json",
                 "Accept": "application/json"},
        method="POST")
    try:
        urllib.request.urlopen(req, timeout=10)
        return True, "Kontakt bei MailerLite angelegt"
    except urllib.error.HTTPError as e:
        # 200/201 kommen nicht hier an; 422 = bereits vorhanden/Validierung -> ok
        if e.code in (200, 201, 202, 409, 422):
            return True, "Kontakt bei MailerLite aktualisiert"
        return False, f"MailerLite-Fehler {e.code}"
    except Exception as e:  # noqa
        return False, str(e)


def _brevo(name, email):
    key = os.environ.get("BREVO_API_KEY")
    if not key:
        return False, "kein Dienst verbunden (Adresse nur angenommen)"
    payload = {"email": email, "updateEnabled": True,
               "attributes": {"VORNAME": name}}
    list_id = os.environ.get("BREVO_LIST_ID")
    if list_id:
        payload["listIds"] = [int(list_id)]
    req = urllib.request.Request(
        "https://api.brevo.com/v3/contacts",
        data=json.dumps(payload).encode("utf-8"),
        headers={"api-key": key, "Content-Type": "application/json"},
        method="POST")
    try:
        urllib.request.urlopen(req, timeout=10)
        return True, "Kontakt angelegt"
    except urllib.error.HTTPError as e:
        # 400 "duplicate" o.ä. ist für uns ok
        if e.code in (400, 204):
            return True, "Kontakt aktualisiert"
        return False, f"Brevo-Fehler {e.code}"
    except Exception as e:  # noqa
        return False, str(e)


def subscribe_contact(name, email, extra_fields=None):
    """Versucht zuerst MailerLite, dann Brevo. Ohne Konfiguration: nur annehmen."""
    res = _mailerlite(name, email, extra_fields)
    if res is not None:
        return res
    return _brevo(name, email)


class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        # Diagnose: sind die Env-Variablen bei der Funktion angekommen? (nur ja/nein)
        self._send(200, {
            "ok": True,
            "mailerlite_key_present": bool(os.environ.get("MAILERLITE_API_KEY")),
            "mailerlite_group_present": bool(os.environ.get("MAILERLITE_GROUP_ID")),
            "brevo_key_present": bool(os.environ.get("BREVO_API_KEY")),
        })

    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            email = (body.get("email") or "").strip()
            name = (body.get("name") or "").strip()
            if "@" not in email or "." not in email:
                return self._send(400, {"ok": False, "error": "Bitte gib eine gültige E-Mail an."})
            # Persoenlicher PDF-Parameter fuer die Willkommensmail (Feld bauplan_pdf).
            # Wir speichern NUR den base64url-Teil, nicht die ganze URL. In der Mail
            # steht dann eine vollstaendige, gueltige Adresse mit dem Tag am Ende:
            #   https://<domain>/api/pdf?d={$bauplan_pdf}
            # So erkennt MailerLite die URL sicher und ersetzt die Variable zuverlaessig.
            extra = {}
            d = (body.get("d") or "").strip()
            if d:
                extra["bauplan_pdf"] = d
            # Opaker Feedback-Token: Mapping in der KV, Token als MailerLite-Feld
            # (fuer den spaeteren Feedback-Link). Rein additiv, aendert den
            # bestehenden Ablauf nicht.
            tok = _feedback_token_for(email)
            if tok:
                extra["feedback_token"] = tok
            ok, msg = subscribe_contact(name, email, extra or None)
            self._send(200, {"ok": True, "stored": ok, "message": msg})
        except Exception as e:  # noqa
            self._send(500, {"ok": False, "error": str(e)})
