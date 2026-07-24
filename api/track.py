"""
Vercel Serverless Function: POST /api/track   (auch GET /api/track?e=... moeglich)

Zaehlt anonym die Schritte im Funnel. Keine Cookies, keine Namen, keine
E-Mails, keine IP-Speicherung. Nur ein Zaehler pro Ereignis, plus ein Zaehler
pro Tag, damit die Statistik-Seite den Verlauf zeigen kann.

Erlaubte Ereignisse:
  visit    Seite geoeffnet
  himmel   Button "Meinen Himmel lesen" gedrueckt (Funnel-Start)
  teaser   Vorschau erreicht (nicht auf Seite 1 abgesprungen)
  email    E-Mail eingetragen (Lead)
  bauplan  kompletter Bauplan gesehen (Seite 3)
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import incr
except Exception:  # noqa
    def incr(keys):
        return

ALLOWED = {"visit", "himmel", "teaser", "email", "bauplan"}


def _count(event):
    if event not in ALLOWED:
        return
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    incr(["imh:t:" + event, "imh:d:" + day + ":" + event])


class handler(BaseHTTPRequestHandler):
    def _ok(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self):
        self._ok()

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        _count((qs.get("e") or [""])[0].strip())
        self._ok()

    def do_POST(self):
        event = ""
        try:
            length = int(self.headers.get("content-length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw or b"{}")
            event = (body.get("e") or body.get("event") or "").strip()
        except Exception:  # noqa
            event = ""
        _count(event)
        self._ok()
