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
import math

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
INK_L = (243, 238, 254)     # helle Schrift auf dunkel (Ueberschriften/Werte)
INK_SOFT = (194, 183, 224)  # gedaempft auf dunkel
# Das ganze Dokument ist jetzt dunkel gehalten. Die frueher hellen Rollen
# zeigen deshalb auf dunkeltaugliche Werte.
INK_DARK = (243, 238, 254)  # Ueberschriften auf dunkel (= hell)
BODY_DK = (206, 197, 230)   # Fliesstext auf dunkel
GOLD_DK = (245, 197, 107)   # Gold-Text auf dunkel (= GOLD)
MUTE = (150, 134, 190)      # #9686be gedaempftes Flieder
CARD2 = (44, 30, 84)        # #2c1e54 zweite Kartenflaeche
LINE_CREAM = (74, 60, 112)  # feine Trennlinie (Flieder, dunkel)
LINE_CREAM2 = (58, 46, 92)  # noch feiner
QUOTE_BG = (44, 30, 84)     # Zitat-/Kartenflaeche auf dunkel
LINE_DARK = (74, 60, 112)   # feine Linie auf dunkel

PW, PH = 210.0, 297.0       # A4 mm
MX = 24.0                   # seitlicher Rand Inhalt

# Kurzzeichen fuer die Abbildungen: Cormorant/Mulish koennen keine Astro-Glyphen,
# deshalb stehen Planeten und Zeichen im Rad als klare Kuerzel da (nichts geht verloren).
SIGN_ABBR = ["Wid", "Sti", "Zwi", "Kre", "Löw", "Jgf", "Waa", "Sko", "Sch", "Stb", "Was", "Fis"]
PLANET_ABBR = {
    "Sonne": "So", "Mond": "Mo", "Merkur": "Me", "Venus": "Ve", "Mars": "Ma",
    "Jupiter": "Ju", "Saturn": "Sa", "Uranus": "Ur", "Neptun": "Ne", "Pluto": "Pl",
    "Chiron": "Ch", "Nordknoten": "Kn", "Südknoten": "Sk",
}
# Echte Astrosymbole (gezeichnet aus der eingebetteten Symbol-Schrift)
SIGN_GLYPH = [chr(0x2648 + i) for i in range(12)]  # Widder..Fische
PLANET_GLYPH = {
    "Sonne": "☉", "Mond": "☽", "Merkur": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptun": "♆", "Pluto": "♇", "Chiron": "⚷",
    "Nordknoten": "☊", "Südknoten": "☋",
}

# Glossar "Was bedeutet was?" (aus dem Uebersicht-Reiter der Website)
LEGEND = [
    ("Human-Design-Typ", "Deine Energie-Bauart. Sie zeigt, wie du am stimmigsten handelst und Entscheidungen triffst."),
    ("Innere Autorität", "Woher deine verlässliche Ja-oder-Nein-Klarheit kommt, dein innerer Kompass."),
    ("Profil", "Die Rolle, in der sich dein Weg entfaltet, mit einer bewussten und einer unbewussten Seite."),
    ("Zentren", "Neun Energiefelder. Definiert heißt verlässlich und konstant, offen heißt lernend und formbar."),
    ("Sonne", "Dein Wesenskern, wer du im tiefsten Sinn bist."),
    ("Mond", "Deine Gefühlswelt und was du brauchst, um dich sicher zu fühlen."),
    ("Aszendent (AC)", "Wie du auf andere wirkst, dein Auftritt. Dafür braucht es deine Geburtszeit."),
    ("Deszendent (DC)", "Er liegt genau gegenüber vom AC und zeigt, was du im Partner suchst und anziehst."),
    ("MC / IC", "Deine Berufung nach außen (MC) und deine Wurzel nach innen (IC)."),
    ("Häuser", "Zwölf Lebensfelder. Sie zeigen, in welchem Bereich deines Lebens ein Planet konkret wirkt."),
    ("Elemente-Balance", "Wie sich Feuer, Erde, Luft und Wasser in dir verteilen. Dein stärkstes Element geht dir am leichtesten von der Hand."),
    ("Deine größte Stärke", "Die Stelle, an der Human Design und Natalchart dasselbe sagen. Was dir mühelos gelingt."),
    ("Deine größten Schwierigkeiten", "Die drei Stellen, an denen du am leichtesten von dir selbst abrutschst. Je Schwierigkeit: woran du sie erkennst, woher sie kommt, was sie dich kostet und wie du damit arbeitest."),
    ("Intuitionstyp", "Über welchen Kanal deine innere Führung zu dir spricht, abgeleitet aus deinem Mond."),
    ("Chiron", "Deine älteste Wunde und genau dort deine besondere Gabe, andere zu heilen."),
    ("Mondknoten-Achse", "Dein roter Faden. Woher du kommst (Südknoten) und wohin du wächst (Nordknoten), deine Lebensaufgabe."),
    ("Stellium", "Eine Häufung von Planeten in einem Zeichen oder Haus. Ein besonders betonter Lebensschwerpunkt."),
    ("Aspekte", "Die Winkel zwischen deinen Planeten, die inneren Gespräche zwischen deinen Kräften."),
]

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


def _spark(pdf, cx, cy, r, color):
    """Ein zartes vierzackiges Funkel-Sternchen (gefuellt)."""
    pts = []
    for i in range(8):
        rad = r if i % 2 == 0 else r * 0.34
        a = math.radians(i * 45 - 90)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pdf.set_fill_color(*color)
    try:
        pdf.polygon(pts, style="F")
    except Exception:  # noqa
        _circle(pdf, cx, cy, r, style="F")


def _teardrop_pts(cx, cy, s, steps=28):
    """Punkte eines nach oben zeigenden Tropfens (fuer Wasser/Feuer)."""
    R = 0.29 * s
    oy = cy + 0.20 * s
    pts = [(cx, cy - 0.52 * s)]
    for i in range(steps + 1):
        ang = math.radians(60 - 300.0 * i / steps)
        pts.append((cx + R * math.cos(ang), oy - R * math.sin(ang)))
    return pts


def _wave(pdf, cx, cy, w, amp, color, segs=22, lw=0.5):
    """Zarte Wellenlinie."""
    pdf.set_draw_color(*color)
    pdf.set_line_width(lw)
    prev = None
    for i in range(segs + 1):
        t = i / segs
        x = cx - w / 2.0 + w * t
        y = cy + amp * math.sin(t * math.pi * 3)
        if prev is not None:
            pdf.line(prev[0], prev[1], x, y)
        prev = (x, y)


def _element_symbol(pdf, cx, cy, s, key):
    """Zeichnet das Element-Sinnbild des Intuitionstyps als Medaillon
    (Feuer, Erde, Luft, Wasser) – im Stil der Website-Skizzen."""
    # Medaillon: weicher Schein + Goldring
    with pdf.local_context(fill_opacity=0.10):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, s * 1.9, style="F")
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    with pdf.local_context(stroke_opacity=0.55):
        _circle(pdf, cx, cy, s * 1.7)
    with pdf.local_context(stroke_opacity=0.3):
        pdf.set_draw_color(*LILAC)
        _circle(pdf, cx, cy, s * 1.86)

    def _fill_poly(pts, col, op):
        with pdf.local_context(fill_opacity=op):
            pdf.set_fill_color(*col)
            pdf.polygon(pts, style="F")

    if key == "Feuer":
        pts = _teardrop_pts(cx, cy - 0.02 * s, s * 1.02)
        _fill_poly(pts, GOLD, 0.22)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.7)
        pdf.polygon(pts, style="D")
        _fill_poly(_teardrop_pts(cx, cy + 0.14 * s, 0.5 * s), LILAC, 0.5)
        for dx, dy in [(-0.55, -0.34), (0.57, -0.16), (0.0, 0.62)]:
            _spark(pdf, cx + dx * s, cy + dy * s, 0.1 * s, LILAC)
    elif key == "Wasser":
        pts = _teardrop_pts(cx, cy - 0.12 * s, 0.94 * s)
        _fill_poly(pts, GOLD, 0.22)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.7)
        pdf.polygon(pts, style="D")
        _wave(pdf, cx, cy + 0.5 * s, s * 1.05, 0.06 * s, LILAC, lw=0.6)
        _wave(pdf, cx, cy + 0.66 * s, s * 0.8, 0.05 * s, LILAC2, lw=0.5)
    elif key == "Erde":
        tri = [(cx, cy - 0.5 * s), (cx + 0.56 * s, cy + 0.34 * s), (cx - 0.56 * s, cy + 0.34 * s)]
        _fill_poly(tri, GOLD, 0.2)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.7)
        pdf.polygon(tri, style="D")
        pdf.set_draw_color(*LILAC)
        pdf.set_line_width(0.7)
        pdf.line(cx - 0.66 * s, cy + 0.34 * s, cx + 0.66 * s, cy + 0.34 * s)
        tri2 = [(cx + 0.18 * s, cy + 0.02 * s), (cx + 0.4 * s, cy + 0.34 * s),
                (cx - 0.04 * s, cy + 0.34 * s)]
        _fill_poly(tri2, LILAC, 0.4)
    else:  # Luft
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.7)
        pdf.ellipse(cx - 0.52 * s, cy - 0.3 * s, 1.04 * s, 0.6 * s, style="D")
        with pdf.local_context(stroke_opacity=0.6):
            pdf.set_draw_color(*LILAC)
            _circle(pdf, cx, cy, 0.34 * s)
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 0.16 * s, style="F")
        _wave(pdf, cx, cy - 0.46 * s, 0.66 * s, 0.045 * s, LILAC, segs=16, lw=0.5)
        _wave(pdf, cx, cy + 0.46 * s, 0.66 * s, 0.045 * s, LILAC, segs=16, lw=0.5)


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


