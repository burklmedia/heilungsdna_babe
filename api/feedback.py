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
           4. In ActiveCampaign "Feedback gegeben" = yes setzen, nur beim
              bestehenden Kontakt (api/_ac.py). Die Automation laesst damit
              die Feedback-Erinnerung aus.

POST mit "art" (seit 29.10.2026, Feedback direkt im Bauplan, public/rueckmeldung.js):
  {"art": "kapitel", "thema": "hd|na|in|nu|de", "wert": "ja|teils|nein", "sek": <Lesezeit im Thema>,
   "text": "...", "nur_text": true, "t": "<Token, optional>", "profil": {...}}
      Zaehlt die Antwort auf „Erkennst du dich hier wieder?“ (imh:kap:<thema>:<wert>), eine
      Anmerkung zu „Eher nicht“ landet in der Liste imh:kapitel. Erst ab KAPITEL_MIN_SEK im Thema.
  {"art": "bauplan", "antworten": {...}, "kapitel": {...}, "lesen": {"sek", "themen", "geoeffnet"},
   "profil": {...}, "t": "<Token, optional>"}
      Der Fragebogen. Wird nur angenommen, wenn der Bauplan gelesen ist (LESEZEIT_MIN_SEK aktive
      Lesezeit, THEMEN_MIN Themen). Mit Token wird die E-Mail zugeordnet und in ActiveCampaign
      "Feedback gegeben" = yes gesetzt, damit Mail 3 nicht mehr nach Feedback fragt. Ohne Token
      bleibt die Rueckmeldung ohne Namen und E-Mail. Liste imh:rueckmeldung, Telegram nur Kurzmeldung.

GET ?pw=... -> geschuetzte Leseansicht aller Rueckmeldungen
               (Passwort aus STATS_PASSWORD, gleiches Muster wie /api/stats).

Keine neue Library, keine neue Datenbank: nutzt die vorhandene KV (_store).
Der ActiveCampaign-API-Key wird ausschliesslich serverseitig verwendet.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import (kv_get, kv_setnx, kv_del, kv_incr_ttl, incr, mget,
                        push_feedback, list_feedback, configured)
except Exception:  # noqa
    def kv_get(k):
        return None

    def kv_setnx(k, v, ttl=None):
        return True

    def kv_del(k):
        return True

    def kv_incr_ttl(k, ttl):
        return None

    def incr(keys):
        return None

    def mget(keys):
        return [None] * len(keys)

    def push_feedback(r, key="imh:feedback"):
        return False

    def list_feedback(key="imh:feedback"):
        return []

    def configured():
        return False

try:
    from _ac import update_contact
except Exception:  # noqa
    def update_contact(email, fields):
        return False, "kein Dienst verbunden"

try:
    import _telegram as telegram
except Exception:  # noqa
    telegram = None

try:
    from _herkunft import ist_intern
except Exception:  # noqa
    def ist_intern(cookie_header):
        return False

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

    # feedback_given=yes beim Kontakt (best effort, blockiert das Speichern nicht).
    crm_ok = False
    try:
        crm_ok, _ = update_contact(email, {"feedback_given": "yes"})
    except Exception:  # noqa
        crm_ok = False

    return 200, {"ok": True, "stored": True, "crm": bool(crm_ok),
                 "message": "Danke, dass du dir die Zeit genommen hast. 🤍"}


# ---------------------------------------------------------------------------
# Feedback direkt im Bauplan (seit 29.10.2026, public/rueckmeldung.js)
# ---------------------------------------------------------------------------

# Leicht unter den Werten im Browser (300 s, 3 Themen), damit Uhren-Ungenauigkeit nicht stoert.
LESEZEIT_MIN_SEK = 240
THEMEN_MIN = 3
KAPITEL_MIN_SEK = 15
THEMEN = {"hd": "Human Design", "na": "Natalchart", "in": "Intuitionstyp", "nu": "Numerologie", "de": "Deutung"}
KAPITEL_WERTE = ("ja", "teils", "nein")
LIMIT_PRO_STUNDE = 30
_TOKEN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

