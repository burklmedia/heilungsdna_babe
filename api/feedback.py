"""
Vercel Serverless Function: /api/feedback

POST  -> nimmt das Feedback zum Kosmischen Bauplan entgegen.
         Body (JSON): { "t": "<opaker Token>",
                        "helpfulness_score", "strongest_recognition",
                        "strongest_aha", "unclear_or_wrong",
                        "new_understanding", "unresolved_problem",
                        "improvement" }
         Ablauf:
           1. Token ueber die KV zur E-Mail aufloesen (imh:fbtok:<t>).
           2. Doppel-Absenden atomar sperren (imh:fbdone:<t>, SET NX).
           3. Genau EINEN Datensatz in der KV ablegen (Liste imh:feedback).
           4. In MailerLite feedback_given=yes setzen (Upsert per E-Mail).

GET ?pw=... -> geschuetzte Leseansicht aller Rueckmeldungen
               (Passwort aus STATS_PASSWORD, gleiches Muster wie /api/stats).

Kein neues Secret, keine neue Library, keine neue Datenbank:
nutzt die vorhandene KV (_store) und die vorhandene MailerLite-Anbindung
(subscribe). Der MailerLite-API-Key wird ausschliesslich serverseitig verwendet.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import (kv_get, kv_setnx, kv_del, push_feedback,
                        list_feedback, configured)
except Exception:  # noqa
    def kv_get(k):
        return None

    def kv_setnx(k, v, ttl=None):
        return True

    def kv_del(k):
        return True

    def push_feedback(r, key="imh:feedback"):
        return False

    def list_feedback(key="imh:feedback"):
        return []

    def configured():
        return False

try:
    from subscribe import subscribe_contact
except Exception:  # noqa
    def subscribe_contact(name, email, extra_fields=None):
        return False, "kein Dienst verbunden"

# Die sieben Felder in Anzeige-Reihenfolge.
FIELDS = [
    "helpfulness_score",
    "strongest_recognition",
    "strongest_aha",
    "unclear_or_wrong",
    "new_understanding",
    "unresolved_problem",
    "improvement",
]

LABELS = {
    "helpfulness_score": "Wie hilfreich (1-10)",
    "strongest_recognition": "Stärkste Wiedererkennung",
    "strongest_aha": "Größter Aha-Moment",
    "unclear_or_wrong": "Unklar oder unpassend",
    "new_understanding": "Neues Verständnis",
    "unresolved_problem": "Offen geblieben",
    "improvement": "Wunsch / Verbesserung",
}

DONE_TTL = 400 * 24 * 3600   # Doppel-Absende-Sperre laenger als das Token-Mapping


def _clip(value, n=4000):
    if value is None:
        return ""
    s = value if isinstance(value, str) else str(value)
    return s.strip()[:n]


def handle_feedback(body):
    """Kernlogik. Rueckgabe (http_code, payload_dict). Rein serverseitig,
    unabhaengig vom HTTP-Handler testbar."""
    token = _clip(body.get("t"), 128)
    if not token:
        return 400, {"ok": False, "error": "missing_token",
                     "message": "Dieser Link ist unvollständig. Bitte nutze den Link aus deiner E-Mail."}

    email = kv_get("imh:fbtok:" + token)
    if not email:
        return 404, {"ok": False, "error": "unknown_token",
                     "message": "Dieser Link ist nicht mehr gültig. Bitte nutze den aktuellen Link aus deiner E-Mail."}

    # Idempotenz: Sperre atomar setzen. Ist sie schon da -> keine Dublette.
    first_time = kv_setnx("imh:fbdone:" + token, "1", ttl=DONE_TTL)
    if not first_time:
        return 200, {"ok": True, "already": True,
                     "message": "Danke, dein Feedback ist schon bei mir angekommen. 🤍"}

    record = {"ts": datetime.now(timezone.utc).isoformat(), "email": email}
    for f in FIELDS:
        record[f] = _clip(body.get(f))

    if not push_feedback(record):
        # Speichern fehlgeschlagen -> Sperre wieder aufheben, damit ein erneuter
        # Versuch moeglich ist.
        kv_del("imh:fbdone:" + token)
        return 500, {"ok": False, "error": "store_failed",
                     "message": "Da ist gerade etwas schiefgelaufen. Bitte versuche es in einem Moment noch einmal."}

    # feedback_given=yes in MailerLite (best effort, blockiert das Speichern nicht).
    ml_ok = False
    try:
        ml_ok, _ = subscribe_contact("", email, {"feedback_given": "yes"})
    except Exception:  # noqa
        ml_ok = False

    return 200, {"ok": True, "stored": True, "mailerlite": bool(ml_ok),
                 "message": "Danke, dass du dir die Zeit genommen hast. 🤍"}


# ---------------------------------------------------------------------------
# Geschuetzte Leseansicht (gleiches Muster wie /api/stats)
# ---------------------------------------------------------------------------

PAGE_CSS = """
*{box-sizing:border-box} body{margin:0;background:#160e2e;color:#f3eefe;
font-family:-apple-system,Segoe UI,Roboto,sans-serif;padding:32px 20px}
.wrap{max-width:760px;margin:0 auto}
h1{font-weight:700;font-size:24px;margin:0 0 4px}
.sub{color:#b3a8d4;font-size:13px;margin:0 0 28px}
.fb{background:#241848;border:1px solid rgba(201,164,255,.18);border-radius:14px;
padding:16px 18px;margin-bottom:14px}
.fb .meta{font-size:11px;color:#8f83b3;margin-bottom:6px}
.fb .q{font-size:11px;color:#f5c56b;text-transform:uppercase;letter-spacing:.04em;margin:12px 0 2px}
.fb .a{font-size:14px;color:#e9e2fb;line-height:1.6;white-space:pre-wrap;margin:0}
.fb .score{color:#f5c56b;font-weight:700;font-size:16px}
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
            "<title>Feedback, Intuition mit Herz</title><style>" + PAGE_CSS +
            "</style></head><body><div class=wrap>" + body + "</div></body></html>")


def _login(msg=""):
    m = ("<div class=warn>" + msg + "</div>") if msg else ""
    return _page("<h1>Feedback</h1><p class=sub>Bitte Passwort eingeben.</p>" + m +
                 "<form method=get><input type=password name=pw placeholder=Passwort>"
                 "<button>Ansehen</button></form>")


def _esc(s):
    return (str(s if s is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _viewer():
    if not configured():
        return _page("<h1>Feedback</h1><div class=warn>Es ist noch kein "
                     "Datenspeicher verbunden.</div>")
    items = list_feedback()
    if not items:
        return _page("<h1>Feedback</h1><p class=sub>Noch keine Rückmeldungen.</p>")
    cards = ""
    for it in reversed(items):  # neueste zuerst
        ts = _esc(it.get("ts", ""))[:16].replace("T", " ")
        email = _esc(it.get("email", ""))
        rows = ""
        for f in FIELDS:
            val = it.get(f, "")
            if val is None or str(val).strip() == "":
                continue
            cls = "a score" if f == "helpfulness_score" else "a"
            rows += ("<div class=q>%s</div><p class='%s'>%s</p>"
                     % (_esc(LABELS.get(f, f)), cls, _esc(val)))
        cards += ("<div class=fb><div class=meta>%s &middot; %s</div>%s</div>"
                  % (ts, email, rows))
    return _page("<h1>Feedback</h1><p class=sub>%d Rückmeldungen, neueste zuerst.</p>%s"
                 % (len(items), cards))


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
                "<h1>Feedback</h1><div class=warn>Es ist noch kein Passwort "
                "gesetzt. Bitte in Vercel die Variable STATS_PASSWORD anlegen.</div>"))
        if pw != pw_env:
            return self._send_html(200 if not pw else 401,
                                   _login("Falsches Passwort." if pw else ""))
        self._send_html(200, _viewer())

    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            code, payload = handle_feedback(body)
            self._send_json(code, payload)
        except Exception as e:  # noqa
            self._send_json(500, {"ok": False, "error": "server_error",
                                  "message": "Da ist etwas schiefgelaufen.",
                                  "detail": str(e)})
