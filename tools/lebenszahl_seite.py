#!/usr/bin/env python3
"""
Füllt public/lebenszahl.html aus den Bauplan-Texten in api/_interpret.py (seit 19.10.2026).

Ersetzt die Bereiche zwischen den Markern:
    <!-- LZ-JSONLD --> … <!-- /LZ-JSONLD -->   strukturierte Daten (WebPage, Breadcrumb, WebApplication, FAQPage)
    <!-- LZ-RASTER --> … <!-- /LZ-RASTER -->   die zwölf Lebenszahlen als statisches HTML (für Google lesbar)
    <!-- LZ-FAQ --> … <!-- /LZ-FAQ -->         die Fragen
    /* LZ-DATEN */ … /* /LZ-DATEN */           die Texte für den Rechner

Nach jeder Änderung an LIFEPATH, LIFEPATH_MORE oder LIFEPATH_FACT erneut laufen lassen:
    python3 tools/lebenszahl_seite.py
Die langen Texte (LIFEPATH[..]["text"]) bleiben dem Bauplan vorbehalten und kommen hier nicht vor.
"""
import html
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "api"))

from _interpret import LIFEPATH, LIFEPATH_MORE, LIFEPATH_FACT  # noqa: E402

SEITE = os.path.join(BASE, "public", "lebenszahl.html")
URL = "https://bauplan.intuitionmitherz.de/lebenszahl"
ZAHLEN = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33]

# Fragen in Denises Stimme: kein „Vielleicht“/„Manchmal“ am Satzanfang, kein „nicht X, sondern Y“, keine Gedankenstriche.
FRAGEN = [
    ("Wie berechne ich meine Lebenszahl?",
     "Du zählst alle Ziffern deines Geburtsdatums zusammen und bildest so lange die Quersumme, bis eine Zahl von 1 bis 9 "
     "übrig bleibt. Ergibt sich unterwegs 11, 22 oder 33, bleibt diese Meisterzahl stehen. Aus dem 14.06.1994 wird so "
     "1 + 4 + 0 + 6 + 1 + 9 + 9 + 4 = 34 und daraus 3 + 4 = 7."),
    ("Was sind Meisterzahlen?",
     "Die 11, die 22 und die 33. Sie gelten in der Numerologie als besonders kraftvoll und werden deshalb nicht weiter "
     "zusammengezählt. Die 11 trägt das Thema der 2 in einer feineren Form, die 22 das der 4 und die 33 das der 6."),
    ("Warum zeigt ein anderer Rechner eine andere Lebenszahl?",
     "Einige Rechner zählen Tag, Monat und Jahr erst einzeln zusammen. Bei den Zahlen 1 bis 9 ändert das nichts. Bei den "
     "Meisterzahlen kann es abweichen: Auf dem einen Weg erscheint die 11, auf dem anderen gleich die 2. Hier und im "
     "Kosmischen Bauplan werden alle Ziffern auf einmal zusammengezählt."),
    ("Brauche ich für die Lebenszahl meine Geburtszeit?",
     "Für die Lebenszahl reicht dein Geburtsdatum. Für deinen ganzen Kosmischen Bauplan brauchst du auch die Geburtszeit, "
     "weil Aszendent, Häuser und dein Human-Design-Chart davon abhängen."),
    ("Ist die Lebenszahl dasselbe wie die Seelenzahl?",
     "In den meisten Numerologie-Systemen sind das zwei verschiedene Zahlen. Die Lebenszahl kommt aus deinem "
     "Geburtsdatum, die Seelenzahl aus den Vokalen deines Namens."),
    ("Ist die Numerologie wissenschaftlich belegt?",
     "Nein. Die Numerologie ist ein symbolisches Deutungssystem. Die Rechnung ist eindeutig, die Bedeutung ist ein "
     "Angebot, über dich nachzudenken, und ersetzt keine Beratung."),
    ("Wird mein Geburtsdatum gespeichert?",
     "Auf dieser Seite wird deine Lebenszahl direkt in deinem Browser ausgerechnet. Dein Geburtsdatum wird dabei an "
     "niemanden geschickt."),
]


