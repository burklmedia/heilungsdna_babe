"""
Vercel Serverless Function: POST /api/subscribe
Nimmt Name + E-Mail entgegen und legt den Kontakt bei deinem Newsletter-
Dienst an. Standardmäßig ist kein Dienst verbunden -> die Funktion nimmt die
Adresse an und antwortet ok (damit der Funnel out-of-the-box läuft).

So aktivierst du das echte Sammeln (Beispiel Brevo, kostenloser Tarif):
  1. Konto bei brevo.com anlegen, API-Key erzeugen
  2. In Vercel unter Settings -> Environment Variables setzen:
       BREVO_API_KEY = dein_key
       BREVO_LIST_ID = 2        (optional, ID deiner Kontaktliste)
  3. Redeploy – ab dann landen alle Adressen automatisch in Brevo.
Andere Dienste (MailerLite, Mailchimp) lassen sich analog anbinden.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request


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

    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            email = (body.get("email") or "").strip()
            name = (body.get("name") or "").strip()
            if "@" not in email or "." not in email:
                return self._send(400, {"ok": False, "error": "Bitte gib eine gültige E-Mail an."})
            ok, msg = _brevo(name, email)
            self._send(200, {"ok": True, "stored": ok, "message": msg})
        except Exception as e:  # noqa
            self._send(500, {"ok": False, "error": str(e)})