def _heading_block(pdf, kapitel, title, subtitle=None, on_dark=True):
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

def _ritual_wheel(pdf, cx, cy, R):
    """Ein Sternenrad wie die Animation beim Laden des Bauplans: zwei Ringe,
    Ticks, die zwoelf Tierkreiszeichen und ein leuchtender Kern."""
    def pt(r, deg):
        a = math.radians(deg - 90)
        return (cx + r * math.cos(a), cy + r * math.sin(a))

    # weicher Goldschein
    with pdf.local_context(fill_opacity=0.10):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, R * 2.7, style="F")
    # aeusserer Goldring + innerer Fliederring
    pdf.set_line_width(0.4)
    with pdf.local_context(stroke_opacity=0.6):
        pdf.set_draw_color(*GOLD)
        _circle(pdf, cx, cy, R * 2)
    pdf.set_line_width(0.3)
    with pdf.local_context(stroke_opacity=0.45):
        pdf.set_draw_color(*LILAC)
        _circle(pdf, cx, cy, R * 1.34)
    # Ticks + Tierkreiszeichen rundherum
    pdf.set_line_width(0.3)
    for k in range(12):
        deg = k * 30
        a, b = pt(R, deg), pt(R - 3.5, deg)
        with pdf.local_context(stroke_opacity=0.5):
            pdf.set_draw_color(*LILAC)
            pdf.line(a[0], a[1], b[0], b[1])
        gp = pt(R - 10, deg + 15)
        _glyph(pdf, gp[0], gp[1], SIGN_GLYPH[k], 9, GOLD)
    # feine Speichen nach innen
    with pdf.local_context(stroke_opacity=0.16):
        pdf.set_draw_color(*LILAC)
        pdf.set_line_width(0.2)
        for k in range(12):
            a, b = pt(R * 1.34, k * 30), pt(R * 0.34, k * 30)
            pdf.line(a[0], a[1], b[0], b[1])
    # zwei zarte Planetenpunkte auf den Ringen
    p1 = pt(R, 52)
    pdf.set_fill_color(*LILAC)
    _circle(pdf, p1[0], p1[1], 2.6, style="F")
    p2 = pt(R * 1.34, 200)
    pdf.set_fill_color(*GOLD)
    _circle(pdf, p2[0], p2[1], 2.2, style="F")
    # leuchtender Kern
    with pdf.local_context(fill_opacity=0.5):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 12, style="F")
    with pdf.local_context(fill_opacity=0.85):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 6, style="F")
    pdf.set_fill_color(255, 250, 240)
    _circle(pdf, cx, cy, 2.6, style="F")


def _abstract_emblem(pdf, cx, cy, R):
    """Abstraktes Sternen-Emblem: zwei Ringe, die zwoelf Tierkreiszeichen zart
    angedeutet, ein verbindendes Sternennetz und ein leuchtender Kern – ein
    Bild, das alle Systeme miteinander verwebt."""
    def pt(r, deg):
        a = math.radians(deg - 90)
        return (cx + r * math.cos(a), cy + r * math.sin(a))

    with pdf.local_context(fill_opacity=0.10):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, R * 2.7, style="F")
    pdf.set_line_width(0.5)
    with pdf.local_context(stroke_opacity=0.6):
        pdf.set_draw_color(*GOLD)
        _circle(pdf, cx, cy, R * 2)
    pdf.set_line_width(0.3)
    with pdf.local_context(stroke_opacity=0.4):
        pdf.set_draw_color(*LILAC)
        _circle(pdf, cx, cy, R * 1.28)
    # Tierkreiszeichen zart auf dem aeusseren Band
    for k in range(12):
        gp = pt(R * 0.85, k * 30 + 15)
        with pdf.local_context(fill_opacity=0.8):
            _glyph(pdf, gp[0], gp[1], SIGN_GLYPH[k], 8, GOLD)
    # verbindendes Sternennetz (verbindet alles miteinander)
    net = [(0.92, 22), (0.62, 70), (0.86, 128), (0.5, 175), (0.9, 214),
           (0.66, 262), (0.44, 312), (0.8, 340)]
    nodes = [pt(R * f, d) for f, d in net]
    links = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0),
             (0, 2), (2, 4), (4, 6), (6, 0)]
    pdf.set_line_width(0.3)
    with pdf.local_context(stroke_opacity=0.32):
        pdf.set_draw_color(*LILAC)
        for a, b in links:
            pdf.line(nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1])
    # Knoten: teils Sternchen (Astrologie), teils Bodygraph-Formen (Human
    # Design) – so verweben sich die Systeme zu einem Bauplan.
    def _node_shape(nx, ny, kind, s=2.5):
        if kind == "square":
            p = [(nx - s, ny - s), (nx + s, ny - s), (nx + s, ny + s), (nx - s, ny + s)]
        elif kind == "diamond":
            p = [(nx, ny - s), (nx + s, ny), (nx, ny + s), (nx - s, ny)]
        elif kind == "tri_up":
            p = [(nx, ny - s), (nx + s, ny + s), (nx - s, ny + s)]
        else:  # tri_down
            p = [(nx, ny + s), (nx + s, ny - s), (nx - s, ny - s)]
        with pdf.local_context(fill_opacity=0.16):
            pdf.set_fill_color(*GOLD)
            pdf.polygon(p, style="F")
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.5)
        with pdf.local_context(stroke_opacity=0.85):
            pdf.polygon(p, style="D")

    kinds = ["spark", "square", "diamond", "tri_up", "spark", "tri_down", "diamond", "dot"]
    for i, (nx, ny) in enumerate(nodes):
        kind = kinds[i % len(kinds)]
        if kind == "spark":
            _spark(pdf, nx, ny, 1.9, GOLD)
        elif kind == "dot":
            pdf.set_fill_color(*LILAC)
            _circle(pdf, nx, ny, 1.7, style="F")
        else:
            _node_shape(nx, ny, kind)
    # leuchtender Kern
    with pdf.local_context(fill_opacity=0.5):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 10, style="F")
    with pdf.local_context(fill_opacity=0.9):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 5, style="F")
    pdf.set_fill_color(255, 250, 240)
    _circle(pdf, cx, cy, 2.2, style="F")


