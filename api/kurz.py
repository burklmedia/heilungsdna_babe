"""
Vercel Serverless Function: die Kurzlinks /story, /kommentar, /bio und /dm (seit 28.09.2026).

Zaehlt den Aufruf (ohne Bots und Link-Vorschauen) und leitet auf die Startseite mit ?q=<kanal> weiter.
Die Seite merkt sich den Kanal fuer die Sitzung und gibt ihn mit der Anmeldung zurueck (api/_herkunft.py).

GET /api/kurz?q=... mit dem Header "Authorization: Bearer <HERKUNFT_TOKEN>" liefert stattdessen alle
Ereignisse als JSON, fuer das Dashboard von Burkl Media. Ohne passendes Token: 404.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import hmac
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _herkunft import KURZLINKS, ereignisse, ist_bot, ist_intern, merken, schritte, schritte_tage, STICHTAG  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _antwort(self, code, daten=b"", typ="text/plain; charset=utf-8", ort=None):
        self.send_response(code)
        if ort:
            self.send_header("Location", ort)
        self.send_header("Content-Type", typ)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex")
        self.send_header("Content-Length", str(len(daten)))
        self.end_headers()
        self.wfile.write(daten)

    def do_GET(self):
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        # Das Dashboard holt die Ereignisse mit Token; ohne Token gibt es diese Antwort nicht.
        if (qs.get("ereignisse") or [""])[0] == "1":
            soll = os.environ.get("HERKUNFT_TOKEN", "").strip()
            ist = (self.headers.get("authorization") or "").removeprefix("Bearer ").strip()
            if not soll or not hmac.compare_digest(soll, ist):
                return self._antwort(404, b"nicht gefunden")
            daten = json.dumps({"ereignisse": ereignisse(), "schritte": schritte(), "stichtag": STICHTAG,
                                "tage": schritte_tage()}, ensure_ascii=False).encode("utf-8")
            return self._antwort(200, daten, "application/json; charset=utf-8")
        k = (qs.get("k") or [""])[0]
        if k not in KURZLINKS:
            k = url.path.strip("/").split("/")[-1]
        if k not in KURZLINKS:
            return self._antwort(302, ort="/")
        if not ist_bot(self.headers.get("user-agent", "")) and not ist_intern(self.headers.get("cookie")):
            merken("klick", k)
        self._antwort(302, ort="/?q=" + k)

    def do_HEAD(self):
        # Link-Vorschauen fragen oft nur den Kopf ab; das zaehlt nie.
        self._antwort(302, ort="/")
