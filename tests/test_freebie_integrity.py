"""
Regressionstest fuer die Unabhaengigkeit des kostenlosen Freebies.

Founder-Entscheidung: Die Bauplan-Verbindung wird AUSSCHLIESSLICH aus der
Heilungs-DNA heraus gestartet. Das kostenlose Produkt bekommt dadurch keine
Werbung, keinen Verkaufsbutton und keinen sichtbaren Einstieg in das
Folgeprodukt.

    python3 tests/test_freebie_integrity.py
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FAILS = []


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


# Kennzeichen des Folgeprodukts, die auf oeffentlichen Freebie-Flaechen nichts
# zu suchen haben.
PAID_MARKERS = ["heilungs-dna", "heilungsdna", "intuition-paidproduct", "/verbinden"]

PUBLIC_SURFACES = [
    "public/index.html",
    "public/feedback.html",
    "public/thema.html",
    "public/datenschutz.html",
    "public/impressum.html",
]


def test_public_surfaces_clean():
    print("Oeffentliche Freebie-Flaechen ohne Folgeprodukt-Werbung")
    for rel in PUBLIC_SURFACES:
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        low = read(rel).lower()
        for marker in PAID_MARKERS:
            check("%s ohne '%s'" % (rel, marker), marker not in low)


def test_emails_clean():
    print("Bestehende E-Mails ohne Folgeprodukt-Werbung")
    mail_dir = os.path.join(ROOT, "emails")
    if not os.path.isdir(mail_dir):
        print("  (keine emails/)")
        return
    for name in sorted(os.listdir(mail_dir)):
        if not name.endswith(".html"):
            continue
        low = read(os.path.join("emails", name)).lower()
        for marker in PAID_MARKERS:
            check("emails/%s ohne '%s'" % (name, marker), marker not in low)


def test_pdf_and_funnel_untouched_by_markers():
    print("PDF- und Funnel-Endpunkte ohne Folgeprodukt-Verweise")
    for rel in ["api/pdf.py", "api/subscribe.py", "api/analyze.py"]:
        low = read(rel).lower()
        for marker in ["heilungs-dna", "heilungsdna", "intuition-paidproduct"]:
            check("%s ohne '%s'" % (rel, marker), marker not in low)


def test_verbinden_direct_access_is_neutral():
    print("Direktaufruf von /verbinden bleibt neutral")
    html = read("public/verbinden.html")

    # Titel und Erklaerung sind per Default versteckt und werden erst nach
    # serverseitiger Bestaetigung eines aktiven Vorgangs eingeblendet.
    check("Titel per Default hidden", re.search(r'<h1 id="title"[^>]*\bhidden\b', html) is not None)
    check("Lead per Default hidden", re.search(r'<p id="lead"[^>]*\bhidden\b', html) is not None)

    # Der Block fuer den ungueltigen Aufruf nennt das Folgeprodukt nicht und
    # bietet einen Rueckweg ins normale Freebie.
    m = re.search(r'<div id="invalid"[^>]*>(.*?)</div>', html, re.S)
    check("invalid-Block vorhanden", m is not None)
    if m:
        block = m.group(1).lower()
        check("invalid-Block ohne Produktnennung", "heilungs" not in block)
        check("invalid-Block ohne Kauf-CTA", not any(w in block for w in ["kaufen", "jetzt starten", "angebot", "preis"]))
        check("invalid-Block mit Rueckweg zur Startseite", 'href="/"' in m.group(1))


def test_verbinden_hygiene():
    print("Uebergabeseite: Hygiene")
    html = read("public/verbinden.html")
    check("noindex gesetzt", "noindex" in html)
    check("no-referrer gesetzt", 'content="no-referrer"' in html)
    # Keine Drittanbieter-Skripte auf der Uebergabe-/Callback-Seite.
    externals = re.findall(r'<script[^>]+src=["\']([^"\']+)', html)
    check("keine externen Skripte", externals == [])
    # Keine fest verdrahtete Ziel-URL mehr im Quelltext.
    check("kein hartcodiertes Rueckgabeziel", "intuition-paidproduct" not in html.lower())


def test_verbinden_not_linked_publicly():
    print("/verbinden ist nirgends oeffentlich verlinkt")
    for rel in PUBLIC_SURFACES:
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        check("%s verlinkt /verbinden nicht" % rel, "/verbinden" not in read(rel))


if __name__ == "__main__":
    for fn in (
        test_public_surfaces_clean,
        test_emails_clean,
        test_pdf_and_funnel_untouched_by_markers,
        test_verbinden_direct_access_is_neutral,
        test_verbinden_hygiene,
        test_verbinden_not_linked_publicly,
    ):
        fn()
    print()
    if FAILS:
        print("FEHLGESCHLAGEN: %d" % len(FAILS))
        for f in FAILS:
            print(" - " + f)
        sys.exit(1)
    print("Freebie-Unabhaengigkeit bestaetigt.")
