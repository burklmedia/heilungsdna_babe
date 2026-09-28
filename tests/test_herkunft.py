"""
Selbsttest fuer die Herkunft (Kurzlinks /story, /kommentar, /bio, /dm und Feld Herkunft in ActiveCampaign).
Laeuft ohne Netzwerk, ohne KV und ohne echte Schluessel:

    python3 tests/test_herkunft.py
"""
import contextlib
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

import _herkunft  # noqa: E402
import kurz  # noqa: E402
import subscribe  # noqa: E402

FAILS = []
TEST_MAIL = "lena.test@beispiel.de"
BROWSER = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Instagram 350.0"


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


@contextlib.contextmanager
def env(**values):
    old = {k: os.environ.get(k) for k in values}
    for k, v in values.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class FakeHandler(kurz.handler):
    """Ruft den Handler ohne Server auf."""

    def __init__(self, pfad, headers):
        self.path = pfad
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.headers_get = self.headers.get
        self.wfile = io.BytesIO()
        self.status = None
        self.kopf = {}

    def send_response(self, code, message=None):
        self.status = code

    def send_header(self, k, v):
        self.kopf[k.lower()] = v

    def end_headers(self):
        pass


class Kopf(dict):
    def get(self, k, d=None):
        return super().get(k.lower(), d)


def aufruf(pfad, **headers):
    h = FakeHandler(pfad, headers)
    h.headers = Kopf({k.lower(): v for k, v in headers.items()})
    h.do_GET()
    return h


def test_kanal():
    print("Kanal: nur kurze, einfache Namen")
    check("story gilt", _herkunft.kanal("story") == "story")
    check("Grossschreibung wird klein", _herkunft.kanal("Kommentar") == "kommentar")
    check("mail-3 gilt", _herkunft.kanal("mail-3") == "mail-3")
    check("Sonderzeichen gelten nicht", _herkunft.kanal("<script>") is None)
    check("leer gilt nicht", _herkunft.kanal("") is None and _herkunft.kanal(None) is None)


def test_kurzlink():
    print("Kurzlinks: zaehlen und weiterleiten")
    gemerkt = []
    with patched(kurz, merken=lambda a, k: gemerkt.append((a, k)) or True):
        h = aufruf("/api/kurz.py?k=story", **{"User-Agent": BROWSER})
        check("302 nach /?q=story", h.status == 302 and h.kopf.get("location") == "/?q=story")
        check("ein Klick gezaehlt", gemerkt == [("klick", "story")])
        h = aufruf("/kommentar", **{"User-Agent": BROWSER})
        check("Pfad /kommentar geht auch", h.kopf.get("location") == "/?q=kommentar")
        gemerkt.clear()
        h = aufruf("/api/kurz.py?k=story", **{"User-Agent": "facebookexternalhit/1.1"})
        check("Link-Vorschau leitet weiter", h.kopf.get("location") == "/?q=story")
        check("Link-Vorschau zaehlt nicht", gemerkt == [])
        h = aufruf("/api/kurz.py?k=story")
        check("ohne Kennung zaehlt nicht", gemerkt == [])
        h = aufruf("/api/kurz.py?k=hack", **{"User-Agent": BROWSER})
        check("unbekannter Kanal geht auf die Startseite, ohne Zaehlung", h.kopf.get("location") == "/" and gemerkt == [])
    check("keine Cache-Speicherung", h.kopf.get("cache-control") == "no-store")


def test_ereignisse_nur_mit_token():
    print("Ereignisse fuer das Dashboard: nur mit Token")
    daten = [{"a": "klick", "k": "story", "t": "2026-09-28T18:00:00Z"}]
    with patched(kurz, ereignisse=lambda: daten, schritte=lambda: {"visit": 3}, schritte_tage=lambda: {}):
        with env(HERKUNFT_TOKEN="geheim-123"):
            h = aufruf("/api/kurz?ereignisse=1")
            check("ohne Token 404", h.status == 404)
            h = aufruf("/api/kurz?ereignisse=1", Authorization="Bearer falsch")
            check("falsches Token 404", h.status == 404)
            h = aufruf("/api/kurz?ereignisse=1", Authorization="Bearer geheim-123")
            check("richtiges Token 200 mit Ereignissen", h.status == 200 and json.loads(h.wfile.getvalue()) == {"ereignisse": daten, "schritte": {"visit": 3}, "stichtag": "2026-09-29", "tage": {}})
        with env(HERKUNFT_TOKEN=None):
            h = aufruf("/api/kurz?ereignisse=1", Authorization="Bearer ")
            check("ohne eingerichtetes Token nie offen", h.status == 404)