# Erlaubte Antworten je Frage (gleich wie SCHRITTE in rueckmeldung.js)
BERUEHRT = ["Human Design", "Natalchart", "Intuitionstyp", "Numerologie", "Deutung", "Deine größte Stärke",
            "Deine Schwierigkeiten", "Der Brief zu deinem Sternzeichen"]
VERSTAENDLICH = ["Klar und leicht", "Manches musste ich zweimal lesen", "Oft zu kompliziert für mich"]
HILFE = ["Ein persönliches Gespräch über meinen Bauplan", "Eine Analyse für mich und einen Menschen, der mir nah ist",
         "Ein Blick auf mein kommendes Jahr", "Kleine Übungen, um meinem Bauchgefühl im Alltag zu folgen",
         "Erst mal nichts, ich lasse ihn wirken"]

_ZU_FRUEH = {"ok": False, "error": "zu_frueh",
             "message": "Nimm dir erst Zeit für deinen Bauplan. Danach freue ich mich sehr über deine Rückmeldung."}


def _begrenzt(ip, art):
    h = hashlib.sha256(("imh-feedback|" + (ip or "")).encode("utf-8")).hexdigest()[:20]
    n = kv_incr_ttl("imh:rl:%s:%s" % (art, h), 3600)
    return isinstance(n, int) and n > LIMIT_PRO_STUNDE


def _zahl(x, lo, hi):
    try:
        v = int(x)
    except (TypeError, ValueError):
        return None
    return v if lo <= v <= hi else None


def _auswahl(werte, erlaubt):
    if not isinstance(werte, list):
        return []
    return [w for w in erlaubt if w in werte]


def _profil(p):
    p = p if isinstance(p, dict) else {}
    return {k: _clip(p.get(k), 60) for k in ("typ", "autoritaet", "profil", "intuition", "sonne", "lebenszahl")}


def _email_aus_token(body):
    t = body.get("t") if isinstance(body.get("t"), str) else ""
    t = t.strip()
    if not _TOKEN.match(t):
        return "", ""
    return (kv_get("imh:fbtok:" + t) or ""), t


def _melden(text, intern):
    if intern or telegram is None:
        return
    try:
        telegram.melden(text)
    except Exception:  # noqa
        pass


def handle_kapitel(body, ip="", intern=False):
    """Antwort auf „Erkennst du dich hier wieder?“ am Ende eines Themas."""
    thema = body.get("thema") if body.get("thema") in THEMEN else ""
    wert = body.get("wert") if body.get("wert") in KAPITEL_WERTE else ""
    if not thema or not wert:
        return 400, {"ok": False, "error": "bad_request"}
    sek = _zahl(body.get("sek"), 0, 10 ** 6) or 0
    if sek < KAPITEL_MIN_SEK:
        return 403, dict(_ZU_FRUEH)
    if _begrenzt(ip, "kapitel"):
        return 429, {"ok": False, "error": "rate_limited"}
    text = re.sub(r"\s+", " ", _clip(body.get("text"), 600)).strip()
    if not body.get("nur_text") and not intern:
        incr(["imh:kap:%s:%s" % (thema, wert)])
    if text:
        email, _ = _email_aus_token(body)
        push_feedback({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "thema": thema, "wert": wert,
                       "text": text, "email": email, "profil": _profil(body.get("profil")), "intern": bool(intern)},
                      key="imh:kapitel")
    return 200, {"ok": True}