def _cover(pdf, birth, name):
    pdf.theme = "cover"
    pdf.add_page()
    cx = PW / 2.0

    wy = 120.0
    Rw = 36.0

    # Sternenstaub + Funkeln, grosszuegig gestreut (etwas dramatischer)
    for sx, sy, sd, col, op in [
        (cx - 66, 150, 2.0, LILAC2, 0.85), (36, 40, 1.5, (243, 238, 254), 0.7),
        (PW - 30, 150, 1.7, GOLD, 0.85), (34, 250, 1.3, LILAC, 0.8),
        (PW - 40, 238, 1.4, INK_L, 0.6), (cx + 66, 205, 1.6, GOLD, 0.7),
        (44, 120, 1.3, GOLD, 0.6), (PW - 46, 96, 1.4, LILAC, 0.7)]:
        with pdf.local_context(fill_opacity=op):
            pdf.set_fill_color(*col)
            _circle(pdf, sx, sy, sd, style="F")
    for sx, sy, sr, col in [(cx - 74, 96, 2.2, GOLD), (PW - 34, 250, 2.0, LILAC),
                            (40, 205, 1.8, LILAC2), (cx + 76, 150, 2.0, GOLD)]:
        _spark(pdf, sx, sy, sr, col)

    # Titelblock oben: Titel + Name – ueber dem Sternenrad
    pdf.set_xy(0, 28)
    pdf.set_font("Cormo", "", 40)
    pdf.set_text_color(*INK_L)
    pdf.cell(PW, 14, safe("Dein kosmischer"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(0)
    pdf.cell(PW, 14, safe("Bauplan"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if name:
        pdf.ln(2)
        pdf.set_x(0)
        pdf.set_font("Vibes", "", 27)
        pdf.set_text_color(*GOLD)
        pdf.cell(PW, 12, safe("für " + name), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ---- Medaillon: Platte + Doppelrahmen (Gold/Flieder) um das Sternenrad ----
    with pdf.local_context(fill_opacity=0.55):
        pdf.set_fill_color(*CARD2)
        _circle(pdf, cx, wy, 94, style="F")
    pdf.set_line_width(0.8)
    with pdf.local_context(stroke_opacity=0.85):
        pdf.set_draw_color(*GOLD)
        _circle(pdf, cx, wy, 90)
    pdf.set_line_width(0.4)
    with pdf.local_context(stroke_opacity=0.5):
        pdf.set_draw_color(*LILAC)
        _circle(pdf, cx, wy, 96)
    # vier Funkel-Sternchen auf dem Rahmen
    for ang, col in [(45, GOLD), (135, LILAC), (225, GOLD), (315, LILAC)]:
        a = math.radians(ang)
        _spark(pdf, cx + 45 * math.cos(a), wy + 45 * math.sin(a), 2.4, col)
    # Abstraktes, verbindendes Sternen-Emblem in der Mitte
    _abstract_emblem(pdf, cx, wy, Rw)

    # Geburtszeile UNTER dem Kreis, in einer geschmeidigen Sternen-Kapsel
    parts = []
    if birth.get("date"):
        _bd = str(birth["date"])
        _m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", _bd)
        parts.append(f"{_m.group(3)}.{_m.group(2)}.{_m.group(1)}" if _m else _bd)
    if birth.get("time") and birth["time"] != "unbekannt":
        parts.append(str(birth["time"]) + " Uhr")
    if birth.get("place"):
        parts.append(str(birth["place"]))
    line = "   ·   ".join(parts)
    py = 174.0
    pdf.set_font("Mul", "", 10.5)
    tw = pdf.get_string_width(line)
    pill_w = min(PW - 2 * MX, tw + 42)
    pill_h = 13.0
    px = cx - pill_w / 2.0
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    _round_rect(pdf, px, py, pill_w, pill_h, pill_h / 2.0, style="DF", border_opacity=0.65)
    _spark(pdf, px + 8, py + pill_h / 2.0, 2.5, GOLD)
    _spark(pdf, px + pill_w - 8, py + pill_h / 2.0, 2.5, GOLD)
    pdf.set_xy(px + 12, py)
    pdf.set_text_color(*GOLD)
    with pdf.local_context(char_spacing=0.5):
        pdf.cell(pill_w - 24, pill_h, safe(line), align="C")

    # Spruch, sauber in Zeilen gesetzt (nicht abgeschnitten)
    pdf.set_xy(MX, 202)
    pdf.set_font("Cormo", "I", 15)
    pdf.set_text_color(*INK_L)
    pdf.multi_cell(PW - 2 * MX, 7.4,
                   safe("Du musst nichts an dir reparieren.\n"
                        "Auf den nächsten Seiten liest du nur noch,\nwie du gemeint bist."),
                   align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Sternen-Abschluss als Bindeglied zur letzten Seite
    _signoff(pdf, 242.0)

    # Wortmarke ganz unten, wie auf den anderen Seiten
    pdf.set_xy(0, 258)
    pdf.set_font("Vibes", "", 26)
    pdf.set_text_color(*GOLD)
    pdf.cell(PW, 10, safe("Intuition mit Herz"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _factrow(pdf, teaser, hd, y):
    """Drei goldgerahmte Kernfakten nebeneinander (Typ, Autorität, Profil)."""
    cw = PW - pdf.l_margin - pdf.r_margin
    gap = 6.0
    fw = (cw - 2 * gap) / 3.0
    fh = 20.0
    facts = [("Typ", hd.get("type_display") or hd.get("type") or teaser.get("type") or ""),
             ("Autorität", (hd.get("authority") or teaser.get("authority") or "")
              .replace(" Autorität", "").replace("Emotionale", "Emotional")),
             ("Profil", hd.get("profile") or teaser.get("profile") or "")]
    for i, (lab, val) in enumerate(facts):
        x = pdf.l_margin + i * (fw + gap)
        pdf.set_fill_color(*CARD)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.3)
        _round_rect(pdf, x, y, fw, fh, 3.5, style="DF", border_opacity=0.34)
        pdf.set_xy(x, y + 4)
        pdf.set_font("Mul", "", 7.5)
        pdf.set_text_color(*INK_SOFT)
        with pdf.local_context(char_spacing=0.8):
            pdf.cell(fw, 4, safe(lab.upper()), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(x + 2, y + 9)
        pdf.set_font("Cormo", "", 15)
        pdf.set_text_color(*GOLD)
        pdf.multi_cell(fw - 4, 6.5, safe(val), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    return y + fh


def _uebersicht(pdf, teaser, full):
    """Reiter 1: die ganze Uebersicht auf einem Blatt (Kernfakten + beide
    Abbildungen nebeneinander), danach die zwei aufgeklappten Felder
    'Was bedeutet was?' und die zwoelf Haeuser."""
    hd = full.get("hd", {})
    geo = full.get("geo")
    name = full.get("name") or ""
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Übersicht", "Auf einen Blick", on_dark=True)
    _para(pdf, (name + ", " if name else "") +
          "was du gleich liest, ist kein Test und kein Urteil. Es ist ein Blick auf das, "
          "was in dir angelegt ist, seit dem ersten Moment deines Lebens. Prüfe beim Lesen "
          "immer selbst, was sich stimmig anfühlt. Was nicht passt, darfst du liegen lassen.",
          font="Mul", size=10, color=INK_SOFT, h=5.8, after=5)

    y = _factrow(pdf, teaser, hd, pdf.get_y() + 1)
    y += 8

    # Zwei Panels nebeneinander: links Natalchart-Rad, rechts Bodygraph
    cw = PW - pdf.l_margin - pdf.r_margin
    gap = 8.0
    col = (cw - gap) / 2.0
    ph = 118.0
    lx = pdf.l_margin
    rx = pdf.l_margin + col + gap
    for x in (lx, rx):
        pdf.set_fill_color(*CARD)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.3)
        _round_rect(pdf, x, y, col, ph, 4.0, style="DF", border_opacity=0.24)

    # Panel-Titel
    for x, cap in ((lx, "Natalchart"), (rx, "Human Design")):
        pdf.set_xy(x, y + 6)
        pdf.set_font("Mul", "", 8)
        pdf.set_text_color(*GOLD)
        with pdf.local_context(char_spacing=1.4):
            pdf.cell(col, 4, safe(cap.upper()), align="C")

    # linkes Panel: Rad + Schluesselwerte
    if geo:
        dia = col - 16
        _draw_wheel(pdf, geo, lx + (col - dia) / 2.0, y + 14, dia)
        by = {p["key"]: p for p in full.get("positions", [])}

        def qv(k):
            p = by.get(k)
            return (p["sign"] + " " + p["deg"]) if p else "…"
        ky = y + 14 + dia + 3
        for lab, k in (("Sonne", "Sonne"), ("Mond", "Mond"),
                       ("Aszendent", "AC"), ("Deszendent", "DC")):
            pdf.set_xy(lx + 6, ky)
            pdf.set_font("Mul", "", 7.5)
            pdf.set_text_color(*INK_SOFT)
            pdf.cell(col * 0.42, 5, safe(lab.upper()))
            pdf.set_xy(lx + col * 0.42, ky)
            pdf.set_font("Cormo", "", 12)
            pdf.set_text_color(*LILAC)
            pdf.cell(col * 0.58 - 6, 5, safe(qv(k)), align="R")
            ky += 6
    else:
        pdf.set_xy(lx + 6, y + ph / 2 - 8)
        pdf.set_font("Cormo", "I", 11)
        pdf.set_text_color(*INK_SOFT)
        pdf.multi_cell(col - 12, 5.4, safe("Für das Rad brauchen wir deine Geburtszeit."),
                       align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # rechtes Panel: Bodygraph + Legende
    bth = ph - 34
    bw = (260.0 / 452.0) * bth
    _draw_bodygraph(pdf, hd, rx + (col - bw) / 2.0, y + 14, bth)
    ly = y + ph - 12
    pdf.set_fill_color(*GOLD)
    pdf.rect(rx + col / 2 - 26, ly, 2.6, 2.6, style="F")
    _ctext(pdf, rx + col / 2 - 15, ly + 1.3, "definiert", 7.5, INK_SOFT)
    pdf.set_draw_color(*INK_SOFT)
    pdf.set_line_width(0.3)
    pdf.rect(rx + col / 2 + 6, ly, 2.6, 2.6, style="D")
    _ctext(pdf, rx + col / 2 + 17, ly + 1.3, "offen", 7.5, INK_SOFT)

    pdf.set_y(y + ph)

    # ── aufgeklappte Felder auf hellen Seiten ──
    pdf.theme = "dark"
    pdf.add_page()
    _fold_head(pdf, "Was bedeutet was?")
    _para(pdf, "Hier findest du die wichtigsten Begriffe aus deinem Bauplan in einfachen "
               "Worten. So kannst du jederzeit nachschauen.",
          size=10, color=BODY_DK, h=5.7, after=4)
    for term, desc in LEGEND:
        _keep(pdf, 15)
        pdf.set_font("Cormo", "B", 14)
        pdf.set_text_color(*GOLD)
        pdf.multi_cell(0, 6.2, safe(term), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Mul", "", 10)
        pdf.set_text_color(*BODY_DK)
        pdf.multi_cell(0, 5.6, safe(desc), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
        pdf.ln(3.5)

    # Passt das Häuser-Feld nicht mehr drauf, den Rest zart fuellen statt leer lassen
    if not _break_with_accent(pdf, 46):
        pdf.ln(2)
    _fold_head(pdf, "Die zwölf Häuser, deine Lebensfelder")
    _para(pdf, "Die Häuser zeigen, in welchem Lebensbereich sich ein Planet entfaltet. "
               "So kannst du jede Position in deinem Natalchart einordnen.",
          size=10, color=BODY_DK, h=5.7, after=4)
    for h in full.get("houses", []):
        _keep(pdf, 13)
        y0 = pdf.get_y()
        pdf.set_font("Mul", "B", 9)
        pdf.set_text_color(*GOLD_DK)
        pdf.set_xy(pdf.l_margin, y0 + 0.6)
        pdf.cell(9, 6, str(h.get("nr", "")))
        pdf.set_xy(pdf.l_margin + 9, y0)
        pdf.set_font("Cormo", "B", 13)
        pdf.set_text_color(*INK_DARK)
        pdf.cell(0, 6, safe("Haus " + str(h.get("nr", "")) + ", " + str(h.get("title") or "")),
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(pdf.l_margin + 9, pdf.get_y())
        pdf.set_font("Mul", "", 9.5)
        pdf.set_text_color(*BODY_DK)
        pdf.multi_cell(PW - pdf.l_margin - pdf.r_margin - 9, 5.2, safe(h.get("meaning") or ""),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2.5)
    _page_tail_accent(pdf)


def _fold_head(pdf, title):
    """Kopf eines aufgeklappten Felds (wie ein geoeffneter Reiter)."""
    _keep(pdf, 20)
    x = pdf.l_margin
    w = PW - pdf.l_margin - pdf.r_margin
    y = pdf.get_y()
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.3)
    _round_rect(pdf, x, y, w, 12, 3, style="DF", border_opacity=0.5)
    pdf.set_fill_color(*GOLD2)
    pdf.rect(x, y, 1.6, 12, style="F")
    pdf.set_xy(x + 8, y)
    pdf.set_font("Cormo", "B", 15)
    pdf.set_text_color(*INK_L)
    pdf.cell(w - 26, 12, safe(title))
    pdf.set_font("Mul", "", 16)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(x + w - 14, y)
    pdf.cell(10, 12, "+", align="C")
    pdf.set_y(y + 12 + 4)


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
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.3)
    _round_rect(pdf, x, top, w, box_h, 3, style="DF", border_opacity=0.45)
    pdf.set_fill_color(*GOLD2)
    pdf.rect(x, top, 1.6, box_h, style="F")
    pdf.set_xy(x + 8, top + 8)
    _eyebrow(pdf, "Merksatz", GOLD, size=7.5, spacing=1.1)
    pdf.set_xy(x + 8, pdf.get_y() + 2)
    pdf.set_font("Cormo", "I", 14)
    pdf.set_text_color(*INK_L)
    pdf.multi_cell(inner, 6.4, safe(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_y(top + box_h)
    pdf.ln(3)


def _unit(pdf, title, meta, oneliner, body):
    """Ein gerahmter Inhaltsblock (wie eine aufgeklappte Karte eines Reiters):
    Fliederrahmen, goldener Akzent, Titel, Meta, Kurzzeile und Text."""
    x = pdf.l_margin
    w = PW - pdf.l_margin - pdf.r_margin
    pad = 6.5
    iw = w - 2 * pad - 2
    # Hoehe vormessen
    ol_lines = []
    if oneliner:
        pdf.set_font("Cormo", "I", 12)
        ol_lines = pdf.multi_cell(iw, 5.6, safe(oneliner), dry_run=True, output="LINES")
    bd_lines = []
    if body:
        pdf.set_font("Mul", "", 10.3)
        bd_lines = pdf.multi_cell(iw, 5.7, safe(body), dry_run=True, output="LINES")
    h_title = 8.0
    h_meta = 5.0 if meta else 0.0
    h_ol = (5.6 * len(ol_lines) + 2.0) if ol_lines else 0.0
    h_bd = 5.7 * len(bd_lines)
    box_h = pad + h_title + h_meta + h_ol + h_bd + pad - 1
    # Passt die Karte nicht mehr auf die Seite? Dann vorher den Rest mit einem
    # zarten Akzent fuellen, damit keine grosse Leere entsteht.
    _break_with_accent(pdf, box_h + 6)
    top = pdf.get_y()
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*LILAC)
    pdf.set_line_width(0.3)
    _round_rect(pdf, x, top, w, box_h, 3.5, style="DF", border_opacity=0.32)
    pdf.set_fill_color(*GOLD2)
    pdf.rect(x, top, 1.4, box_h, style="F")
    ty = top + pad
    pdf.set_xy(x + pad, ty)
    pdf.set_font("Cormo", "", 19)
    pdf.set_text_color(*INK_L)
    pdf.cell(iw, h_title, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    yy = ty + h_title
    if meta:
        pdf.set_xy(x + pad, yy)
        pdf.set_font("Mul", "", 9)
        pdf.set_text_color(*MUTE)
        with pdf.local_context(char_spacing=0.4):
            pdf.cell(iw, h_meta, safe(meta))
        yy += h_meta
    if oneliner:
        pdf.set_xy(x + pad, yy)
        pdf.set_font("Cormo", "I", 12)
        pdf.set_text_color(*GOLD)
        pdf.multi_cell(iw, 5.6, safe(oneliner), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        yy = pdf.get_y() + 2
    if body:
        pdf.set_xy(x + pad, yy)
        pdf.set_font("Mul", "", 10.3)
        pdf.set_text_color(*BODY_DK)
        pdf.multi_cell(iw, 5.7, safe(body), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
    pdf.set_y(top + box_h)
    pdf.ln(4)


def _dblock(pdf, kicker, label, title, parts):
    """Eine Schwierigkeit im Vier-Schritt-Aufbau: gerahmte Karte mit Kicker,
    Titel und je Schritt einer goldenen Marke plus Text."""
    x = pdf.l_margin
    w = PW - pdf.l_margin - pdf.r_margin
    pad = 6.5
    iw = w - 2 * pad - 2
    h_lbl, h_txt, gap = 4.8, 5.7, 3.0

    # Hoehe vormessen
    gemessen = []
    for lbl, txt in parts:
        pdf.set_font("Mul", "", 10.3)
        zeilen = pdf.multi_cell(iw, h_txt, safe(txt), dry_run=True, output="LINES")
        gemessen.append((lbl, txt, len(zeilen)))
    h_kick = 5.0 if (kicker or label) else 0.0
    h_titel = 8.0 + 2.5   # etwas Luft zwischen Titel und der ersten Marke
    box_h = pad + h_titel + h_kick + sum(h_lbl + h_txt * n + gap for _, _, n in gemessen) + pad - gap

    if box_h > 225:   # Notbremse: passt nicht auf eine Seite, dann ohne Rahmen
        _eyebrow(pdf, safe(((kicker + ": ") if kicker else "") + (label or "")), MUTE, size=8)
        pdf.ln(1)
        pdf.set_font("Cormo", "", 19)
        pdf.set_text_color(*INK_L)
        pdf.multi_cell(0, 8, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        for lbl, txt, _n in gemessen:
            _eyebrow(pdf, safe(lbl), GOLD, size=7.5)
            _para(pdf, txt, size=10.3, color=BODY_DK, h=h_txt, after=2.5)
        pdf.ln(3)
        return

    _break_with_accent(pdf, box_h + 6)
    top = pdf.get_y()
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*LILAC)
    pdf.set_line_width(0.3)
    _round_rect(pdf, x, top, w, box_h, 3.5, style="DF", border_opacity=0.32)
    pdf.set_fill_color(*GOLD2)
    pdf.rect(x, top, 1.4, box_h, style="F")

    yy = top + pad
    if h_kick:
        pdf.set_xy(x + pad, yy)
        pdf.set_font("Mul", "", 8)
        pdf.set_text_color(*LILAC)
        with pdf.local_context(char_spacing=0.9):
            pdf.cell(iw, h_kick, safe((((kicker + ": ") if kicker else "") + (label or "")).upper()))
        yy += h_kick
    pdf.set_xy(x + pad, yy)
    pdf.set_font("Cormo", "", 19)
    pdf.set_text_color(*INK_L)
    pdf.cell(iw, 8.0, safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    yy += h_titel
    for lbl, txt, _n in gemessen:
        pdf.set_xy(x + pad, yy)
        pdf.set_font("Mul", "B", 7.5)
        pdf.set_text_color(*GOLD)
        with pdf.local_context(char_spacing=0.9):
            pdf.cell(iw, h_lbl, safe(str(lbl).upper()))
        yy += h_lbl
        pdf.set_xy(x + pad, yy)
        pdf.set_font("Mul", "", 10.3)
        pdf.set_text_color(*BODY_DK)
        pdf.multi_cell(iw, h_txt, safe(txt), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="J")
        yy = pdf.get_y() + gap
    pdf.set_y(top + box_h)
    pdf.ln(4)


def _simple_chapter_head(pdf, eyebrow, title, intro=None):
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, eyebrow, title, on_dark=True)
    pdf.ln(1)
    if intro:
        _para(pdf, intro, size=10.5, color=BODY_DK, h=6, after=5)


# ---------- Abbildungen (Rad + Bodygraph, wie auf der Website) ----------

def _ctext(pdf, cx, cy, s, size, color, font="Mul", style=""):
    """Text horizontal auf cx zentriert, vertikal auf cy mittig."""
    s = safe(s)
    if not s:
        return
    pdf.set_font(font, style, size)
    pdf.set_text_color(*color)
    w = pdf.get_string_width(s)
    h = size * 0.3528 * 1.25
    pdf.set_xy(cx - w / 2.0, cy - h / 2.0)
    pdf.cell(w, h, s, align="C")


def _glyph(pdf, cx, cy, ch, size, color):
    """Ein echtes Astrosymbol (Planet oder Zeichen) aus der Symbol-Schrift,
    mittig auf (cx, cy). Laeuft NICHT durch safe(), sonst wuerde es entfernt."""
    if not ch:
        return
    pdf.set_font("Astro", "", size)
    pdf.set_text_color(*color)
    w = pdf.get_string_width(ch)
    h = size * 0.3528 * 1.3
    pdf.set_xy(cx - w / 2.0, cy - h / 2.0)
    pdf.cell(w, h, ch, align="C")


def _draw_bodygraph(pdf, hd, ox, oy, target_h):
    """Human-Design-Bodygraph als Vektorgrafik, exakt nach den definierten
    Zentren und aktiven Kanaelen. Portiert aus buildBodygraph der Website."""
    VW, VH = 260.0, 452.0
    k = target_h / VH
    C = {"Kopf": (130, 36), "Ajna": (130, 110), "Kehle": (130, 186), "G": (130, 262),
         "Herz": (196, 230), "Milz": (40, 300), "Solarplexus": (220, 300),
         "Sakral": (130, 340), "Wurzel": (130, 416)}
    SIZE = {"Kopf": 16, "Ajna": 16, "Kehle": 17, "G": 18, "Herz": 12, "Milz": 16,
            "Solarplexus": 16, "Sakral": 17, "Wurzel": 17}
    SHAPE = {"Kopf": "td", "Ajna": "tu", "Kehle": "sq", "G": "di", "Herz": "td",
             "Milz": "tr", "Solarplexus": "tl", "Sakral": "sq", "Wurzel": "sq"}
    LABEL = {"Kopf": "Kopf", "Ajna": "Ajna", "Kehle": "Kehle", "G": "G", "Herz": "Herz",
             "Milz": "Milz", "Solarplexus": "Solar", "Sakral": "Sakral", "Wurzel": "Wurzel"}
    SKEL = [("Kopf", "Ajna"), ("Ajna", "Kehle"), ("Kehle", "G"), ("Kehle", "Herz"),
            ("Kehle", "Sakral"), ("Kehle", "Milz"), ("Kehle", "Solarplexus"),
            ("G", "Sakral"), ("G", "Herz"), ("G", "Milz"), ("Herz", "Milz"),
            ("Herz", "Solarplexus"), ("Sakral", "Milz"), ("Sakral", "Solarplexus"),
            ("Sakral", "Wurzel"), ("Milz", "Wurzel"), ("Solarplexus", "Wurzel")]

    def pg(c):
        x, y = C[c]
        return (ox + x * k, oy + y * k)

    def shape_pts(t, cx, cy, s):
        if t == "sq":
            p = [(cx - s, cy - s), (cx + s, cy - s), (cx + s, cy + s), (cx - s, cy + s)]
        elif t == "di":
            p = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
        elif t == "tu":
            p = [(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s)]
        elif t == "td":
            p = [(cx, cy + s), (cx + s, cy - s), (cx - s, cy - s)]
        elif t == "tr":
            p = [(cx - s, cy - s), (cx + s, cy), (cx - s, cy + s)]
        else:  # tl
            p = [(cx + s, cy - s), (cx - s, cy), (cx + s, cy + s)]
        return [(ox + px * k, oy + py * k) for px, py in p]

    defset = set(hd.get("defined_centers", []))
    # Skelett (feine Verbindungen)
    pdf.set_draw_color(*LINE_DARK)
    pdf.set_line_width(max(0.2, 2 * k))
    for a, b in SKEL:
        pa, pb = pg(a), pg(b)
        pdf.line(pa[0], pa[1], pb[0], pb[1])
    # aktive Kanaele (gold, kraeftig)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(max(0.5, 4.5 * k))
    for e in hd.get("center_links", []):
        if len(e) >= 2 and e[0] in C and e[1] in C:
            pa, pb = pg(e[0]), pg(e[1])
            pdf.line(pa[0], pa[1], pb[0], pb[1])
    # Zentren
    for c, (x, y) in C.items():
        on = c in defset
        pts = shape_pts(SHAPE[c], x, y, SIZE[c])
        if on:
            pdf.set_fill_color(*GOLD)
            pdf.set_draw_color(*GOLD)
            pdf.set_line_width(max(0.2, 1 * k))
            pdf.polygon(pts, style="DF")
        else:
            pdf.set_draw_color(*INK_SOFT)
            pdf.set_line_width(max(0.25, 1.4 * k))
            pdf.polygon(pts, style="D")
        ly = oy + (y + SIZE[c]) * k + 5.6
        _ctext(pdf, ox + x * k, ly, LABEL[c], 7.5, GOLD if on else INK_SOFT, style="")


def _draw_wheel(pdf, geo, ox, oy, dia):
    """Natal-Rad (Horoskop) als Vektorgrafik, exakt aus den ekliptikalen
    Laengen. Portiert aus buildNatalWheel der Website; Astro-Glyphen als Kuerzel."""
    VW = 360.0
    k = dia / VW
    asc = geo["asc"]
    R1, R2, R4 = 160.0, 131.0, 52.0

    def P(r, L):
        a = math.radians(180 + (L - asc))
        return (ox + (180 + r * math.cos(a)) * k, oy + (180 - r * math.sin(a)) * k)

    def circle(r, col, op, w=1.0):
        cx, cy = ox + 180 * k, oy + 180 * k
        pr = r * k
        pdf.set_draw_color(*col)
        pdf.set_line_width(max(0.15, w * k))
        if op < 1.0:
            with pdf.local_context(stroke_opacity=op):
                pdf.ellipse(cx - pr, cy - pr, 2 * pr, 2 * pr, style="D")
        else:
            pdf.ellipse(cx - pr, cy - pr, 2 * pr, 2 * pr, style="D")

    circle(R1, GOLD, 0.6)
    circle(R2, GOLD, 0.3)
    circle(R4, LINE_DARK, 1.0)
    # 12 Zeichen-Speichen + Zeichenkuerzel + Hausnummern
    sign_start = math.floor(asc / 30.0) * 30
    pdf.set_draw_color(*LINE_DARK)
    pdf.set_line_width(max(0.15, 1 * k))
    for i in range(12):
        Lc = sign_start + 30 * i
        a, b = P(R4, Lc), P(R1, Lc)
        with pdf.local_context(stroke_opacity=0.55):
            pdf.line(a[0], a[1], b[0], b[1])
        si = (round(sign_start / 30) + i) % 12
        gp = P((R1 + R2) / 2, Lc + 15)
        _glyph(pdf, gp[0], gp[1], SIGN_GLYPH[si], 12, GOLD)
        hn = P(R4 + 13, Lc + 15)
        _ctext(pdf, hn[0], hn[1], str(i + 1), 7, LILAC, style="")

    def axis(L1, L2, l1, l2, col):
        a, b = P(R1, L1), P(R1, L2)
        pdf.set_draw_color(*col)
        pdf.set_line_width(max(0.2, 1.3 * k))
        with pdf.local_context(stroke_opacity=0.85):
            pdf.line(a[0], a[1], b[0], b[1])
        t1, t2 = P(R1 + 12, L1), P(R1 + 12, L2)
        _ctext(pdf, t1[0], t1[1], l1, 8.5, col, style="B")
        _ctext(pdf, t2[0], t2[1], l2, 8.5, col, style="B")

    axis(geo["asc"], geo["dc"], "AC", "DC", LILAC)
    axis(geo["mc"], geo["ic"], "MC", "IC", GOLD)
    # Planeten mit einfacher Kollisionsvermeidung
    placed = []
    for p in sorted(geo.get("planets", []), key=lambda x: x["lon"]):
        r, guard = 98.0, 0
        while guard < 8:
            clash = False
            for q in placed:
                dl = abs(((p["lon"] - q["lon"] + 180) % 360) - 180)
                if dl < 8 and abs(q["r"] - r) < 12:
                    clash = True
                    break
            if not clash:
                break
            r -= 13
            guard += 1
        placed.append({"lon": p["lon"], "r": r})
        t1, t2 = P(R2, p["lon"]), P(R2 - 6, p["lon"])
        pdf.set_draw_color(*INK_SOFT)
        pdf.set_line_width(max(0.15, 1 * k))
        pdf.line(t1[0], t1[1], t2[0], t2[1])
        g = P(r, p["lon"])
        gl = PLANET_GLYPH.get(p.get("name", ""))
        if gl:
            _glyph(pdf, g[0], g[1], gl, 12.5, INK_L)
        else:
            _ctext(pdf, g[0], g[1],
                   PLANET_ABBR.get(p.get("name", ""), (p.get("name", "") or "")[:2]),
                   8.5, INK_L, style="B")


def _kvrow_dark(pdf, k, v):
    """Zeile Schluessel/Wert auf dunkel, mit feiner Trennlinie (wie kv auf der Seite)."""
    if not v:
        return
    cw = PW - pdf.l_margin - pdf.r_margin
    y0 = pdf.get_y()
    pdf.set_font("Mul", "", 10)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(cw * 0.4, 8, safe(k))
    pdf.set_xy(pdf.l_margin + cw * 0.4, y0)
    pdf.set_font("Cormo", "", 15)
    pdf.set_text_color(*INK_L)
    pdf.multi_cell(cw * 0.6, 8, safe(v), align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    with pdf.local_context(stroke_opacity=0.18):
        pdf.set_draw_color(*LILAC)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y() + 0.6, PW - pdf.r_margin, pdf.get_y() + 0.6)
    pdf.ln(2.4)


def _human_design(pdf, teaser, full):
    """Reiter Human Design: Bodygraph gross, Kernfakten und die neun Zentren."""
    hd = full.get("hd", {})
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Reiter", "Human Design", on_dark=True)
    th = 118.0
    ox = (PW - (260.0 / 452.0) * th) / 2.0
    oy = pdf.get_y() + 1
    _draw_bodygraph(pdf, hd, ox, oy, th)
    pdf.set_y(oy + th + 6)
    cx = PW / 2.0
    yy = pdf.get_y()
    pdf.set_fill_color(*GOLD)
    pdf.rect(cx - 38, yy, 2.8, 2.8, style="F")
    _ctext(pdf, cx - 26, yy + 1.4, "definiert", 8.5, INK_SOFT)
    pdf.set_draw_color(*INK_SOFT)
    pdf.set_line_width(0.3)
    pdf.rect(cx + 8, yy, 2.8, 2.8, style="D")
    _ctext(pdf, cx + 20, yy + 1.4, "offen", 8.5, INK_SOFT)
    pdf.ln(9)
    cross = hd.get("incarnation_cross")
    _kvrow_dark(pdf, "Typ", hd.get("type_display") or hd.get("type"))
    _kvrow_dark(pdf, "Strategie", teaser.get("strategy"))
    _kvrow_dark(pdf, "Autorität", hd.get("authority"))
    prof = str(hd.get("profile") or "")
    if teaser.get("profile_name"):
        prof = (prof + ", " + str(teaser["profile_name"])).strip(", ")
    _kvrow_dark(pdf, "Profil", prof)
    _kvrow_dark(pdf, "Definition", hd.get("definition"))
    if cross:
        _kvrow_dark(pdf, "Inkarnationskreuz",
                    "%s/%s, %s/%s" % (cross.get("pers_sun"), cross.get("pers_earth"),
                                      cross.get("des_sun"), cross.get("des_earth")))
    _page_tail_accent(pdf)

    # Die neun Zentren auf hellen Seiten
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Human Design", "Deine neun Energiezentren", on_dark=True)
    _para(pdf, "Jedes Zentrum ist entweder definiert oder offen. Definiert heißt: hier "
               "bist du dir treu, diese Energie ist immer verlässlich da. Offen heißt: "
               "hier bist du feinfühlig, formbar und lernst ein Leben lang. Beides ist "
               "wertvoll.", size=10.5, color=BODY_DK, h=5.9, after=3)
    for c in full.get("hd_centers", []):
        state = "definiert" if c.get("defined") else "offen"
        body = str(c.get("detail") or "")
        if c.get("defined") and c.get("gift"):
            body += ("\n" if body else "") + "Deine Gabe hier: " + str(c["gift"]) + "."
        if (not c.get("defined")) and c.get("tip"):
            body += ("\n" if body else "") + "Impuls: " + str(c["tip"])
        _unit(pdf, str(c.get("name") or ""), state,
              c.get("theme") or c.get("meaning"), body)
    _page_tail_accent(pdf)


def _natalchart(pdf, full):
    """Reiter Natalchart: Horoskop-Rad gross und alle Positionen im Detail."""
    geo = full.get("geo")
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Reiter", "Natalchart", on_dark=True)
    if geo:
        dia = 122.0
        oy = pdf.get_y() + 1
        _draw_wheel(pdf, geo, (PW - dia) / 2.0, oy, dia)
        pdf.set_y(oy + dia + 5)
        by = {p["key"]: p for p in full.get("positions", [])}

        def qv(k):
            p = by.get(k)
            return (p["sign"] + " " + p["deg"]) if p else "…"
        # Eine Leerzeile unter dem Rad, dann die Werte untereinander in
        # einer zentrierten Karte.
        pdf.ln(6)
        rows = [("Sonne", qv("Sonne")), ("Mond", qv("Mond")),
                ("Aszendent", qv("AC")), ("Deszendent", qv("DC"))]
        card_w = 122.0
        card_x = (PW - card_w) / 2.0
        pad = 8.0
        row_h = 11.0
        card_h = pad * 2 + row_h * len(rows)
        cyc = pdf.get_y()
        pdf.set_fill_color(*CARD)
        pdf.set_draw_color(*LILAC)
        pdf.set_line_width(0.3)
        _round_rect(pdf, card_x, cyc, card_w, card_h, 4.0, style="DF", border_opacity=0.32)
        pdf.set_fill_color(*GOLD2)
        pdf.rect(card_x, cyc, 1.4, card_h, style="F")
        for i, (lab, val) in enumerate(rows):
            ry = cyc + pad + i * row_h
            pdf.set_xy(card_x + pad + 2, ry)
            pdf.set_font("Mul", "", 8.5)
            pdf.set_text_color(*INK_SOFT)
            with pdf.local_context(char_spacing=0.6):
                pdf.cell(card_w * 0.42, row_h - 4, safe(lab.upper()))
            pdf.set_xy(card_x + card_w * 0.42, ry)
            pdf.set_font("Cormo", "", 15)
            pdf.set_text_color(*LILAC)
            pdf.cell(card_w * 0.58 - pad - 2, row_h - 4, safe(val), align="R")
            if i < len(rows) - 1:
                with pdf.local_context(stroke_opacity=0.18):
                    pdf.set_draw_color(*LILAC)
                    pdf.set_line_width(0.2)
                    pdf.line(card_x + pad, ry + row_h - 2, card_x + card_w - pad, ry + row_h - 2)
        pdf.set_y(cyc + card_h)
    else:
        _para(pdf, "Für das Horoskop-Rad brauchen wir deine Geburtszeit. Die Positionen "
                   "von Sonne, Mond und den Planeten liest du trotzdem gleich.",
              font="Cormo", style="I", size=13, color=GOLD, h=6.4, after=4, align="C")
    _page_tail_accent(pdf)

    # Positionen auf hellen Seiten
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Natalchart", "Deine Positionen im Detail", on_dark=True)
    _para(pdf, "Jeder Planet steht für einen Bereich deines Lebens. Zeichen und Haus "
               "sagen, wie und wo er sich zeigt. Beim Haus zeigen wir Ganzzeichen und "
               "Placidus; die ausführliche Deutung folgt den Ganzzeichen-Häusern.",
          size=10.5, color=BODY_DK, h=5.9, after=3)
    for p in full.get("positions", []):
        sign = str(p.get("sign") or "")
        deg = str(p.get("deg") or "")
        house = p.get("house")
        hpl = p.get("house_pl", house)
        meta = ", ".join(x for x in [sign, deg] if x)
        if house:
            if hpl and hpl != house:
                meta += ", Ganzzeichen H%s / Placidus H%s" % (house, hpl)
            else:
                meta += ", " + str(house) + ". Haus"
        _unit(pdf, str(p.get("label") or p.get("key") or ""), meta,
              p.get("meaning"), p.get("desc"))
    _page_tail_accent(pdf)


# ---------- Inhaltsverzeichnis ----------

def _toc_page(pdf, entries):
    """Eine dunkle Seite, die alle Kapitel mit Seitenzahl auflistet."""
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Übersicht", "Inhalt", on_dark=True)
    _para(pdf, "Dein Bauplan, Kapitel für Kapitel. Blättere in Ruhe, du musst nichts "
               "auf einmal lesen.", font="Mul", size=11, color=INK_SOFT, h=6.4, after=8)
    if not entries:
        return
    x = pdf.l_margin
    w = PW - pdf.l_margin - pdf.r_margin
    for nr, title, page in entries:
        y = pdf.get_y()
        pdf.set_font("Mul", "B", 10)
        pdf.set_text_color(*GOLD)
        with pdf.local_context(char_spacing=0.6):
            pdf.set_xy(x, y + 1)
            pdf.cell(13, 8, safe(nr))
        pdf.set_font("Cormo", "", 17)
        pdf.set_text_color(*INK_L)
        pdf.set_xy(x + 13, y)
        pdf.cell(w - 13 - 12, 9, safe(title))
        pdf.set_font("Mul", "", 11)
        pdf.set_text_color(*INK_SOFT)
        pdf.set_xy(PW - pdf.r_margin - 12, y + 1)
        pdf.cell(12, 8, str(page), align="R")
        # feine Punktlinie
        with pdf.local_context(stroke_opacity=0.18):
            pdf.set_draw_color(*LILAC)
            pdf.set_line_width(0.2)
            pdf.line(x, y + 11.5, PW - pdf.r_margin, y + 11.5)
        pdf.set_y(y + 13.5)
    _page_tail_accent(pdf, min_remaining=40)


# ---------- Intuitionstyp ----------

def _intuition(pdf, it):
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Intuitionstyp", "Dein Intuitionstyp", on_dark=True)
    # Element-Medaillon zentriert
    s = 15.0
    ey = pdf.get_y() + 20
    _element_symbol(pdf, PW / 2.0, ey, s, it.get("key"))
    pdf.set_y(ey + s * 0.95 + 6)
    if it.get("archetype"):
        pdf.set_font("Cormo", "", 25)
        pdf.set_text_color(*GOLD)
        pdf.cell(0, 10, safe(it["archetype"]), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    sub = " · ".join(x for x in [it.get("tagline"),
                                 ("Mond in " + it["moon_sign"]) if it.get("moon_sign") else ""] if x)
    if sub:
        pdf.set_font("Cormo", "I", 13)
        pdf.set_text_color(*INK_SOFT)
        pdf.cell(0, 6, safe(sub), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)
    _para(pdf, it.get("text"), size=10.5, color=BODY_DK, h=5.9, after=4)
    depth = it.get("depth")
    if depth and depth.get("summary"):
        _keep(pdf, 24)
        pdf.ln(1)
        _eyebrow(pdf, "Deine intuitive Ausprägung: " + str(depth.get("level", "")),
                 MUTE, size=8, spacing=1.0)
        pdf.ln(2)
        _para(pdf, depth.get("summary"), font="Cormo", style="I", size=13,
              color=GOLD_DK, h=6.4, after=4)
        if depth.get("caveat"):
            _para(pdf, depth["caveat"], size=10.5, color=BODY_DK, h=5.9, after=4)
        for fc in depth.get("facets", []):
            _unit(pdf, fc.get("title") or "", "", None, fc.get("text") or "")
    if it.get("tools"):
        _keep(pdf, 24)
        pdf.ln(1)
        pdf.set_draw_color(*LINE_CREAM)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), PW - pdf.r_margin, pdf.get_y())
        pdf.ln(4)
        _eyebrow(pdf, "Deine Werkzeuge", MUTE, size=8, spacing=1.0)
        pdf.ln(3)
        for tool in it["tools"]:
            _keep(pdf, 14)
            y0 = pdf.get_y()
            pdf.set_font("Cormo", "", 15)
            pdf.set_text_color(*GOLD_DK)
            pdf.set_xy(pdf.l_margin, y0)
            pdf.cell(7, 6, safe("✦" if "✦" in _supported() else "·"))
            pdf.set_xy(pdf.l_margin + 7, y0)
            pdf.set_font("Mul", "", 10.5)
            pdf.set_text_color(*BODY_DK)
            pdf.multi_cell(PW - pdf.l_margin - pdf.r_margin - 7, 5.9, safe(tool),
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2.5)
    # Galerie der vier Intuitionstypen, jeweils mit Element-Symbol
    types = it.get("all") or []
    if types:
        _keep(pdf, 70)
        pdf.ln(2)
        _eyebrow(pdf, "Die vier Intuitionstypen", MUTE, size=8, spacing=1.0)
        pdf.ln(4)
        cw = PW - pdf.l_margin - pdf.r_margin
        gap = 8.0
        col = (cw - gap) / 2.0
        ch = 46.0
        for idx, a in enumerate(types):
            row, ccol = divmod(idx, 2)
            cxp = pdf.l_margin + ccol * (col + gap)
            cyp = pdf.get_y() if ccol == 0 else cyp_row
            if ccol == 0:
                cyp_row = cyp
            active = a.get("key") == it.get("key")
            pdf.set_fill_color(*CARD)
            pdf.set_draw_color(*(GOLD if active else LILAC))
            pdf.set_line_width(0.4 if active else 0.3)
            _round_rect(pdf, cxp, cyp_row, col, ch, 3.5, style="DF",
                        border_opacity=0.55 if active else 0.28)
            _element_symbol(pdf, cxp + col / 2.0, cyp_row + 12, 6.2, a.get("key"))
            pdf.set_xy(cxp, cyp_row + 22)
            pdf.set_font("Cormo", "", 14)
            pdf.set_text_color(*(GOLD if active else INK_L))
            pdf.cell(col, 6, safe(a.get("archetype") or ""), align="C",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_xy(cxp + 4, cyp_row + 28)
            pdf.set_font("Mul", "", 8)
            pdf.set_text_color(*INK_SOFT)
            pdf.multi_cell(col - 8, 4.4, safe(a.get("oneliner") or a.get("tagline") or ""),
                           align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if ccol == 1 or idx == len(types) - 1:
                pdf.set_y(cyp_row + ch + gap)
    if it.get("note"):
        pdf.ln(1)
        _para(pdf, it["note"], size=8.5, color=MUTE, h=4.6, after=0)
    _page_tail_accent(pdf)


# ---------- Deutung als ein Kapitel mit aufgeklappten Abschnitten ----------

def _deutung(pdf, sections):
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Deutung", "Deine Deutung", on_dark=True)
    _para(pdf, "Hier ist alles in Klartext für dich gedeutet, ein Abschnitt nach dem "
               "anderen. Prüfe beim Lesen immer selbst, was sich stimmig anfühlt. Was "
               "nicht passt, darfst du liegen lassen.",
          size=10.5, color=BODY_DK, h=6, after=3)
    for i, s in enumerate(sections):
        nr = ("0" + str(i + 1))[-2:]
        # Genug Platz halten, damit Nummer, Titel und der Anfang zusammenbleiben;
        # bricht es um, wird der Rest der Seite zart gefuellt.
        _break_with_accent(pdf, 62, min_remaining=48)
        pdf.ln(3)
        pdf.set_draw_color(*LINE_CREAM)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), PW - pdf.r_margin, pdf.get_y())
        pdf.ln(4)
        y0 = pdf.get_y()
        pdf.set_font("Mul", "B", 10)
        pdf.set_text_color(*GOLD_DK)
        with pdf.local_context(char_spacing=0.6):
            pdf.set_xy(pdf.l_margin, y0 + 2)
            pdf.cell(12, 7, safe(nr))
        pdf.set_xy(pdf.l_margin + 12, y0)
        pdf.set_font("Cormo", "", 22)
        pdf.set_text_color(*INK_DARK)
        pdf.multi_cell(PW - pdf.l_margin - pdf.r_margin - 12, 9, safe(s.get("title") or ""),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if s.get("subtitle"):
            pdf.set_x(pdf.l_margin + 12)
            pdf.set_font("Mul", "", 9)
            pdf.set_text_color(*MUTE)
            pdf.multi_cell(PW - pdf.l_margin - pdf.r_margin - 12, 5, safe(s["subtitle"]),
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
        if s.get("headline"):
            pdf.set_font("Cormo", "I", 14)
            pdf.set_text_color(*GOLD_DK)
            pdf.multi_cell(0, 6.4, safe(s["headline"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2.5)
        for para in str(s.get("body") or "").replace("\n\n", "\n").split("\n"):
            p = para.strip()
            if p:
                _para(pdf, p, size=10.5, color=BODY_DK, h=5.9, after=3.5)
        # Vier-Schritt-Bloecke (Kapitel "Deine groessten Schwierigkeiten")
        for b in s.get("blocks") or []:
            _dblock(pdf, b.get("kicker"), b.get("label"),
                    str(b.get("title") or ""), b.get("parts") or [])
        if s.get("after_blocks"):
            _para(pdf, s["after_blocks"], size=10.5, color=BODY_DK, h=5.9, after=3.5)
        if s.get("takeaway"):
            _merksatz(pdf, s["takeaway"])
        if s.get("facts"):
            _keep(pdf, 10 + 7 * len(s["facts"]))
            for row in s["facts"]:
                try:
                    kf, vf = row[0], row[1]
                except Exception:  # noqa
                    continue
                y1 = pdf.get_y()
                pdf.set_font("Mul", "", 9.5)
                pdf.set_text_color(*BODY_DK)
                pdf.cell((PW - pdf.l_margin - pdf.r_margin) * 0.42, 6, safe(str(kf)))
                pdf.set_xy(pdf.l_margin + (PW - pdf.l_margin - pdf.r_margin) * 0.42, y1)
                pdf.set_font("Mul", "B", 9.5)
                pdf.set_text_color(*INK_DARK)
                pdf.multi_cell((PW - pdf.l_margin - pdf.r_margin) * 0.58, 6, safe(str(vf)),
                               align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(1)
    _page_tail_accent(pdf)


def _lifepath_emblem(pdf, num):
    """Die Lebenszahl gross und auffaellig als goldenes Medaillon (wie im Bauplan)."""
    cx = PW / 2.0
    cy = pdf.get_y() + 24
    d = 40.0
    with pdf.local_context(fill_opacity=0.12):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, d * 1.5, style="F")
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.5)
    with pdf.local_context(stroke_opacity=0.6):
        _circle(pdf, cx, cy, d)
    with pdf.local_context(stroke_opacity=0.32):
        pdf.set_draw_color(*LILAC)
        _circle(pdf, cx, cy, d + 4)
    # grosse Zahl
    num_txt = str(num.get("lifepath", ""))
    pdf.set_font("Cormo", "B", 54)
    pdf.set_text_color(*GOLD)
    w = pdf.get_string_width(num_txt)
    pdf.set_xy(cx - w / 2.0, cy - 12.5)
    pdf.cell(w, 25, num_txt, align="C")
    pdf.set_y(cy + d / 2.0 + 5)
    # Titel + Tagline
    if num.get("title"):
        pdf.set_font("Cormo", "", 20)
        pdf.set_text_color(*INK_L)
        pdf.cell(0, 8, safe(num["title"]), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if num.get("tagline"):
        pdf.set_font("Cormo", "I", 13)
        pdf.set_text_color(*GOLD)
        pdf.cell(0, 6, safe(num["tagline"]), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if num.get("calc"):
        pdf.ln(2)
        pdf.set_font("Mul", "", 8.5)
        cl = safe(num["calc"])
        tw = pdf.get_string_width(cl)
        pw = tw + 16
        px = cx - pw / 2.0
        yy = pdf.get_y()
        pdf.set_fill_color(*CARD)
        pdf.set_draw_color(*LILAC)
        pdf.set_line_width(0.3)
        _round_rect(pdf, px, yy, pw, 8, 4, style="DF", border_opacity=0.35)
        pdf.set_xy(px, yy)
        pdf.set_text_color(*INK_SOFT)
        pdf.cell(pw, 8, cl, align="C")
        pdf.set_y(yy + 8)
    pdf.ln(6)


def _numerology(pdf, full):
    num = full["numerology"]
    pdf.theme = "dark"
    pdf.add_page()
    _heading_block(pdf, "Zahlen", "Deine Numerologie", on_dark=True)
    _para(pdf, "Zwei Zahlen, die sich aus deinem Geburtsdatum und deinem Vornamen "
               "ergeben und einen eigenen Blick auf deine Themen werfen.",
          size=10.5, color=BODY_DK, h=6, after=3)
    _lifepath_emblem(pdf, num)
    lp_body = str(num.get("text") or "")
    if num.get("strengths"):
        lp_body += "\nDeine Stärken: " + str(num["strengths"]) + "."
    if num.get("growth"):
        lp_body += "\nDeine Aufgabe: Es geht darum, " + str(num["growth"]) + "."
    if num.get("fact"):
        lp_body += "\nGut zu wissen: " + str(num["fact"])
    _unit(pdf, "Was deine Zahl erzählt",
          "Lebenszahl " + str(num.get("lifepath", "")),
          None, lp_body)
    py = num.get("personal_year")
    if py and py.get("number"):
        _unit(pdf, "Persönliches Jahr " + str(py.get("number", "")),
              str(py.get("year", "")) + " · " + str(py.get("theme", "")),
              None, str(py.get("text", "")) + " Diese Zahl wandert jedes Jahr eine weiter.")
    if num.get("note"):
        pdf.ln(2)
        _para(pdf, num["note"], size=8.5, color=MUTE, h=4.6, after=0)
    _page_tail_accent(pdf)


def _instagram(pdf, x, y, s, color):
    """Zeichnet ein Instagram-Symbol (gerundetes Quadrat, Linse, Punkt)."""
    lw = max(0.5, s * 0.085)
    pdf.set_draw_color(*color)
    pdf.set_line_width(lw)
    _round_rect(pdf, x, y, s, s, s * 0.30, style="D")
    r = s * 0.29
    pdf.ellipse(x + s / 2 - r, y + s / 2 - r, 2 * r, 2 * r, style="D")
    d = s * 0.13
    pdf.set_fill_color(*color)
    pdf.ellipse(x + s - s * 0.28 - d / 2, y + s * 0.28 - d / 2, d, d, style="F")


def _signoff(pdf, cy):
    """Zarter Sternen-Abschluss: ein leuchtender Kern zwischen zwei Goldlinien,
    von kleinen Sternen flankiert. Ein warmes Echo des Deckblatt-Rades."""
    cx = PW / 2.0
    with pdf.local_context(fill_opacity=0.08):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 66, style="F")
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.3)
    with pdf.local_context(stroke_opacity=0.5):
        pdf.line(cx - 36, cy, cx - 10, cy)
        pdf.line(cx + 10, cy, cx + 36, cy)
    # leuchtender Kern
    with pdf.local_context(fill_opacity=0.45):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 8, style="F")
    with pdf.local_context(fill_opacity=0.9):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, cy, 3.6, style="F")
    pdf.set_fill_color(255, 250, 240)
    _circle(pdf, cx, cy, 1.5, style="F")
    # flankierende Sternchen
    for dx, dy, col, op, d in [(-46, -2, LILAC, 0.8, 1.7), (46, -2, GOLD, 0.8, 1.7),
                               (-58, 3, GOLD, 0.5, 1.2), (58, 3, LILAC, 0.5, 1.2),
                               (-24, -9, GOLD, 0.55, 1.1), (24, -9, LILAC, 0.55, 1.1)]:
        with pdf.local_context(fill_opacity=op):
            pdf.set_fill_color(*col)
            _circle(pdf, cx + dx, cy + dy, d, style="F")


def _page_tail_accent(pdf, min_remaining=50.0):
    """Fuellt viel freien Raum am Seitenende mit einem sehr zarten, fliessenden
    Akzent. Die Variante wechselt je Seite, damit es nie gleich aussieht."""
    remaining = pdf.page_break_trigger - pdf.get_y()
    if remaining < min_remaining:
        return
    cx = PW / 2.0
    top = pdf.get_y()
    bot = pdf.page_break_trigger
    midy = min(top + remaining * 0.5, bot - 16)
    seed = pdf.page_no()
    feat = seed % 3

    # --- wechselndes, sehr dezentes Feature-Element ---
    if feat == 0:
        # weicher Schein, der sanft aus einer unteren Ecke ausblendet
        corner_x = (PW - 2) if (seed % 2) else 2
        with pdf.local_context(fill_opacity=0.05):
            pdf.set_fill_color(*GOLD)
            _circle(pdf, corner_x, bot + 2, 100, style="F")
    elif feat == 1:
        # zarter Ring, halb aus dem Seitenrand
        side_x = -8 if (seed % 2) else PW + 8
        pdf.set_line_width(0.3)
        with pdf.local_context(stroke_opacity=0.11):
            pdf.set_draw_color(*LILAC)
            _circle(pdf, side_x, midy, 92)
    else:
        # kleiner, blasser Kern mit zwei Linien
        with pdf.local_context(fill_opacity=0.04):
            pdf.set_fill_color(*GOLD)
            _circle(pdf, cx, midy, 50, style="F")
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.3)
        with pdf.local_context(stroke_opacity=0.28):
            pdf.line(cx - 24, midy, cx - 8, midy)
            pdf.line(cx + 8, midy, cx + 24, midy)
        with pdf.local_context(fill_opacity=0.65):
            pdf.set_fill_color(*GOLD)
            _circle(pdf, cx, midy, 2.6, style="F")

    # --- zart driftendes Sternenfeld, waechst mit dem freien Raum ---
    n = int(min(10, max(3, remaining / 16.0)))
    cols = [GOLD, LILAC, LILAC2, INK_SOFT]
    for i in range(n):
        fx = ((seed * (i * 7 + 5) + 13) % 101) / 101.0
        fy = ((seed * (i * 5 + 3) + i * 23 + 7) % 97) / 97.0
        x = MX + 10 + fx * (PW - 2 * MX - 20)
        y = top + 8 + fy * (remaining - 16)
        r = 0.9 + ((seed + i * 3) % 4) * 0.3
        with pdf.local_context(fill_opacity=0.8):
            _spark(pdf, x, y, r, cols[(i + seed) % 4])


def _break_with_accent(pdf, need, min_remaining=44.0):
    """Reicht der Platz fuer den naechsten Block nicht, wird der Rest der Seite
    mit einem zarten Akzent gefuellt und dann umgebrochen."""
    if pdf.get_y() + need > pdf.page_break_trigger:
        _page_tail_accent(pdf, min_remaining=min_remaining)
        pdf.add_page()
        return True
    return False


def _closing(pdf, full):
    """Abschlussseite: der warme Schlusstext, der spirituelle Lieblingsspruch
    und der Instagram-Auftritt."""
    pdf.theme = "dark"
    pdf.add_page()
    cx = PW / 2.0
    # weicher Goldschein oben + zarter Fliederring
    with pdf.local_context(fill_opacity=0.12):
        pdf.set_fill_color(*GOLD)
        _circle(pdf, cx, 20, 130, style="F")
    with pdf.local_context(stroke_opacity=0.16):
        pdf.set_draw_color(*LILAC)
        pdf.set_line_width(0.3)
        _circle(pdf, cx, 40, 150)
    # Inhalt etwas nach unten ruecken, damit die Seite ausgewogen wirkt
    pdf.set_y(42)
    _heading_block(pdf, "Abschluss", "Zum Schluss", on_dark=True)
    _para(pdf, full.get("closing"), font="Cormo", style="I", size=14,
          color=INK_L, h=7.0, after=6)

    # Lieblingsspruch als gold-/fliedergerahmtes Zitat
    quote = ("Du lebst nur einmal in diesem Leben. Du machst nichts falsch. "
             "Lebe das Leben genauso, wie du es dir vorstellst. Denn es ist deins.")
    _keep(pdf, 74)
    pdf.ln(3)
    x = pdf.l_margin
    w = PW - pdf.l_margin - pdf.r_margin
    top = pdf.get_y()
    pdf.set_font("Cormo", "I", 18)
    lines = pdf.multi_cell(w - 28, 8.4, safe(quote), dry_run=True, output="LINES")
    th = 8.4 * max(1, len(lines))
    box_h = 15 + th + 15
    pdf.set_fill_color(*CARD)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.4)
    _round_rect(pdf, x, top, w, box_h, 5, style="DF", border_opacity=0.5)
    with pdf.local_context(stroke_opacity=0.4):
        pdf.set_draw_color(*LILAC)
        pdf.set_line_width(0.3)
        _round_rect(pdf, x + 2, top + 2, w - 4, box_h - 4, 4, style="D")
    pdf.set_xy(x, top + 9)
    pdf.set_font("Vibes", "", 22)
    pdf.set_text_color(*GOLD)
    pdf.cell(w, 8, safe("Zum Mitnehmen"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(x + 14, top + 17)
    pdf.set_font("Cormo", "I", 18)
    pdf.set_text_color(*INK_L)
    pdf.multi_cell(w - 28, 8.4, safe(quote), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_y(top + box_h)

    # Instagram-Auftritt: Symbol + Handle
    pdf.ln(11)
    handle = "intuitionmitherz"
    icon_s = 8.0
    pdf.set_font("Mul", "B", 14)
    tw = pdf.get_string_width(handle)
    gap = 4.0
    total = icon_s + gap + tw
    gx = (PW - total) / 2.0
    gy = pdf.get_y()
    _instagram(pdf, gx, gy, icon_s, GOLD)
    pdf.set_xy(gx + icon_s + gap, gy)
    pdf.set_text_color(*INK_L)
    pdf.cell(tw, icon_s, handle)
    pdf.set_y(gy + icon_s + 4)
    # Aufruf: folgen und teilen
    _para(pdf, "Folge mir für mehr Impulse. Und wenn dich dein Bauplan berührt oder "
               "inspiriert hat, teile ihn gerne in deiner Story und verlinke "
               "@intuitionmitherz.",
          size=9.5, color=INK_SOFT, h=5.2, after=0, align="C")

    # zarter Sternen-Abschluss als Trenner
    _signoff(pdf, pdf.get_y() + 13)
    pdf.set_y(pdf.get_y() + 24)

    # Feindruck: Hinweis + Copyright
    import datetime
    year = datetime.date.today().year
    if full.get("note"):
        _para(pdf, full["note"], size=8, color=MUTE, h=4.4, after=1.5, align="C")
    pdf.set_font("Mul", "", 8)
    pdf.set_text_color(*MUTE)
    with pdf.local_context(char_spacing=0.3):
        pdf.cell(0, 4, safe("© %d Intuition mit Herz · Alle Rechte vorbehalten" % year),
                 align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _render(result, toc_entries):
    """Baut das komplette Dokument. Wird zweimal aufgerufen: einmal, um die
    Seitenzahlen der Kapitel einzusammeln, und einmal mit gefuelltem Inhalt."""
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
    pdf.add_font("Astro", "", os.path.join(FONT_DIR, "AstroSymbols.ttf"))
    pdf.set_title(safe("Dein kosmischer Bauplan"))
    pdf.set_author("Intuition mit Herz")

    _cover(pdf, birth, name)
    _toc_page(pdf, toc_entries)

    collected = []

    def chap(title, fn, *a):
        # Die Kapitelfunktion beginnt mit add_page(), die erste Seite ist also
        # die naechste. So kennen wir die Seitenzahl fuer das Inhaltsverzeichnis.
        first = pdf.page_no() + 1
        fn(pdf, *a)
        collected.append((("0" + str(len(collected) + 1))[-2:], title, first))

    # Reihenfolge wie die Reiter der Website: Uebersicht, Human Design,
    # Natalchart, Intuitionstyp, Numerologie, Deutung, dann der Abschluss.
    chap("Übersicht", _uebersicht, teaser, full)
    chap("Human Design", _human_design, teaser, full)
    chap("Natalchart", _natalchart, full)
    if full.get("intuition"):
        chap("Intuitionstyp", _intuition, full["intuition"])
    if full.get("numerology"):
        chap("Numerologie", _numerology, full)
    if full.get("sections"):
        chap("Deutung", _deutung, full["sections"])
    if full.get("closing"):
        chap("Zum Schluss", _closing, full)

    return pdf, collected


def build_pdf(result):
    # Erster Durchlauf sammelt die Seitenzahlen, der zweite fuellt das Inhaltsverzeichnis.
    _, collected = _render(result, None)
    pdf, _ = _render(result, collected)
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
