"""
Vercel Serverless Function: /api/topic

POST  -> nimmt die Themenauswahl zum Kosmischen Bauplan entgegen.
         Body (JSON): { "t": "<opaker feedback_token>",
                        "topic": "relationship|decision|boundaries|energy|none" }
         Ablauf (MailerLite-Write ist verpflichtend):
           1. Token validieren (vorhanden + loest in der KV zu einer E-Mail auf).
           2. topic gegen Whitelist validieren.
           3. imh:topicdone:<token> atomar per SET NX reservieren (Doppel-Submit).
           4. beta_topic beim MailerLite-Subscriber setzen (Upsert per E-Mail).
           5. Erfolg -> aggregierte KV-Zaehler erhoehen, Erfolg zurueckgeben.
              Fehler -> imh:topicdone:<token> wieder loeschen, freundlicher Retry-Fehler.
         feedback_given wird NIEMALS veraendert.

GET ?pw=... -> geschuetzte Auswertung (Themen-Verteilung), Passwort STATS_PASSWORD.

Wiederverwendung: derselbe opake feedback_token und dieselbe Token->E-Mail-Zuordnung
in der KV (imh:fbtok:<token>) wie beim Feedback. Keine neue Token-Logik, keine neue
Library, keine neue Datenbank.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import kv_get, kv_setnx, kv_del, incr, mget, configured
except Exception:  # noqa
    def kv_get(k):
        return None

    def kv_setnx(k, v, ttl=None):
        return True

    def kv_del(k):
        return True

    def incr(keys):
        pass

    def mget(keys):
        return [0] * len(keys)

    def configured():
        return False

try:
    from subscribe import subscribe_contact
except Exception:  # noqa
    def subscribe_contact(name, email, extra_fields=None):
        return False, "kein Dienst verbunden"

# Erlaubte Themenwerte (Whitelist) und Anzeige-Labels fuer die Auswertung.
TOPICS = ["relationship", "decision", "boundaries", "energy", "none"]
TOPIC_LABELS = {
    "relationship": "Beziehung & Selbstverlust",
    "decision": "Entscheidungen & Overthinking",
    "boundaries": "Grenzen & People Pleasing",
    "energy": "Energie & Überforderung",
    "none": "Aktuell keines davon",
}

DONE_TTL = 400 * 24 * 3600   # Doppel-Absende-Sperre


def _clip(value, n=128):
    if value is None:
        return ""
    s = value if isinstance(value, str) else str(value)
    return s.strip()[:n]


def handle_topic(body):
    """Kernlogik. Rueckgabe (http_code, payload_dict). Unabhaengig vom HTTP-Handler
    testbar."""
    # 1. Token validieren (vorhanden + loest zu einer E-Mail auf)
    token = _clip(body.get("t"), 128)
    if not token:
        return 400, {"ok": False, "error": "missing_token",
                     "message": "Dieser Link ist unvollständig. Bitte nutze den Link aus deiner E-Mail."}
    email = kv_get("imh:fbtok:" + token)
    if not email:
        return 404, {"ok": False, "error": "unknown_token",
                     "message": "Dieser Link ist nicht mehr gültig. Bitte nutze den aktuellen Link aus deiner E-Mail."}

    # 2. topic gegen Whitelist validieren
    topic = _clip(body.get("topic"), 32)
    if topic not in TOPICS:
        return 400, {"ok": False, "error": "invalid_topic",
                     "message": "Bitte wähle eine der Optionen aus."}

    # 3. Doppel-Submit atomar reservieren
    first_time = kv_setnx("imh:topicdone:" + token, topic, ttl=DONE_TTL)
    if not first_time:
        return 200, {"ok": True, "already": True,
                     "message": "Danke, deine Auswahl ist schon bei mir angekommen. 🤍"}

    # 4. beta_topic in MailerLite setzen (Upsert per E-Mail). MUSS erfolgreich sein.
    ml_ok = False
    try:
        ml_ok, _ = subscribe_contact("", email, {"beta_topic": topic})
    except Exception:  # noqa
        ml_ok = False

    if not ml_ok:
        # 6. Sperre wieder freigeben -> Nutzer kann erneut absenden, nichts geht verloren.
        kv_del("imh:topicdone:" + token)
        return 503, {"ok": False, "error": "mailerlite_failed",
                     "message": "Da ist gerade etwas schiefgelaufen. Bitte versuche es in einem Moment noch einmal."}

    # 5. Erst nach erfolgreichem MailerLite-Write aggregiert zaehlen (keine PII).
    try:
        day = datetime.now(timezone.utc).date().isoformat()
        incr(["imh:t:topic:" + topic, "imh:d:" + day + ":topic:" + topic])
    except Exception:  # noqa
        pass

    return 200, {"ok": True, "stored": True,
                 "message": "Danke für deine Antwort. 🤍"}


# ---------------------------------------------------------------------------
# Geschuetzte Auswertung (gleiches Muster wie /api/stats und /api/feedback)
# ---------------------------------------------------------------------------

PAGE_CSS = """
*{box-sizing:border-box} body{margin:0;background:#160e2e;color:#f3eefe;
font-family:-apple-system,Segoe UI,Roboto,sans-serif;padding:32px 20px}
.wrap{max-width:640px;margin:0 auto}
h1{font-weight:700;font-size:24px;margin:0 0 4px}
.sub{color:#b3a8d4;font-size:13px;margin:0 0 28px}
.row{background:#241848;border:1px solid rgba(201,164,255,.18);border-radius:14px;
padding:14px 18px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;
gap:14px;position:relative;overflow:hidden}
.row .bar{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,
rgba(245,197,107,.22),rgba(245,197,107,.06));border-radius:14px}
.lbl{position:relative;font-size:14px;color:#e9e2fb}
.rgt{position:relative;text-align:right}
.num{font-size:22px;font-weight:700;color:#f5c56b;line-height:1}
.pct{font-size:11px;color:#b3a8d4;margin-top:3px}
.warn{background:#3a1d2a;border:1px solid #f0a6b2;border-radius:12px;padding:16px 18px;
color:#f0a6b2;margin-bottom:24px;font-size:13.5px;line-height:1.6}
form input{padding:12px 14px;border-radius:10px;border:1px solid #43356e;
background:#241848;color:#fff;font-size:15px;width:220px}
form button{margin-left:8px;padding:12px 20px;border:0;border-radius:10px;
background:#f5c56b;color:#3a2410;font-weight:700;font-size:15px;cursor:pointer}
"""


def _page(body):
    return ("<!doctype html><html lang=de><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<meta name=robots content=noindex>"
            "<title>Themen, Intuition mit Herz</title><style>" + PAGE_CSS +
            "</style></head><body><div class=wrap>" + body + "</div></body></html>")


def _login(msg=""):
    m = ("<div class=warn>" + msg + "</div>") if msg else ""
    return _page("<h1>Themenauswahl</h1><p class=sub>Bitte Passwort eingeben.</p>" + m +
                 "<form method=get><input type=password name=pw placeholder=Passwort>"
                 "<button>Ansehen</button></form>")


def _viewer():
    if not configured():
        return _page("<h1>Themenauswahl</h1><div class=warn>Es ist noch kein "
                     "Datenspeicher verbunden.</div>")
    vals = mget(["imh:t:topic:" + t for t in TOPICS])
    total = sum(vals) or 0
    rows = ""
    for t, v in zip(TOPICS, vals):
        pct = (100.0 * v / total) if total else 0
        rows += ("<div class=row><div class=bar style='width:%.1f%%'></div>"
                 "<div class=lbl>%s</div><div class=rgt><div class=num>%d</div>"
                 "<div class=pct>%.0f%%</div></div></div>"
                 % (pct, TOPIC_LABELS[t], v, pct))
    return _page("<h1>Themenauswahl</h1>"
                 "<p class=sub>%d Antworten gesamt. Die Zuordnung pro Person steht als "
                 "Feld beta_topic in MailerLite.</p>%s" % (total, rows))


class handler(BaseHTTPRequestHandler):
    def _send_json(self, code, payload):
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

    def _send_html(self, code, html):
        data = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_GET(self):
        pw_env = os.environ.get("STATS_PASSWORD")
        pw = (parse_qs(urlparse(self.path).query).get("pw") or [""])[0]
        if not pw_env:
            return self._send_html(200, _page(
                "<h1>Themenauswahl</h1><div class=warn>Es ist noch kein Passwort "
                "gesetzt. Bitte in Vercel die Variable STATS_PASSWORD anlegen.</div>"))
        if pw != pw_env:
            return self._send_html(200 if not pw else 401,
                                   _login("Falsches Passwort." if pw else ""))
        self._send_html(200, _viewer())

    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            code, payload = handle_topic(body)
            self._send_json(code, payload)
        except Exception as e:  # noqa
            self._send_json(500, {"ok": False, "error": "server_error",
                                  "message": "Da ist etwas schiefgelaufen.",
                                  "detail": str(e)})