def daten():
    out = {}
    for z in ZAHLEN:
        info, more = LIFEPATH[z], LIFEPATH_MORE[z]
        out[z] = {"titel": info["title"], "unter": info["tagline"], "staerken": more["strengths"],
                  "aufgabe": more["growth"], "gut": LIFEPATH_FACT[z]}
    return out


def raster(d):
    karten = []
    for z in ZAHLEN:
        x = d[z]
        karten.append(
            f'      <article class="zahl{" meister" if z > 9 else ""}" id="zahl-{z}">\n'
            f'        <div class="mini" aria-hidden="true">{z}</div>\n'
            f'        <div>\n'
            f'          <h3>Lebenszahl {z}: {html.escape(x["titel"])}</h3>\n'
            f'          <p class="unter">{html.escape(x["unter"])}</p>\n'
            f'          <p><strong>Stärken:</strong> {html.escape(x["staerken"])}.</p>\n'
            f'          <p><strong>Deine Aufgabe</strong> ist, {html.escape(x["aufgabe"])}.</p>\n'
            f'        </div>\n'
            f'      </article>')
    return '    <div class="raster">\n' + "\n".join(karten) + "\n    </div>\n    "


def faq():
    teile = []
    for f, a in FRAGEN:
        teile.append(f'      <details><summary>{html.escape(f)}</summary><p>{html.escape(a)}</p></details>')
    return "\n".join(teile) + "\n      "


def jsonld():
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "@id": URL + "#seite", "url": URL,
             "name": "Lebenszahl berechnen: kostenlos, mit Bedeutung",
             "description": "Lebenszahl aus dem Geburtsdatum berechnen, mit Rechenweg, Meisterzahlen 11, 22 und 33 "
                            "und der Bedeutung jeder Zahl.",
             "inLanguage": "de-DE",
             "isPartOf": {"@id": "https://bauplan.intuitionmitherz.de/#website"},
             "publisher": {"@id": "https://bauplan.intuitionmitherz.de/#organization"},
             "breadcrumb": {"@id": URL + "#breadcrumb"}},
            {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Kosmischer Bauplan",
                 "item": "https://bauplan.intuitionmitherz.de/"},
                {"@type": "ListItem", "position": 2, "name": "Lebenszahl berechnen", "item": URL}]},
            {"@type": "WebApplication", "@id": URL + "#rechner", "name": "Lebenszahl-Rechner",
             "url": URL, "applicationCategory": "LifestyleApplication", "operatingSystem": "Web",
             "inLanguage": "de-DE", "isAccessibleForFree": True,
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
             "provider": {"@id": "https://bauplan.intuitionmitherz.de/#organization"}},
            {"@type": "FAQPage", "@id": URL + "#fragen", "mainEntity": [
                {"@type": "Question", "name": f, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for f, a in FRAGEN]},
        ],
    }
    return '<script type="application/ld+json">\n' + json.dumps(graph, ensure_ascii=False, indent=2) + "\n</script>\n"


def ersetzen(text, start, ende, inhalt):
    muster = re.compile(re.escape(start) + r".*?" + re.escape(ende), re.S)
    if not muster.search(text):
        sys.exit(f"Marker fehlt: {start}")
    return muster.sub(lambda _: start + inhalt + ende, text, count=1)


def main():
    d = daten()
    text = open(SEITE, encoding="utf-8").read()
    text = ersetzen(text, "<!-- LZ-JSONLD -->\n", "<!-- /LZ-JSONLD -->", jsonld())
    text = ersetzen(text, "<!-- LZ-RASTER -->\n", "<!-- /LZ-RASTER -->", raster(d))
    text = ersetzen(text, "<!-- LZ-FAQ -->\n", "<!-- /LZ-FAQ -->", faq())
    text = ersetzen(text, "/* LZ-DATEN */", "/* /LZ-DATEN */",
                    "var LZ=" + json.dumps({str(k): v for k, v in d.items()}, ensure_ascii=False) + ";")
    open(SEITE, "w", encoding="utf-8").write(text)
    print("lebenszahl.html aktualisiert:", len(ZAHLEN), "Zahlen,", len(FRAGEN), "Fragen")


if __name__ == "__main__":
    main()