def test_anmeldung_setzt_herkunft():
    print("Anmeldung: Herkunft in AC-Feld 8 und gezaehlt")
    gemerkt = []
    gesetzt = []
    antworten = [(False, "kein_kontakt"), (True, "gesetzt")]
    with patched(subscribe, _submit=lambda f: (True, None), kv_set=lambda *a, **k: True,
                 ac_api_configured=lambda: True, herkunft_merken=lambda a, k: gemerkt.append((a, k)),
                 set_fields=lambda e, v: gesetzt.append((e, v)) or antworten.pop(0)), \
            patched(subscribe.time, sleep=lambda s: None), patched(subscribe, form_connected=lambda: True):
        code, res = subscribe.handle_subscribe({"email": TEST_MAIL, "q": "story"})
    check("Anmeldung gilt", code == 200 and res.get("ok"))
    check("Anmeldung mit Kanal story gezaehlt", gemerkt == [("anmeldung", "story")])
    check("Feld 8 = story, zweiter Versuch nach kein_kontakt", gesetzt == [(TEST_MAIL, {"8": "story"})] * 2)

    gemerkt.clear()
    gesetzt.clear()
    with patched(subscribe, _submit=lambda f: (True, None), kv_set=lambda *a, **k: True,
                 ac_api_configured=lambda: True, herkunft_merken=lambda a, k: gemerkt.append((a, k)),
                 set_fields=lambda e, v: gesetzt.append(v) or (True, "gesetzt"), form_connected=lambda: True):
        subscribe.handle_subscribe({"email": TEST_MAIL, "q": "<b>"})
    check("ungueltiger Kanal wird direkt", gemerkt == [("anmeldung", "direkt")] and gesetzt == [{"8": "direkt"}])

    with patched(subscribe, _submit=lambda f: (False, "upstream_http"), kv_set=lambda *a, **k: True,
                 herkunft_merken=lambda a, k: gemerkt.append(("fehler", k)), form_connected=lambda: True):
        gemerkt.clear()
        code, _ = subscribe.handle_subscribe({"email": TEST_MAIL, "q": "story"})
    check("gescheiterte Anmeldung zaehlt nicht", code == 502 and gemerkt == [])


def test_intern():
    print("Eigene Geraete: Cookie imh_intern=1 zaehlt nicht")
    check("Cookie erkannt", _herkunft.ist_intern("a=1; imh_intern=1; b=2"))
    check("ohne Cookie nicht intern", not _herkunft.ist_intern("") and not _herkunft.ist_intern(None))
    check("anderer Wert nicht intern", not _herkunft.ist_intern("imh_intern=0"))
    gemerkt = []
    with patched(kurz, merken=lambda a, k: gemerkt.append((a, k)) or True):
        h = aufruf("/api/kurz.py?k=story", **{"User-Agent": BROWSER, "Cookie": "imh_intern=1"})
    check("interner Klick leitet weiter, zaehlt aber nicht", h.kopf.get("location") == "/?q=story" and gemerkt == [])
    gemerkt.clear()
    gesetzt = []
    with patched(subscribe, _submit=lambda f: (True, None), kv_set=lambda *a, **k: True,
                 ac_api_configured=lambda: True, herkunft_merken=lambda a, k: gemerkt.append((a, k)),
                 set_fields=lambda e, v: gesetzt.append(v) or (True, "gesetzt"), form_connected=lambda: True):
        subscribe.handle_subscribe({"email": TEST_MAIL, "q": "story"}, intern=True)
    check("interne Anmeldung: Herkunft intern in AC, nicht gezaehlt", gesetzt == [{"8": "intern"}] and gemerkt == [])


def test_schritte_tage():
    print("Schritte je Tag ab Stichtag")
    from datetime import date
    with patched(_herkunft, mget=lambda keys: [1 if k.endswith(":visit") else 0 for k in keys]):
        t = _herkunft.schritte_tage(heute=date(2026, 9, 30))
    check("zwei Tage ab 29.09.", sorted(t) == ["2026-09-29", "2026-09-30"])
    check("nur Schritte mit Wert", t["2026-09-29"] == {"visit": 1})
    with patched(_herkunft, mget=lambda keys: [5] * len(keys)):
        check("vor dem Stichtag nichts", _herkunft.schritte_tage(heute=date(2026, 9, 28)) == {})


def test_merken():
    print("Speicher: nur Art, Kanal und Zeit")
    gespeichert = []
    with patched(_herkunft, push_feedback=lambda r, key=None: gespeichert.append((key, r)) or True):
        _herkunft.merken("klick", "story")
        _herkunft.merken("klick", "<x>")
        _herkunft.merken("kauf", "story")
    check("genau ein Eintrag", len(gespeichert) == 1)
    key, r = gespeichert[0]
    check("Liste imh:herkunft", key == "imh:herkunft")
    check("nur a, k, t", set(r) == {"a", "k", "t"} and r["a"] == "klick" and r["k"] == "story")


if __name__ == "__main__":
    for fn in (test_kanal, test_kurzlink, test_ereignisse_nur_mit_token, test_anmeldung_setzt_herkunft, test_intern, test_schritte_tage, test_merken):
        fn()
    print()
    if FAILS:
        print("FEHLGESCHLAGEN: %d" % len(FAILS))
        for f in FAILS:
            print(" - " + f)
        sys.exit(1)
    print("Herkunft bestaetigt.")
