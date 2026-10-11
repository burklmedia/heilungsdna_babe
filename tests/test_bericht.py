"""
Selbsttest fuer /api/bericht (Warteliste Liebesanalyse und Frage an Denise).
Laeuft ohne Netzwerk, ohne KV und ohne echte Schluessel:

    python3 tests/test_bericht.py
"""
import contextlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

import bericht  # noqa: E402

FAILS = []
TEST_MAIL = "lena.test@beispiel.de"
TOKEN = "abcDEF123_-xyz"


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


@contextlib.contextmanager
def patched(module, **attrs):
    old = {k: getattr(module, k) for k in attrs}
    for k, v in attrs.items():
        setattr(module, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(module, k, v)


class Telegram:
    def __init__(self):
        self.texte = []

    def melden(self, text):
        self.texte.append(text)
        return True


def test_warteliste():
    print("Warteliste: Token wird zur E-Mail, Tag 13 am bestehenden Kontakt")
    getaggt = []
    with patched(bericht, kv_get=lambda k: TEST_MAIL if k == "imh:fbtok:" + TOKEN else None,
                 kv_incr_ttl=lambda k, ttl: 1, add_tag=lambda e, t: getaggt.append((e, t)) or (True, "gesetzt")):
        code, res = bericht.handle({"aktion": "warteliste", "t": TOKEN})
    check("mit Token gilt", code == 200 and res.get("ok"))
    check("Tag 13 an der aufgeloesten Adresse", getaggt == [(TEST_MAIL, "13")])

    getaggt.clear()
    with patched(bericht, kv_get=lambda k: None, kv_incr_ttl=lambda k, ttl: 1,
                 add_tag=lambda e, t: getaggt.append((e, t)) or (True, "gesetzt")):
        code, res = bericht.handle({"aktion": "warteliste", "t": "unbekannt123"})
        check("unbekannter Token ohne E-Mail fragt nach der Adresse", code == 400 and res.get("error") == "need_email")
        code, res = bericht.handle({"aktion": "warteliste", "email": TEST_MAIL})
        check("mit E-Mail gilt", code == 200 and getaggt == [(TEST_MAIL, "13")])
        bericht.handle({"aktion": "warteliste", "email": "keine-mail"})
        check("ungueltige E-Mail taggt nicht", len(getaggt) == 1)

    with patched(bericht, kv_get=lambda k: None, kv_incr_ttl=lambda k, ttl: 1, add_tag=lambda e, t: (False, "kein_kontakt")):
        code, res = bericht.handle({"aktion": "warteliste", "email": TEST_MAIL})
    check("unbekannter Kontakt wird nicht angelegt", code == 404 and res.get("error") == "unknown_contact")


def test_frage():
    print("Frage: anonym gespeichert, Telegram ohne Text")
    gespeichert = []
    tg = Telegram()
    with patched(bericht, kv_incr_ttl=lambda k, ttl: 1, telegram=tg,
                 push_feedback=lambda r, key="": gespeichert.append((key, r)) or True):
        code, res = bericht.handle({"aktion": "frage", "text": "  Wie merke ich,\n ob mein Bauch Ja sagt?  ", "email": TEST_MAIL})
        check("Frage gilt", code == 200 and res.get("ok"))
        check("in imh:fragen", gespeichert and gespeichert[0][0] == "imh:fragen")
        rec = gespeichert[0][1] if gespeichert else {}
        check("Text bereinigt", rec.get("frage") == "Wie merke ich, ob mein Bauch Ja sagt?")
        check("keine E-Mail im Datensatz", TEST_MAIL not in str(rec))
        check("Telegram ohne Fragetext", len(tg.texte) == 1 and "Bauch" not in tg.texte[0])
        code, res = bericht.handle({"aktion": "frage", "text": " "})
        check("leere Frage abgelehnt", code == 400 and len(gespeichert) == 1)
        bericht.handle({"aktion": "frage", "text": "x" * 5000})
        check("lange Frage gekuerzt", len(gespeichert[-1][1]["frage"]) == bericht.FRAGE_MAX)


def test_grenzen():
    print("Grenzen: unbekannte Aktion, Rate Limit")
    code, _ = bericht.handle({"aktion": "loeschen"})
    check("unbekannte Aktion 400", code == 400)
    with patched(bericht, kv_incr_ttl=lambda k, ttl: bericht.LIMIT_PRO_STUNDE + 1):
        code, _ = bericht.handle({"aktion": "frage", "text": "Hallo Denise"}, ip="1.2.3.4")
    check("zu viele Aufrufe 429", code == 429)


def test_stand():
    print("Stand: geräteübergreifend frühestes Öffnen, höchste Karte")
    kv = {}
    K = "a" * 32
    with patched(bericht, kv_get=lambda k: kv.get(k), kv_set=lambda k, v, ttl=None: kv.__setitem__(k, v) or True,
                 kv_incr_ttl=lambda k, ttl: 1):
        code, res = bericht.handle({"aktion": "stand", "k": K, "erst": 1790000000000, "nr": 0})
        check("erster Abgleich speichert", code == 200 and res["erst"] == 1790000000000 and res["nr"] == 0)
        code, res = bericht.handle({"aktion": "stand", "k": K, "erst": 1790500000000, "nr": 3, "tag": 300})
        check("späteres Öffnen ändert erst nicht", res["erst"] == 1790000000000)
        check("höhere Karte gewinnt", res["nr"] == 3 and res["tag"] == 300)
        code, res = bericht.handle({"aktion": "stand", "k": K, "nr": 2, "tag": 301})
        check("niedrigere Karte ändert nichts", res["nr"] == 3 and res["tag"] == 300)
        code, res = bericht.handle({"aktion": "stand", "k": K, "erst": 1789000000000})
        check("früheres Öffnen gewinnt", res["erst"] == 1789000000000)
        code, res = bericht.handle({"aktion": "stand", "k": "kurz"})
        check("ungültiger Schlüssel 400", code == 400)
        code, res = bericht.handle({"aktion": "stand", "k": K, "erst": 99})
        check("unsinniger Zeitpunkt wird ignoriert", res["erst"] == 1789000000000)
        bericht.handle({"aktion": "stand", "k": K, "neu": True})
        check("neu beginnen erst nach 180 Karten", json.loads(kv["imh:stand:" + K])["nr"] == 3)
        bericht.handle({"aktion": "stand", "k": K, "nr": 180, "tag": 480})
        code, res = bericht.handle({"aktion": "stand", "k": K, "neu": True})
        check("nach 180 Karten neu beginnen", res["nr"] == 0 and res["erst"] == 1789000000000)
        check("im Speicher nur Zeit und Karte", set(json.loads(kv["imh:stand:" + K]).keys()) == {"erst", "nr", "tag"})


if __name__ == "__main__":
    for fn in (test_warteliste, test_frage, test_grenzen, test_stand):
        fn()
    print()
    if FAILS:
        print("FEHLGESCHLAGEN: %d" % len(FAILS))
        for f in FAILS:
            print(" - " + f)
        sys.exit(1)
    print("Bericht-Aktionen bestaetigt.")
