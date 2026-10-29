"""
Selbsttest fuer das Feedback direkt im Bauplan (/api/feedback mit art "kapitel" und "bauplan").
Laeuft ohne Netzwerk, ohne KV und ohne echte Schluessel:

    python3 tests/test_rueckmeldung.py
"""
import contextlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

import feedback  # noqa: E402

FAILS = []
TEST_MAIL = "lena.test@beispiel.de"
TOKEN = "abcDEF123_-xyz"


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


@contextlib.contextmanager
def speicher():
    """Ersetzt KV, ActiveCampaign und Telegram durch Attrappen im Arbeitsspeicher."""
    sp = {"kv": {"imh:fbtok:" + TOKEN: TEST_MAIL}, "listen": {}, "zaehler": {}, "ac": [], "tg": []}

    class Telegram:
        @staticmethod
        def melden(text):
            sp["tg"].append(text)
            return True

    attrs = {
        "kv_get": lambda k: sp["kv"].get(k),
        "kv_setnx": lambda k, v, ttl=None: (k not in sp["kv"]) and (sp["kv"].__setitem__(k, v) or True),
        "kv_del": lambda k: sp["kv"].pop(k, None) or True,
        "kv_incr_ttl": lambda k, ttl: 1,
        "incr": lambda keys: [sp["zaehler"].__setitem__(k, sp["zaehler"].get(k, 0) + 1) for k in keys],
        "push_feedback": lambda r, key="imh:feedback": sp["listen"].setdefault(key, []).append(r) or True,
        "update_contact": lambda email, fields: sp["ac"].append((email, fields)) or (True, ""),
        "telegram": Telegram,
    }
    old = {k: getattr(feedback, k) for k in attrs}
    for k, v in attrs.items():
        setattr(feedback, k, v)
    try:
        yield sp
    finally:
        for k, v in old.items():
            setattr(feedback, k, v)


GELESEN = {"sek": 420, "themen": ["hd", "in", "de"], "geoeffnet": 4}
ANTWORTEN = {"wiedererkannt": 4, "beruehrt": ["Intuitionstyp", "Erfunden"], "verstaendlich": "Klar und leicht",
             "aha": "  Der Satz über mein Bauchgefühl.  ", "empfehlen": 9, "stimme_text": "Ich habe mich so gesehen gefühlt.",
             "stimme_ok": True, "vorname": "Lena"}

print("Kapitel-Frage")
with speicher() as sp:
    code, p = feedback.handle_kapitel({"thema": "hd", "wert": "ja", "sek": 5})
    check("zu kurz im Thema -> 403", code == 403 and p["error"] == "zu_frueh")
    code, p = feedback.handle_kapitel({"thema": "xx", "wert": "ja", "sek": 50})
    check("unbekanntes Thema -> 400", code == 400)
    code, p = feedback.handle_kapitel({"thema": "hd", "wert": "ja", "sek": 50})
    check("gezaehlt", code == 200 and sp["zaehler"].get("imh:kap:hd:ja") == 1)
    code, p = feedback.handle_kapitel({"thema": "nu", "wert": "nein", "sek": 50, "text": "Passt gar nicht", "nur_text": True, "t": TOKEN})
    check("Anmerkung gespeichert, nicht doppelt gezaehlt", code == 200 and not sp["zaehler"].get("imh:kap:nu:nein")
          and sp["listen"]["imh:kapitel"][0]["text"] == "Passt gar nicht" and sp["listen"]["imh:kapitel"][0]["email"] == TEST_MAIL)
    feedback.handle_kapitel({"thema": "na", "wert": "teils", "sek": 50}, intern=True)
    check("interne Geraete zaehlen nicht", not sp["zaehler"].get("imh:kap:na:teils"))

print("Fragebogen")
with speicher() as sp:
    code, p = feedback.handle_rueckmeldung({"antworten": ANTWORTEN, "lesen": {"sek": 100, "themen": ["hd", "in", "de"]}})
    check("zu wenig Lesezeit -> 403", code == 403)
    code, p = feedback.handle_rueckmeldung({"antworten": ANTWORTEN, "lesen": {"sek": 900, "themen": ["hd"]}})
    check("zu wenig Themen -> 403", code == 403)
    code, p = feedback.handle_rueckmeldung({"antworten": {}, "lesen": GELESEN})
    check("ohne Sterne -> 400", code == 400)
    code, p = feedback.handle_rueckmeldung({"antworten": ANTWORTEN, "lesen": GELESEN, "kapitel": {"hd": "ja", "zz": "ja"},
                                            "profil": {"typ": "Generator", "sonne": "Zwillinge"}})
    r = sp["listen"]["imh:rueckmeldung"][0]
    check("ohne Token angenommen, ohne E-Mail", code == 200 and r["email"] == "" and not sp["ac"])
    check("nur erlaubte Antworten", r["antworten"]["beruehrt"] == ["Intuitionstyp"] and r["antworten"]["aha"] == "Der Satz über mein Bauchgefühl.")
    check("Kapitel bereinigt", r["kapitel"] == {"hd": "ja"})
    check("Vorname nur mit Freigabe", r["antworten"]["vorname"] == "Lena")
    check("Telegram ohne Text der Leserin", len(sp["tg"]) == 1 and "Bauchgefühl" not in sp["tg"][0] and "Lena" not in sp["tg"][0])

with speicher() as sp:
    ohne = dict(ANTWORTEN, stimme_ok=False)
    feedback.handle_rueckmeldung({"antworten": ohne, "lesen": GELESEN})
    check("ohne Freigabe kein Vorname", sp["listen"]["imh:rueckmeldung"][0]["antworten"]["vorname"] == "")

with speicher() as sp:
    code, p = feedback.handle_rueckmeldung({"antworten": ANTWORTEN, "lesen": GELESEN, "t": TOKEN})
    check("mit Token: E-Mail zugeordnet, AC 'Feedback gegeben'", code == 200 and sp["listen"]["imh:rueckmeldung"][0]["email"] == TEST_MAIL
          and sp["ac"] == [(TEST_MAIL, {"feedback_given": "yes"})])
    code, p = feedback.handle_rueckmeldung({"antworten": ANTWORTEN, "lesen": GELESEN, "t": TOKEN})
    check("zweites Absenden: keine Dublette", code == 200 and p.get("already") and len(sp["listen"]["imh:rueckmeldung"]) == 1)
    feedback.handle_rueckmeldung({"antworten": ANTWORTEN, "lesen": GELESEN}, intern=True)
    check("intern: kein Telegram", len(sp["tg"]) == 1)

print()
if FAILS:
    print("%d Fehler" % len(FAILS))
    sys.exit(1)
print("Alles in Ordnung.")