def handle_rueckmeldung(body, ip="", intern=False):
    """Der Fragebogen aus dem Fenster. Nur, wenn der Bauplan gelesen ist."""
    lesen = body.get("lesen") if isinstance(body.get("lesen"), dict) else {}
    sek = _zahl(lesen.get("sek"), 0, 10 ** 7) or 0
    themen = [t for t in (lesen.get("themen") or []) if t in THEMEN] if isinstance(lesen.get("themen"), list) else []
    if sek < LESEZEIT_MIN_SEK or len(themen) < THEMEN_MIN:
        return 403, dict(_ZU_FRUEH)
    if _begrenzt(ip, "rueckmeldung"):
        return 429, {"ok": False, "error": "rate_limited",
                     "message": "Das war gerade etwas viel. Bitte versuch es später noch einmal."}

    a = body.get("antworten") if isinstance(body.get("antworten"), dict) else {}
    antworten = {
        "wiedererkannt": _zahl(a.get("wiedererkannt"), 1, 5),
        "beruehrt": _auswahl(a.get("beruehrt"), BERUEHRT),
        "verstaendlich": a.get("verstaendlich") if a.get("verstaendlich") in VERSTAENDLICH else "",
        "aha": _clip(a.get("aha"), 1000),
        "hilfe": _auswahl(a.get("hilfe"), HILFE),
        "hilfe_anderes": _clip(a.get("hilfe_anderes"), 200),
        "empfehlen": _zahl(a.get("empfehlen"), 0, 10),
        "empfehlen_fehlt": _clip(a.get("empfehlen_fehlt"), 800),
        "stimme_text": _clip(a.get("stimme_text"), 1200),
        "stimme_ok": bool(a.get("stimme_ok")) and bool(_clip(a.get("stimme_text"), 10)),
    }
    if antworten["wiedererkannt"] is None:
        return 400, {"ok": False, "error": "missing_answer",
                     "message": "Tipp bitte noch an, wie sehr du dich wiedererkannt hast."}
    # Den Vornamen gibt es nur zusammen mit der Freigabe der eigenen Worte
    antworten["vorname"] = _clip(a.get("vorname"), 40) if antworten["stimme_ok"] else ""

    email, token = _email_aus_token(body)
    if token and email and not kv_setnx("imh:rmdone:" + token, "1", ttl=DONE_TTL):
        return 200, {"ok": True, "already": True}

    kapitel = body.get("kapitel") if isinstance(body.get("kapitel"), dict) else {}
    record = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "art": "bauplan", "email": email,
              "antworten": antworten, "kapitel": {k: kapitel.get(k) for k in THEMEN if kapitel.get(k) in KAPITEL_WERTE},
              "lesen": {"sek": sek, "themen": themen, "geoeffnet": _zahl(lesen.get("geoeffnet"), 0, 100) or 0},
              "profil": _profil(body.get("profil")), "intern": bool(intern)}
    if not push_feedback(record, key="imh:rueckmeldung"):
        if token and email:
            kv_del("imh:rmdone:" + token)
        return 500, {"ok": False, "error": "store_failed",
                     "message": "Da ist gerade etwas schiefgelaufen. Bitte versuche es in einem Moment noch einmal."}

    if email:
        try:
            update_contact(email, {"feedback_given": "yes"})
        except Exception:  # noqa
            pass
    teile = ["Wiedererkannt %d von 5" % antworten["wiedererkannt"]]
    if antworten["empfehlen"] is not None:
        teile.append("Freundin %d von 10" % antworten["empfehlen"])
    if antworten["stimme_ok"]:
        teile.append("mit freigegebener Stimme")
    _melden("Neues Feedback zum Bauplan ✦ " + " · ".join(teile) + ". Lesen unter /api/feedback", intern)
    return 200, {"ok": True, "stored": True}


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
h2{font-size:17px;margin:34px 0 10px;color:#f5c56b}
table.kap{width:100%;border-collapse:collapse;margin-bottom:8px;font-size:14px}
table.kap th,table.kap td{padding:9px 10px;border-bottom:1px solid rgba(201,164,255,.18);text-align:left}
table.kap th{font-size:11px;color:#8f83b3;text-transform:uppercase;letter-spacing:.04em;font-weight:600}
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


R_LABELS = [
    ("beruehrt", "Am meisten berührt"), ("verstaendlich", "Wie leicht zu lesen"), ("aha", "Satz zum Innehalten"),
    ("hilfe", "Was jetzt helfen würde"), ("hilfe_anderes", "Etwas anderes"), ("empfehlen_fehlt", "Was zum Weitergeben fehlte"),
    ("stimme_text", "Wie es beim Lesen war"),
]


def _bauplan_teil():
    """Neue Rückmeldungen aus dem Bauplan: Kapitel-Zähler, Fragebögen, Anmerkungen."""
    werte = mget(["imh:kap:%s:%s" % (t, w) for t in THEMEN for w in KAPITEL_WERTE])
    zeilen, i = "", 0
    for t, name in THEMEN.items():
        ja, teils, nein = werte[i:i + 3]
        i += 3
        zeilen += "<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>" % (_esc(name), ja, teils, nein)
    html = ("<h2>Erkennst du dich hier wieder?</h2><table class=kap><tr><th>Thema</th><th>Ja, total</th>"
            "<th>Teils</th><th>Eher nicht</th></tr>" + zeilen + "</table>")

    items = [x for x in list_feedback("imh:rueckmeldung") if not x.get("intern")]
    html += "<h2>Fragebogen im Bauplan</h2><p class=sub>%d Rückmeldungen, neueste zuerst. Interne Tests ausgeblendet.</p>" % len(items)
    for it in reversed(items):
        a = it.get("antworten") or {}
        p = it.get("profil") or {}
        le = it.get("lesen") or {}
        meta = "%s · %s · %d Min. gelesen · %s, %s, %s" % (
            _esc(it.get("ts", ""))[:16].replace("T", " "), _esc(it.get("email") or "ohne E-Mail"), int(le.get("sek") or 0) // 60,
            _esc(p.get("typ")), _esc(p.get("intuition")), _esc(p.get("sonne")))
        kopf = "<span class=score>%s</span>" % ("★" * int(a.get("wiedererkannt") or 0))
        if a.get("empfehlen") is not None:
            kopf += " &nbsp;·&nbsp; Freundin %s/10" % _esc(a.get("empfehlen"))
        rows = ""
        for k, label in R_LABELS:
            v = a.get(k)
            if isinstance(v, list):
                v = ", ".join(v)
            if v:
                rows += "<div class=q>%s</div><p class=a>%s</p>" % (_esc(label), _esc(v))
        if a.get("stimme_ok"):
            rows += "<div class=q>Freigabe</div><p class=a>Darf mit Vornamen gezeigt werden: <b>%s</b></p>" % _esc(a.get("vorname"))
        kap = it.get("kapitel") or {}
        if kap:
            rows += "<div class=q>Kapitel</div><p class=a>%s</p>" % _esc(", ".join("%s: %s" % (THEMEN.get(k, k), v) for k, v in kap.items()))
        html += "<div class=fb><div class=meta>%s</div><p class=a>%s</p>%s</div>" % (meta, kopf, rows)

    notizen = [x for x in list_feedback("imh:kapitel") if not x.get("intern")]
    if notizen:
        html += "<h2>Was in einem Thema nicht gepasst hat</h2>"
        for it in reversed(notizen):
            html += "<div class=fb><div class=meta>%s · %s · %s</div><p class=a>%s</p></div>" % (
                _esc(it.get("ts", ""))[:16].replace("T", " "), _esc(THEMEN.get(it.get("thema"), it.get("thema"))),
                _esc(it.get("email") or "ohne E-Mail"), _esc(it.get("text")))
    return html


def _viewer():
    if not configured():
        return _page("<h1>Feedback</h1><div class=warn>Es ist noch kein "
                     "Datenspeicher verbunden.</div>")
    neu = _bauplan_teil()
    items = list_feedback()
    if not items:
        return _page("<h1>Feedback</h1>" + neu + "<h2>Feedback aus Mail 3</h2><p class=sub>Noch keine Rückmeldungen.</p>")
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
    return _page("<h1>Feedback</h1>%s<h2>Feedback aus Mail 3</h2><p class=sub>%d Rückmeldungen, neueste zuerst.</p>%s"
                 % (neu, len(items), cards))


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
            if not isinstance(body, dict):
                body = {}
            ip = (self.headers.get("x-forwarded-for") or "").split(",")[0].strip()
            intern = ist_intern(self.headers.get("cookie"))
            if body.get("art") == "kapitel":
                code, payload = handle_kapitel(body, ip, intern)
            elif body.get("art") == "bauplan":
                code, payload = handle_rueckmeldung(body, ip, intern)
            else:
                code, payload = handle_feedback(body)
            self._send_json(code, payload)
        except Exception as e:  # noqa
            self._send_json(500, {"ok": False, "error": "server_error",
                                  "message": "Da ist etwas schiefgelaufen.",
                                  "detail": str(e)})
