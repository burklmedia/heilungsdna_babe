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
import urllib.request

# (redeploy-trigger, damit Vercel die MailerLite-Env-Variablen zieht)


def _mailerlite(name, email):
    key = os.environ.get("MAILERLITE_API_KEY")
    if not key:
        return None  # nicht konfiguriert -> naechster Dienst
    payload = {"email": email}
    if name:
        payload["fields"] = {"name": name}
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


def subscribe_contact(name, email):
    """Versucht zuerst MailerLite, dann Brevo. Ohne Konfiguration: nur annehmen."""
    res = _mailerlite(name, email)
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
            ok, msg = subscribe_contact(name, email)
            self._send(200, {"ok": True, "stored": ok, "message": msg})
        except Exception as e:  # noqa
            self._send(500, {"ok": False, "error": str(e)})
