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
  karte, siegeldreh, himmelpunkt   Vorschau: Karte aufgedeckt, Siegel umgedreht, Planet angetippt
  deckblatt, story, folgen, frage  Bericht: PDF über die Deckblatt-Karte, Story-Bild, Instagram, Frage an Denise
  zurueck                          Bericht ein weiteres Mal geöffnet (auf demselben Gerät)
  bestaetigt, kontakt              Bestätigungsseite geöffnet, Kontaktkarte geladen
  grusston, grussende              Videogruß im Pop-up: Ton eingeschaltet, bis zum Ende angesehen
  empfehlen                        Bericht: "Schenk ihn einer Freundin" angetippt
  hintergrund                      Bericht: Geburtshimmel als Handy-Hintergrund geladen
  warteliste, fragebox, vollendet  Bericht: Warteliste Liebesanalyse, Frage abgeschickt, alle Kapitel gelesen
  popup_insta                      Pop-up nach dem Eintragen: Instagram-Link angetippt
  app_start                        Bericht vom Startbildschirm aus geöffnet (als App)
  wrapped, wrapped_ende             Bauplan in 60 Sekunden: gestartet, bis zur letzten Karte gesehen
  hoeren                           Bericht: von Lea vorlesen lassen
  film_start, film_ton, film_ende, film_cta   Erklärfilm: angelaufen, mit Ton, zu Ende gesehen, Knopf darunter
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _herkunft import ist_intern  # noqa: E402

try:
    from _store import incr
except Exception:  # noqa
    def incr(keys):
        return

ALLOWED = {"visit", "himmel", "teaser", "email", "bauplan", "scroll", "pdf",
           # seit 10.10.2026 (Runde 8): Erlebnis-Elemente, je Sitzung höchstens einmal
           "karte", "siegeldreh", "himmelpunkt", "deckblatt", "story", "kontakt",
           "bestaetigt", "folgen", "frage", "zurueck",
           # seit 11.10.2026: Videogruß von Denise im Pop-up nach dem Eintragen
           "grusston", "grussende",
           # seit 11.10.2026: Bauplan an eine Freundin weiterempfohlen (Karte am Berichtsende)
           "empfehlen", "hintergrund", "warteliste", "fragebox", "vollendet", "popup_insta", "app_start", "wrapped", "wrapped_ende", "hoeren",
           # seit 11.10.2026: Erklärfilm auf der Startseite
           "film_start", "film_ton", "film_ende", "film_cta",
           # Aha-Momente in der Vorschau
           "spiegel_ja", "spiegel_nein", "spiegel_fertig", "du_und", "himmel_mit", "bestaetigt_insta"}


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
        # Eigene Geraete (Cookie imh_intern=1 nach /?intern=1) zaehlen nicht mit.
        if not ist_intern(self.headers.get("cookie")):
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
        if not ist_intern(self.headers.get("cookie")):
            _count(event)
        self._ok()
