"""
Vercel Serverless Function: POST /api/analyze
Nimmt Geburtsdaten entgegen, berechnet Natalchart + Human Design exakt
und liefert Gratis-Einblick (teaser) + Voll-Analyse zurück.

Body (JSON):
  name       str
  date       "TT.MM.JJJJ"  (oder JJJJ-MM-TT)
  time       "HH:MM"       (optional -> time_known=false)
  place      str           (Anzeige / Fallback-Geocoding)
  lat, lon   float         (optional, vom Frontend-Autocomplete)
  tz         str           (IANA-Zone, optional, vom Frontend-Autocomplete)
"""
from http.server import BaseHTTPRequestHandler
import json

from _engine import compute_chart
from _interpret import teaser, full_analysis
from _geo import resolve_place, tz_for


def _parse_date(s):
    s = (s or "").strip()
    if "." in s:
        d, m, y = s.split(".")
    elif "-" in s:
        y, m, d = s.split("-")
    else:
        raise ValueError("Datum bitte als TT.MM.JJJJ angeben.")
    return int(y), int(m), int(d)


def _parse_time(s):
    s = (s or "").strip()
    if not s:
        return 12, 0, False          # unbekannt -> Mittag, ohne Häuser/Aszendent
    h, mi = s.replace(".", ":").split(":")[:2]
    return int(h), int(mi), True


def build_result(body):
    name = (body.get("name") or "").strip()
    year, month, day = _parse_date(body.get("date"))
    hour, minute, time_known = _parse_time(body.get("time"))

    lat = body.get("lat")
    lon = body.get("lon")
    tz = body.get("tz")
    place = (body.get("place") or "").strip()
    display = place

    if lat is not None and lon is not None:
        lat, lon = float(lat), float(lon)
        if not tz:
            tz = tz_for(lat, lon)
    else:
        resolved = resolve_place(place)
        if not resolved:
            raise ValueError(
                f"Den Geburtsort „{place}“ konnte ich nicht finden. "
                "Bitte wähle einen Vorschlag aus der Liste oder gib die nächstgrößere Stadt an.")
        lat, lon, tz, display = resolved

    chart = compute_chart(name, year, month, day, hour, minute, lat, lon, tz,
                          time_known=time_known)
    chart["place_display"] = display
    return {
        "ok": True,
        "birth": {"name": name, "date": body.get("date"),
                  "time": body.get("time") or "unbekannt", "place": display,
                  "lat": round(lat, 4), "lon": round(lon, 4), "tz": tz},
        "teaser": teaser(chart),
        "full": full_analysis(chart),
    }


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
        self._send(200, {"ok": True, "service": "Intuition mit Herz – Analyse-API"})

    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            self._send(200, build_result(body))
        except ValueError as e:
            self._send(400, {"ok": False, "error": str(e)})
        except Exception as e:  # noqa
            self._send(500, {"ok": False, "error": "Berechnung fehlgeschlagen.",
                             "detail": str(e)})
