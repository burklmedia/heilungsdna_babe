"""
Vercel Serverless Function: GET /api/pdf?d=<base64url(JSON Geburtsdaten)>

Berechnet den kompletten kosmischen Bauplan frisch aus den Geburtsdaten und
gibt ihn als gebrandetes PDF zurueck. Nichts wird vorgespeichert, jede Ausgabe
entsteht neu aus den uebergebenen Daten.

Der Parameter d ist base64url-kodiertes JSON mit denselben Feldern, die auch
/api/analyze bekommt: name, date, time, place, lat, lon, tz, gender.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import sys
import base64
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_IMPORT_ERROR = None
try:
    from analyze import build_result
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    from fontTools.ttLib import TTFont
except Exception:  # noqa
    import traceback
    _IMPORT_ERROR = traceback.format_exc()

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_assets", "fonts")

# Farben (Marke: Violett + Gold, auf hellem Grund fuers Lesen und Drucken)
VIOLET = (74, 45, 122)
VIOLET_DK = (48, 30, 84)
GOLD = (168, 124, 36)
GOLD_LINE = (207, 169, 92)
INK = (44, 38, 66)
BODY = (72, 66, 90)
MUTE = (122, 114, 142)
TINT = (245, 240, 250)

# Zeichen, die die eingebettete Schrift kann (einmal laden), damit nie leere
# Kaestchen im PDF landen (z. B. Deko-Emojis).
_SUPPORTED = None


def _supported():
    global _SUPPORTED
    if _SUPPORTED is None:
        try:
            _SUPPORTED = set(TTFont(os.path.join(FONT_DIR, "DejaVuSans.ttf")).getBestCmap().keys())
        except Exception:  # noqa
            _SUPPORTED = set()
    return _SUPPORTED


def safe(s):
    if s is None:
        return ""
    s = str(s)
    sup = _supported()
    if not sup:
        return s
    out = []
    for ch in s:
        if ch in "\n\t" or ord(ch) in sup:
            out.append(ch)
        # alles andere (Emoji, Variation Selectors) still weglassen
    return "".join(out)


class Bauplan(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Vibes", "", 18)
        self.set_text_color(*GOLD)
        self.set_y(8)
        self.cell(0, 8, safe("Intuition mit Herz"), align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*GOLD_LINE)
        self.set_line_width(0.3)
        y = self.get_y() + 1
        self.line(self.l_margin + 30, y, self.w - self.r_margin - 30, y)
        self.set_y(self.t_margin)

    def footer(self):
        self.set_y(-13)
        self.set_font("Deja", "", 8)
        self.set_text_color(*MUTE)
        self.cell(0, 6, safe("Dein kosmischer Bauplan"), align="L")
        self.cell(0, 6, str(self.page_no()), align="R")


def _para(pdf, txt, size=10.5, color=BODY, style="", h=5.6, after=1.6, family="Deja"):
    if not txt:
        return
    pdf.set_font(family, style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, h, safe(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if after:
        pdf.ln(after)


def _keep(pdf, need=30):
    if pdf.get_y() + need > pdf.page_break_trigger:
        pdf.add_page()


def _heading(pdf, title, sub=None):
    _keep(pdf, 34)
    pdf.set_font("Deja", "B", 15)
    pdf.set_text_color(*VIOLET)
    pdf.multi_cell(0, 7.5, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y = pdf.get_y() + 1.2
    pdf.set_draw_color(*GOLD_LINE)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, y, pdf.l_margin + 22, y)
    pdf.ln(4.5)
    if sub:
        _para(pdf, sub, size=10, color=GOLD, h=5, after=2)


def _facts(pdf, facts):
    for row in facts or []:
        try:
            k, v = row[0], row[1]
        except Exception:  # noqa
            continue
        _keep(pdf, 12)
        x0 = pdf.get_x()
        pdf.set_font("Deja", "B", 9.5)
        pdf.set_text_color(*VIOLET)
        pdf.cell(42, 5.6, safe(str(k)), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Deja", "", 9.5)
        pdf.set_text_color(*BODY)
        pdf.multi_cell(0, 5.6, safe(str(v)), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(x0)
    pdf.ln(1.5)


def _takeaway(pdf, txt):
    if not txt:
        return
    _keep(pdf, 26)
    pdf.ln(1)
    start = pdf.get_y()
    pdf.set_x(pdf.l_margin + 5)
    pdf.set_font("Deja", "B", 10)
    pdf.set_text_color(*VIOLET_DK)
    pdf.multi_cell(pdf.epw - 5, 5.6, safe(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    end = pdf.get_y()
    pdf.set_draw_color(*GOLD_LINE)
    pdf.set_line_width(1.4)
    pdf.line(pdf.l_margin + 1.2, start + 0.5, pdf.l_margin + 1.2, end - 0.5)
    pdf.ln(3)


def _factcard(pdf, rows):
    """Auf einen Blick: kleine getoente Box mit den Kernpunkten."""
    _keep(pdf, 12 + 8 * len(rows))
    top = pdf.get_y()
    pad = 5
    line_h = 7.2
    box_h = pad * 2 + line_h * len(rows)
    pdf.set_fill_color(*TINT)
    pdf.set_draw_color(*GOLD_LINE)
    pdf.set_line_width(0.3)
    pdf.rect(pdf.l_margin, top, pdf.epw, box_h, style="DF")
    label_w = 56
    pdf.set_xy(pdf.l_margin + pad, top + pad)
    for k, v in rows:
        pdf.set_x(pdf.l_margin + pad)
        pdf.set_font("Deja", "B", 9.5)
        pdf.set_text_color(*GOLD)
        pdf.cell(label_w, line_h, safe(k), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Deja", "B", 10.5)
        pdf.set_text_color(*VIOLET_DK)
        pdf.multi_cell(pdf.epw - pad * 2 - label_w, line_h, safe(v),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_y(top + box_h)
    pdf.ln(6)


def build_pdf(result):
    birth = result["birth"]
    teaser = result["teaser"]
    full = result["full"]
    name = (birth.get("name") or "").strip()

    pdf = Bauplan(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(True, margin=16)
    pdf.set_margins(18, 18, 18)
    pdf.add_font("Deja", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
    pdf.add_font("Deja", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
    pdf.add_font("Vibes", "", os.path.join(FONT_DIR, "GreatVibes-Regular.ttf"))
    pdf.set_title(safe("Dein kosmischer Bauplan"))
    pdf.set_author("Intuition mit Herz")

    # ---------- Deckblatt ----------
    pdf.add_page()
    pdf.ln(26)
    pdf.set_font("Vibes", "", 44)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 20, safe("Intuition mit Herz"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.set_font("Deja", "B", 27)
    pdf.set_text_color(*VIOLET)
    pdf.cell(0, 13, safe("Dein kosmischer Bauplan"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    if name:
        pdf.set_font("Deja", "", 14)
        pdf.set_text_color(*BODY)
        pdf.cell(0, 8, safe("für " + name), align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Geburtszeile
    parts = []
    if birth.get("date"):
        parts.append(str(birth["date"]))
    if birth.get("time") and birth["time"] != "unbekannt":
        parts.append(str(birth["time"]) + " Uhr")
    if birth.get("place"):
        parts.append(str(birth["place"]))
    pdf.ln(1)
    pdf.set_font("Deja", "", 10.5)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 7, safe(", ".join(parts)), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # goldene Linie
    pdf.ln(5)
    y = pdf.get_y()
    pdf.set_draw_color(*GOLD_LINE)
    pdf.set_line_width(0.5)
    pdf.line(pdf.w / 2 - 25, y, pdf.w / 2 + 25, y)
    pdf.ln(9)
    pdf.set_font("Deja", "", 11)
    pdf.set_text_color(*BODY)
    intro = ("Das hier ist kein Test und keine Schublade. Es ist ein Spiegel. "
             "Er zeigt dir, wie du gemeint bist. Lies ihn in Ruhe, und bleib bei "
             "den Sätzen, die dich berühren.")
    pdf.set_x(pdf.l_margin + 12)
    pdf.multi_cell(pdf.epw - 24, 6, safe(intro), align="C",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)

    # Auf einen Blick
    prof = str(teaser.get("profile") or "")
    if teaser.get("profile_name"):
        prof = (prof + ", " + str(teaser["profile_name"])).strip(", ")
    smax = full.get("ascendant", {}).get("sign", "")
    sma = []
    if teaser.get("sun_sign"):
        sma.append("Sonne " + str(teaser["sun_sign"]))
    if teaser.get("moon_sign"):
        sma.append("Mond " + str(teaser["moon_sign"]))
    if smax:
        sma.append("Aszendent " + str(smax))
    rows = []
    if teaser.get("type"):
        rows.append(("Typ", str(teaser["type"])))
    if teaser.get("authority"):
        rows.append(("Innere Autorität", str(teaser["authority"])))
    if prof:
        rows.append(("Profil", prof))
    if sma:
        rows.append(("Sonne, Mond, Aszendent", ", ".join(sma)))
    if rows:
        pdf.set_font("Deja", "B", 12)
        pdf.set_text_color(*VIOLET)
        pdf.cell(0, 8, safe("Auf einen Blick"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)
        _factcard(pdf, rows)

    # ---------- Die 16 Kapitel ----------
    pdf.add_page()
    for s in full.get("sections", []):
        _heading(pdf, s.get("title"), s.get("subtitle"))
        if s.get("headline"):
            _para(pdf, s["headline"], size=11, color=INK, style="B", h=5.8, after=1.5)
        if s.get("body"):
            _para(pdf, s["body"], size=10.5, color=BODY, h=5.7, after=1.5)
        if s.get("facts"):
            _facts(pdf, s["facts"])
        if s.get("takeaway"):
            _takeaway(pdf, s["takeaway"])
        pdf.ln(3)

    # ---------- Planeten im Detail ----------
    positions = full.get("positions", [])
    if positions:
        pdf.add_page()
        _heading(pdf, "Deine Planeten im Detail",
                 "Wo die Kräfte in deinem Chart genau stehen")
        for p in positions:
            _keep(pdf, 24)
            label = str(p.get("label") or p.get("key") or "")
            sign = str(p.get("sign") or "")
            deg = str(p.get("deg") or "")
            house = p.get("house")
            hl = str(p.get("house_meaning") or "")
            head = label
            tail = " ".join(x for x in [sign, deg] if x)
            if tail:
                head = label + ", " + tail
            if house:
                head += ", Haus " + str(house)
            pdf.set_font("Deja", "B", 11)
            pdf.set_text_color(*VIOLET)
            pdf.multi_cell(0, 5.8, safe(head), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if p.get("meaning"):
                _para(pdf, p["meaning"], size=9.5, color=GOLD, h=5, after=0.8)
            if hl:
                _para(pdf, "Lebensbereich: " + hl, size=9.5, color=MUTE, h=5, after=0.8)
            if p.get("desc"):
                _para(pdf, p["desc"], size=10, color=BODY, h=5.5, after=2.5)

    # ---------- Haeuser ----------
    houses = full.get("houses", [])
    if houses:
        _keep(pdf, 40)
        _heading(pdf, "Deine Häuser",
                 "Die zwölf Lebensbühnen, auf denen sich dein Chart zeigt")
        for h in houses:
            _keep(pdf, 16)
            title = "Haus " + str(h.get("nr", "")) + ", " + str(h.get("title") or "")
            pdf.set_font("Deja", "B", 10.5)
            pdf.set_text_color(*VIOLET)
            pdf.multi_cell(0, 5.5, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            _para(pdf, h.get("meaning"), size=9.8, color=BODY, h=5.3, after=2.2)

    # ---------- Energiezentren ----------
    centers = full.get("hd_centers", [])
    if centers:
        pdf.add_page()
        _heading(pdf, "Deine neun Energiezentren",
                 "Was bei dir fest verankert ist und was dich fein wahrnehmen lässt")
        for c in centers:
            _keep(pdf, 26)
            state = "definiert" if c.get("defined") else "offen"
            title = str(c.get("name") or "") + ", " + state
            pdf.set_font("Deja", "B", 11)
            pdf.set_text_color(*VIOLET)
            pdf.multi_cell(0, 5.8, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if c.get("theme") or c.get("meaning"):
                _para(pdf, c.get("theme") or c.get("meaning"), size=9.5, color=GOLD,
                      h=5, after=0.8)
            if c.get("detail"):
                _para(pdf, c["detail"], size=10, color=BODY, h=5.5, after=1)
            if c.get("tip"):
                _para(pdf, "Impuls: " + str(c["tip"]), size=9.8, color=MUTE,
                      h=5.2, after=2.5)

    # ---------- Abschluss ----------
    if full.get("closing"):
        pdf.add_page()
        _heading(pdf, "Zum Schluss")
        _para(pdf, full["closing"], size=11.5, color=INK, h=6.2, after=4)
    if full.get("note"):
        pdf.ln(2)
        _para(pdf, full["note"], size=8.5, color=MUTE, h=4.6, after=0)

    out = pdf.output()
    return bytes(out)


def _decode(d):
    d = d.replace("-", "+").replace("_", "/")
    d += "=" * (-len(d) % 4)
    raw = base64.b64decode(d)
    return json.loads(raw.decode("utf-8"))


def _filename(name):
    base = re.sub(r"[^A-Za-z0-9]+", "-", (name or "").strip()).strip("-")
    return ("Kosmischer-Bauplan-" + base + ".pdf") if base else "Kosmischer-Bauplan.pdf"


class handler(BaseHTTPRequestHandler):
    def _err(self, code, msg, detail=None):
        payload = {"ok": False, "error": msg}
        if detail:
            payload["detail"] = detail
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if _IMPORT_ERROR:
            return self._err(500, "Import fehlgeschlagen.", _IMPORT_ERROR)
        try:
            qs = parse_qs(urlparse(self.path).query)
            d = (qs.get("d") or [""])[0]
            if not d:
                return self._err(400, "Kein Bauplan-Parameter (d) angegeben.")
            body = _decode(d)
            result = build_result(body)
            pdf_bytes = build_pdf(result)
            fname = _filename(body.get("name"))
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", 'inline; filename="%s"' % fname)
            self.send_header("Content-Length", str(len(pdf_bytes)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(pdf_bytes)
        except ValueError as e:
            self._err(400, str(e))
        except Exception as e:  # noqa
            import traceback
            self._err(500, "PDF konnte nicht erstellt werden.", traceback.format_exc())
