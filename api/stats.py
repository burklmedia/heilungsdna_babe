"""
Vercel Serverless Function: GET /api/stats?pw=DEIN_PASSWORT

Zeigt die eigene Besucher-Statistik als einfache, geschuetzte Seite.
Passwort kommt aus der Umgebungsvariable STATS_PASSWORD.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone, timedelta
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import mget, configured, diag_names
except Exception:  # noqa
    def mget(keys):
        return [0] * len(keys)

    def configured():
        return False

    def diag_names():
        return {"gefundene_namen": [], "url_erkannt": False, "token_erkannt": False}

STEPS = [
    ("visit", "Besucher"),
    ("himmel", "„Meinen Himmel“ geklickt"),
    ("teaser", "Vorschau erreicht"),
    ("email", "E-Mail eingetragen"),
    ("bauplan", "Bauplan gesehen"),
]

PAGE_CSS = """
*{box-sizing:border-box} body{margin:0;background:#160e2e;color:#f3eefe;
font-family:-apple-system,Segoe UI,Roboto,sans-serif;padding:32px 20px}
.wrap{max-width:820px;margin:0 auto}
h1{font-weight:700;font-size:24px;margin:0 0 4px}
.sub{color:#b3a8d4;font-size:13px;margin:0 0 28px}
.funnel{display:flex;flex-direction:column;gap:10px;margin-bottom:34px}
.row{background:#241848;border:1px solid rgba(201,164,255,.18);border-radius:14px;
padding:16px 18px;display:flex;align-items:center;justify-content:space-between;gap:14px}
.row .bar{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,
rgba(245,197,107,.22),rgba(245,197,107,.06));border-radius:14px}
.row{position:relative;overflow:hidden}
.lbl{position:relative;font-size:14px;color:#e9e2fb}
.rgt{position:relative;text-align:right}
.num{font-size:22px;font-weight:700;color:#f5c56b;line-height:1}
.pct{font-size:11px;color:#b3a8d4;margin-top:3px}
table{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:8px}
th,td{padding:8px 6px;text-align:right;border-bottom:1px solid rgba(201,164,255,.12)}
th:first-child,td:first-child{text-align:left;color:#b3a8d4}
th{color:#8f83b3;font-weight:600;font-size:11px}
.note{margin-top:26px;color:#8f83b3;font-size:12px;line-height:1.6}
.warn{background:#3a1d2a;border:1px solid #f0a6b2;border-radius:12px;padding:16px 18px;
color:#f0a6b2;margin-bottom:24px;font-size:13.5px;line-height:1.6}
a{color:#f5c56b}
"""


def _html(body):
    return ("<!doctype html><html lang=de><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Statistik, Intuition mit Herz</title><style>" + PAGE_CSS +
            "</style></head><body><div class=wrap>" + body + "</div></body></html>")


def _login(msg=""):
    m = ("<div class=warn>" + msg + "</div>") if msg else ""
    return _html(
        "<h1>Statistik</h1><p class=sub>Bitte Passwort eingeben.</p>" + m +
        "<form method=get>"
        "<input type=password name=pw placeholder=Passwort "
        "style='padding:12px 14px;border-radius:10px;border:1px solid #43356e;"
        "background:#241848;color:#fff;font-size:15px;width:220px'>"
        "<button style='margin-left:8px;padding:12px 20px;border:0;border-radius:10px;"
        "background:#f5c56b;color:#3a2410;font-weight:700;font-size:15px;cursor:pointer'>"
        "Ansehen</button></form>")


def _dashboard():
    if not configured():
        return _html(
            "<h1>Statistik</h1>"
            "<div class=warn>Es ist noch kein Datenspeicher verbunden. "
            "Sobald in Vercel der kostenlose Speicher (Upstash bzw. Vercel KV) "
            "aktiv ist, erscheinen hier die Zahlen.</div>")

    total_keys = ["imh:t:" + e for e, _ in STEPS]
    totals = mget(total_keys)
    base = totals[0] or 0

    rows = ""
    prev = None
    for (ev, label), val in zip(STEPS, totals):
        of_visit = (100.0 * val / base) if base else 0
        step = ""
        if prev is not None and prev > 0:
            step = " · " + ("%.0f" % (100.0 * val / prev)) + "% vom Schritt davor"
        width = min(100.0, of_visit if base else 0)
        rows += (
            "<div class=row><div class=bar style='width:%.1f%%'></div>"
            "<div class=lbl>%s</div><div class=rgt>"
            "<div class=num>%d</div><div class=pct>%.0f%% der Besucher%s</div>"
            "</div></div>" % (width, label, val, of_visit, step))
        prev = val

    # letzte 14 Tage
    days = [(datetime.now(timezone.utc).date() - timedelta(days=i)) for i in range(13, -1, -1)]
    day_keys = []
    for d in days:
        for ev, _ in STEPS:
            day_keys.append("imh:d:" + d.isoformat() + ":" + ev)
    dvals = mget(day_keys)
    thead = "<tr><th>Tag</th>" + "".join("<th>%s</th>" % lbl for _, lbl in STEPS) + "</tr>"
    trows = ""
    for i, d in enumerate(days):
        cells = dvals[i * len(STEPS):(i + 1) * len(STEPS)]
        if not any(cells):
            continue
        trows += ("<tr><td>%s</td>" % d.strftime("%d.%m.") +
                  "".join("<td>%d</td>" % c for c in cells) + "</tr>")
    if not trows:
        trows = "<tr><td colspan=%d style='color:#8f83b3'>Noch keine Daten.</td></tr>" % (len(STEPS) + 1)

    return _html(
        "<h1>Deine Statistik</h1>"
        "<p class=sub>Eigenes Tracking, cookiefrei, ohne Namen. Live aus deinem Funnel.</p>"
        "<div class=funnel>" + rows + "</div>"
        "<h1 style='font-size:16px'>Letzte 14 Tage</h1>"
        "<table>" + thead + trows + "</table>"
        "<p class=note>Die Zahlen zaehlen Sitzungen: jedes Ereignis wird pro "
        "Browser-Sitzung nur einmal gezaehlt. „Vorschau erreicht“ heisst, jemand "
        "ist von Seite 1 weitergekommen. Namen siehst du bewusst nicht hier, die "
        "echten Kontakte stehen in MailerLite.</p>")


class handler(BaseHTTPRequestHandler):
    def _send(self, code, html):
        data = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        pw_env = os.environ.get("STATS_PASSWORD")
        pw = (parse_qs(urlparse(self.path).query).get("pw") or [""])[0]
        if not pw_env:
            return self._send(200, _html(
                "<h1>Statistik</h1><div class=warn>Es ist noch kein Passwort gesetzt. "
                "Bitte in Vercel die Variable STATS_PASSWORD anlegen.</div>"))
        if pw != pw_env:
            return self._send(200 if not pw else 401,
                              _login("Falsches Passwort." if pw else ""))
        if (parse_qs(urlparse(self.path).query).get("diag") or [""])[0]:
            d = diag_names()
            names = "".join("<li>" + n + "</li>" for n in d["gefundene_namen"]) or "<li>(keine gefunden)</li>"
            return self._send(200, _html(
                "<h1>Diagnose Speicher</h1>"
                "<p class=sub>Nur Namen, keine Werte.</p>"
                "<p>URL erkannt: <b>%s</b> · Token erkannt: <b>%s</b></p>"
                "<p>Gefundene speicher-relevante Variablen:</p><ul>%s</ul>"
                "<p class=note>Wenn hier nichts steht, ist der Speicher noch nicht "
                "mit dieser Umgebung verbunden oder es fehlt ein Redeploy.</p>"
                % (d["url_erkannt"], d["token_erkannt"], names)))
        self._send(200, _dashboard())
