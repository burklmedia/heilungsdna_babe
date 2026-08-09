"""
Vercel Serverless Function: GET /api/pdf?d=<base64url(JSON Geburtsdaten)>

Berechnet den kompletten kosmischen Bauplan frisch aus den Geburtsdaten und
gibt ihn als gebrandetes PDF im Design von "Intuition mit Herz" zurueck.
Nichts wird vorgespeichert, jede Ausgabe entsteht neu aus den Daten.

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

# Marke (aus der Website): Violett + Gold + Flieder
GROUND = (22, 14, 46)       # #160e2e  Deckblatt
GROUND2 = (27, 19, 56)      # #1b1338  dunkle Kapitelseite
CARD = (36, 24, 72)         # #241848  Kartenflaeche
CREAM = (250, 247, 252)     # #faf7fc  helle Inhaltsseiten
GOLD = (245, 197, 107)      # #f5c56b
GOLD2 = (234, 178, 77)      # #eab24d
GOLD_DK = (184, 137, 44)    # #b8892c  Gold-Text auf hell
LILAC = (201, 164, 255)     # #c9a4ff
LILAC2 = (180, 140, 255)    # #b48cff
INK_L = (243, 238, 254)     # helle Schrift auf dunkel
INK_SOFT = (179, 168, 212)  # gedaempft auf dunkel
INK_DARK = (44, 38, 66)     # #2c2642 Schrift auf hell
BODY_DK = (74, 64, 102)     # #4a4066 Fliesstext auf hell
MUTE = (138, 122, 176)      # #8a7ab0 Eyebrow auf hell
LINE_CREAM = (228, 220, 240)
LINE_CREAM2 = (236, 229, 246)
QUOTE_BG = (244, 237, 250)  # #f4edfa
LINE_DARK = (74, 60, 112)   # feine Linie auf dunkel

PW, PH = 210.0, 297.0       # A4 mm
MX = 24.0                   # seitlicher Rand Inhalt

_SUPPORTED = None


def _supported():
    global _SUPPORTED
    if _SUPPORTED is None:
        try:
            a = set(TTFont(os.path.join(FONT_DIR, "Cormorant-Regular.ttf")).getBestCmap().keys())
            b = set(TTFont(os.path.join(FONT_DIR, "Mulish-Regular.ttf")).getBestCmap().keys())
            _SUPPORTED = a & b
        except Exception:  # noqa
            _SUPPORTED = set()
    return _SUPPORTED


def safe(s):
    """Astro-Glyphen und Emojis raus, die Cormorant/Mulish nicht haben.
    Die Sternzeichen stehen ohnehin als Worte da, es geht nichts verloren."""
    if s is None:
        return ""
    s = str(s)
    sup = _supported()
    if not sup:
        return s
    return "".join(ch for ch in s if ch in "\n\t" or ord(ch) in sup)


class Bauplan(FPDF):
    theme = "cream"

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._pth = {}

    def header(self):
        # Theme dieser Seite festhalten (Footer laeuft spaeter, wenn self.theme
        # schon auf die naechste Seite gewechselt ist).
        self._pth[self.page_no()] = self.theme
        c = {"cover": GROUND, "dark": GROUND2, "cream": CREAM}.get(self.theme, CREAM)
        self.set_fill_color(*c)
        self.rect(0, 0, PW, PH, style="F")
        self.set_xy(self.l_margin, self.t_margin)

    def footer(self):
        th = self._pth.get(self.page_no(), self.theme)
        if th == "cover":
            return
        on_dark = th == "dark"
        gold = GOLD if on_dark else GOLD_DK
        num = INK_SOFT if on_dark else MUTE
        line = (245, 197, 107) if on_dark else (234, 178, 77)
        self.set_y(-16)
        self.set_draw_color(*line)
        self.set_line_width(0.2)
        with self.local_context(stroke_opacity=0.5 if on_dark else 0.5):
            self.line(self.l_margin, self.get_y(), PW - self.r_margin, self.get_y())
        self.set_y(-13)
        self.set_font("Vibes", "", 13)
        self.set_text_color(*gold)
        self.cell((PW - self.l_margin - self.r_margin) / 2, 6, safe("Intuition mit Herz"),
                  align="L")
        self.set_font("Mul", "", 8.5)
        self.set_text_color(*num)
        self.cell((PW - self.l_margin - self.r_margin) / 2, 6, str(self.page_no()), align="R")


# ---------- kleine Zeichenhelfer ----------

def _circle(pdf, cx, cy, d, style="D"):
    pdf.ellipse(cx - d / 2.0, cy - d / 2.0, d, d, style=style)


def _eyebrow(pdf, text, color, size=8, spacing=0.9):
    pdf.set_font("Mul", "", size)
    pdf.set_text_color(*color)
    try:
        with pdf.local_context(char_spacing=spacing):
            pdf.cell(0, 4, safe(text.upper()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    except Exception:  # noqa
        pdf.cell(0, 4, safe(text.upper()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _para(pdf, text, font="Mul", style="", size=10.5, color=BODY_DK, h=5.9, after=4.0, align="J"):
    if not text:
        return
    pdf.set_font(font, style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, h, safe(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align=align)
    if after:
        pdf.ln(after)


def _keep(pdf, need):
    if pdf.get_y() + need > pdf.page_break_trigger:
        pdf.add_page()


def _heading_block(pdf, kapitel, title, subtitle=None, on_dark=False):
    """Eyebrow + grosse Ueberschrift + Goldlinie + optionale Unterzeile."""
    ink = INK_L if on_dark else INK_DARK
    eb = GOLD if on_dark else MUTE
    _eyebrow(pdf, kapitel, eb, size=8, spacing=1.1)
    pdf.ln(3.5)
    pdf.set_font("Cormo", "", 30)
    pdf.set_text_color(*ink)
    pdf.multi_cell(0, 10.5, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    y = pdf.get_y() + 3
    pdf.set_fill_color(*(GOLD if on_dark else GOLD2))
    pdf.rect(pdf.l_margin, y, 24, 0.7, style="F")
    pdf.set_y(y + 6)
    if subtitle:
        pdf.set_font("Cormo", "I", 13)
        pdf.set_text_color(*(GOLD if on_dark else GOLD_DK))
        pdf.multi_cell(0, 6, safe(subtitle), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)


# ---------- Seiten ----------

def _cover(pdf, birth, name):
    pdf.theme = "cover"
    pdf.add_page()
    cx = PW / 2.0
    # weicher Goldschein oben
    with pdf.local_context(fill_opacity=0.10):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, 14, 150, style="F")
    # zwei Ringe
    pdf.set_line_width(0.3)
    with pdf.local_context(stroke_opacity=0.24):
        pdf.set_draw_color(*LILAC)
        _circle(pdf, cx, 88, 92)
    with pdf.local_context(stroke_opacity=0.30):
        pdf.set_draw_color(*GOLD)
        _circle(pdf, cx, 88, 66)
    # Planetenpunkte auf den Ringen
    pdf.set_fill_color(*GOLD)
    _circle(pdf, cx, 89, 6, style="F")
    pdf.set_fill_color(*LILAC)
    _circle(pdf, cx + 30, 58.5, 3, style="F")
    # Sternenstaub
    for sx, sy, sd, col, op in [
        (cx - 48, 118, 2.0, LILAC2, 0.85), (36, 30, 1.5, (243, 238, 254), 0.7),
        (PW - 30, 150, 1.7, GOLD, 0.85), (34, 235, 1.3, LILAC, 0.8),
        (PW - 40, 60, 1.4, INK_L, 0.6)]:
        with pdf.local_context(fill_opacity=op):
            pdf.set_fill_color(*col)
            _circle(pdf, sx, sy, sd, style="F")

    # Wortmarke oben
    pdf.set_xy(0, 26)
    pdf.set_font("Vibes", "", 30)
    pdf.set_text_color(*GOLD)
    pdf.cell(PW, 12, safe("Intuition mit Herz"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(0)
    pdf.set_font("Mul", "", 8)
    pdf.set_text_color(*INK_SOFT)
    with pdf.local_context(char_spacing=1.6):
        pdf.cell(PW, 6, safe("HUMAN DESIGN & ASTROLOGIE"), align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Titelblock, mittig
    pdf.set_xy(0, 116)
    pdf.set_font("Cormo", "", 40)
    pdf.set_text_color(*INK_L)
    pdf.cell(PW, 15, safe("Dein kosmischer"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(0)
    pdf.cell(PW, 15, safe("Bauplan"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if name:
        pdf.ln(4)
        pdf.set_x(0)
        pdf.set_font("Vibes", "", 26)
        pdf.set_text_color(*GOLD)
        pdf.cell(PW, 12, safe("für " + name), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # goldene Kurzlinie
    ly = pdf.get_y() + 6
    pdf.set_fill_color(*GOLD)
    pdf.rect(cx - 17, ly, 34, 0.4, style="F")
    # Geburtszeile
    parts = []
    if birth.get("date"):
        parts.append(str(birth["date"]))
    if birth.get("time") and birth["time"] != "unbekannt":
        parts.append(str(birth["time"]) + " Uhr")
    if birth.get("place"):
        parts.append(str(birth["place"]))
    pdf.set_xy(0, ly + 4)
    pdf.set_font("Mul", "", 10.5)
    pdf.set_text_color(*INK_SOFT)
    with pdf.local_context(char_spacing=0.6):
        pdf.cell(PW, 7, safe(", ".join(parts)), align="C",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Fusszeile mit Satz
    pdf.set_fill_color(*GOLD)
    with pdf.local_context(fill_opacity=0.55):
        pdf.rect(MX, 250, PW - 2 * MX, 0.3, style="F")
    pdf.set_xy(MX, 256)
    pdf.set_font("Cormo", "I", 14)
    pdf.set_text_color(*INK_L)
    pdf.multi_cell(PW - 2 * MX, 6.5,
                   safe("Du musst nichts an dir reparieren. Auf den nächsten Seiten "
                        "liest du nur noch, wie du gemeint bist."),
                   align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _summary(pdf, teaser, full, kap):
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Kapitel " + str(kap), "Auf einen Blick", on_dark=True)
    _para(pdf, "Das sind die Kernpunkte, aus denen sich alles Weitere ableitet. "
               "Sie sind exakt aus deinem Geburtsmoment berechnet und ändern sich nie.",
          font="Mul", size=11, color=INK_SOFT, h=6.4, after=6)

    prof = str(teaser.get("profile") or "")
    if teaser.get("profile_name"):
        prof = (prof + ", " + str(teaser["profile_name"])).strip(", ")
    asc = full.get("ascendant", {}).get("sign", "")
    sma = ", ".join(x for x in [
        str(teaser.get("sun_sign") or ""), str(teaser.get("moon_sign") or ""), str(asc)] if x)
    rows = []
    if teaser.get("type"):
        rows.append(("Typ", str(teaser["type"]), GOLD))
    if teaser.get("authority"):
        rows.append(("Innere Autorität", str(teaser["authority"]), INK_L))
    if prof:
        rows.append(("Profil", prof, INK_L))
    if sma:
        rows.append(("Sonne, Mond, Aszendent", sma, LILAC))

    cy = pdf.get_y() + 4
    cx = pdf.l_margin
    cw = PW - pdf.l_margin - pdf.r_margin
    pad = 13.0
    row_h = 15.5
    ch = pad * 2 + row_h * len(rows)
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.3)
    _round_rect(pdf, cx, cy, cw, ch, 4.5, style="DF", border_opacity=0.30)
    for i, (label, value, col) in enumerate(rows):
        ry = cy + pad + i * row_h
        pdf.set_xy(cx + pad, ry)
        pdf.set_font("Mul", "", 8.5)
        pdf.set_text_color(*INK_SOFT)
        with pdf.local_context(char_spacing=0.8):
            pdf.cell(cw / 2 - pad, row_h - 5, safe(label.upper()))
        pdf.set_xy(cx + cw / 2, ry)
        pdf.set_font("Cormo", "", 18)
        pdf.set_text_color(*col)
        pdf.cell(cw / 2 - pad, row_h - 5, safe(value), align="R")
        if i < len(rows) - 1:
            with pdf.local_context(stroke_opacity=0.2):
                pdf.set_draw_color(*LILAC)
                pdf.set_line_width(0.2)
                pdf.line(cx + pad, ry + row_h - 2.5, cx + cw - pad, ry + row_h - 2.5)


def _round_rect(pdf, x, y, w, h, r, style="D", border_opacity=1.0):
    try:
        if border_opacity < 1.0 and "D" in style:
            # Fuellung ohne Transparenz, Rahmen mit
            if "F" in style:
                pdf.rect(x, y, w, h, style="F", round_corners=True, corner_radius=r)
            with pdf.local_context(stroke_opacity=border_opacity):
                pdf.rect(x, y, w, h, style="D", round_corners=True, corner_radius=r)
        else:
            pdf.rect(x, y, w, h, style=style, round_corners=True, corner_radius=r)
    except TypeError:
        pdf.rect(x, y, w, h, style=style if "F" in style else "D")


def _chapter(pdf, kap, section):
    pdf.theme = "cream"
    pdf.add_page()
    _heading_block(pdf, "Kapitel " + str(kap), section.get("title") or "",
                   section.get("subtitle"), on_dark=False)
    pdf.ln(2)
    if section.get("headline"):
        pdf.set_font("Cormo", "B", 17)
        pdf.set_text_color(*INK_DARK)
        pdf.multi_cell(0, 7.6, safe(section["headline"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)
    for para in str(section.get("body") or "").split("\n"):
        p = para.strip()
        if p:
            _para(pdf, p, size=10.5, color=BODY_DK, h=5.9, after=4)
    if section.get("facts"):
        _keep(pdf, 14 + 8 * len(section["facts"]))
        pdf.ln(1)
        pdf.set_draw_color(*LINE_CREAM)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), PW - pdf.r_margin, pdf.get_y())
        pdf.ln(4)
        _eyebrow(pdf, "Deine Werte im Detail", MUTE, size=8, spacing=1.0)
        pdf.ln(2)
        for row in section["facts"]:
            try:
                k, v = row[0], row[1]
            except Exception:  # noqa
                continue
            y0 = pdf.get_y()
            pdf.set_font("Mul", "", 10)
            pdf.set_text_color(*BODY_DK)
            pdf.cell((PW - pdf.l_margin - pdf.r_margin) * 0.42, 6.5, safe(str(k)))
            pdf.set_xy(pdf.l_margin + (PW - pdf.l_margin - pdf.r_margin) * 0.42, y0)
            pdf.set_font("Mul", "B", 10)
            pdf.set_text_color(*INK_DARK)
            pdf.multi_cell((PW - pdf.l_margin - pdf.r_margin) * 0.58, 6.5, safe(str(v)),
                           align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(*LINE_CREAM2)
            pdf.set_line_width(0.15)
            pdf.line(pdf.l_margin, pdf.get_y() + 0.5, PW - pdf.r_margin, pdf.get_y() + 0.5)
            pdf.ln(2)
    if section.get("takeaway"):
        _merksatz(pdf, section["takeaway"])


def _merksatz(pdf, text):
    _keep(pdf, 34)
    pdf.ln(3)
    x = pdf.l_margin
    w = PW - pdf.l_margin - pdf.r_margin
    top = pdf.get_y()
    # Text vormessen fuer die Boxhoehe
    pdf.set_font("Cormo", "I", 14)
    inner = w - 14
    lines = pdf.multi_cell(inner, 6.4, safe(text), dry_run=True, output="LINES")
    th = 6.4 * max(1, len(lines))
    box_h = 8 + 6 + th + 8
    pdf.set_fill_color(*QUOTE_BG)
    _round_rect(pdf, x, top, w, box_h, 3, style="F")
    pdf.set_fill_color(*GOLD2)
    pdf.rect(x, top, 1.2, box_h, style="F")
    pdf.set_xy(x + 7, top + 8)
    _eyebrow(pdf, "Merksatz", GOLD_DK, size=7.5, spacing=1.1)
    pdf.set_xy(x + 7, pdf.get_y() + 2)
    pdf.set_font("Cormo", "I", 14)
    pdf.set_text_color(*INK_DARK)
    pdf.multi_cell(inner, 6.4, safe(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_y(top + box_h)
    pdf.ln(3)


def _unit(pdf, title, meta, oneliner, body):
    _keep(pdf, 30)
    pdf.set_draw_color(*LINE_CREAM)
    pdf.set_line_width(0.2)
    pdf.line(pdf.l_margin, pdf.get_y(), PW - pdf.r_margin, pdf.get_y())
    pdf.ln(5)
    y0 = pdf.get_y()
    pdf.set_font("Cormo", "", 20)
    pdf.set_text_color(*INK_DARK)
    tw = pdf.get_string_width(safe(title))
    pdf.cell(tw + 4, 8, safe(title))
    if meta:
        pdf.set_font("Mul", "", 10)
        pdf.set_text_color(*MUTE)
        pdf.set_xy(pdf.l_margin + tw + 6, y0 + 2.6)
        pdf.cell(0, 5, safe(meta))
    pdf.set_xy(pdf.l_margin, y0 + 9)
    if oneliner:
        pdf.set_font("Cormo", "I", 12.5)
        pdf.set_text_color(*GOLD_DK)
        pdf.multi_cell(0, 5.6, safe(oneliner), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1.5)
    _para(pdf, body, size=10.5, color=BODY_DK, h=5.7, after=5)


def _simple_chapter_head(pdf, kap, title, intro=None):
    pdf.theme = "cream"
    pdf.add_page()
    _heading_block(pdf, "Kapitel " + str(kap), title, on_dark=False)
    pdf.ln(1)
    if intro:
        _para(pdf, intro, size=10.5, color=BODY_DK, h=6, after=5)


def build_pdf(result):
    birth = result["birth"]
    teaser = result["teaser"]
    full = result["full"]
    name = (birth.get("name") or "").strip()

    pdf = Bauplan(orientation="P", unit="mm", format="A4")
    pdf.set_margins(MX, 26, MX)
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_font("Vibes", "", os.path.join(FONT_DIR, "GreatVibes-Regular.ttf"))
    pdf.add_font("Cormo", "", os.path.join(FONT_DIR, "Cormorant-Regular.ttf"))
    pdf.add_font("Cormo", "B", os.path.join(FONT_DIR, "Cormorant-SemiBold.ttf"))
    pdf.add_font("Cormo", "I", os.path.join(FONT_DIR, "Cormorant-Italic.ttf"))
    pdf.add_font("Mul", "", os.path.join(FONT_DIR, "Mulish-Regular.ttf"))
    pdf.add_font("Mul", "B", os.path.join(FONT_DIR, "Mulish-Bold.ttf"))
    pdf.set_title(safe("Dein kosmischer Bauplan"))
    pdf.set_author("Intuition mit Herz")

    _cover(pdf, birth, name)

    kap = 1
    _summary(pdf, teaser, full, kap)

    for s in full.get("sections", []):
        kap += 1
        _chapter(pdf, kap, s)

    # Planeten im Detail
    positions = full.get("positions", [])
    if positions:
        kap += 1
        _simple_chapter_head(pdf, kap, "Deine Planeten im Detail",
                             "Jeder Planet steht für einen Bereich deines Lebens. "
                             "Zeichen und Haus sagen, wie und wo er sich zeigt.")
        for p in positions:
            sign = str(p.get("sign") or "")
            deg = str(p.get("deg") or "")
            house = p.get("house")
            meta = ", ".join(x for x in [sign, deg] if x)
            if house:
                meta += (", " if meta else "") + str(house) + ". Haus"
            _unit(pdf, str(p.get("label") or p.get("key") or ""), meta,
                  p.get("meaning"), p.get("desc"))

    # Haeuser
    houses = full.get("houses", [])
    if houses:
        kap += 1
        _simple_chapter_head(pdf, kap, "Deine Häuser",
                             "Die zwölf Lebensbühnen, auf denen sich dein Chart zeigt.")
        for h in houses:
            _unit(pdf, "Haus " + str(h.get("nr", "")), str(h.get("title") or ""),
                  None, h.get("meaning"))

    # Energiezentren
    centers = full.get("hd_centers", [])
    if centers:
        kap += 1
        _simple_chapter_head(pdf, kap, "Deine neun Energiezentren",
                             "Was bei dir fest verankert ist und was dich fein "
                             "wahrnehmen lässt.")
        for c in centers:
            state = "definiert" if c.get("defined") else "offen"
            body = str(c.get("detail") or "")
            if c.get("tip"):
                body += ("\n" if body else "") + "Impuls: " + str(c["tip"])
            _unit(pdf, str(c.get("name") or ""), state,
                  c.get("theme") or c.get("meaning"), body)

    # Numerologie
    num = full.get("numerology")
    if num:
        kap += 1
        _simple_chapter_head(pdf, kap, "Deine Numerologie",
                             "Zwei Zahlen, die sich aus deinem Geburtsdatum und deinem Vornamen "
                             "ergeben und einen eigenen Blick auf deine Themen werfen.")
        lp_body = str(num.get("text") or "")
        if num.get("calc"):
            lp_body += "\nSo wird sie gerechnet: " + str(num["calc"])
        _unit(pdf, num.get("title") or "Lebenszahl",
              "Lebenszahl " + str(num.get("lifepath", "")),
              num.get("tagline"), lp_body)
        nn = num.get("name_number")
        if nn:
            _unit(pdf, "Namenszahl " + str(nn.get("number", "")),
                  nn.get("name") or "", None, nn.get("text"))
        if num.get("note"):
            pdf.ln(2)
            _para(pdf, num["note"], size=8.5, color=MUTE, h=4.6, after=0)

    # Abschluss
    if full.get("closing"):
        kap += 1
        _simple_chapter_head(pdf, kap, "Zum Schluss")
        _para(pdf, full["closing"], font="Cormo", size=14, color=INK_DARK, h=7, after=4)
        if full.get("note"):
            pdf.ln(2)
            _para(pdf, full["note"], size=8.5, color=MUTE, h=4.6, after=0)

    return bytes(pdf.output())


def _decode(d):
    d = d.replace("-", "+").replace("_", "/")
    d += "=" * (-len(d) % 4)
    return json.loads(base64.b64decode(d).decode("utf-8"))


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
            result = build_result(_decode(d))
            pdf_bytes = build_pdf(result)
            fname = _filename(result["birth"].get("name"))
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
