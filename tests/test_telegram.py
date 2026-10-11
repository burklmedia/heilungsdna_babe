"""
Selbsttest fuer die Telegram-Meldung bei jeder Bauplan-Anmeldung.
Laeuft ohne Netzwerk und ohne echten Bot-Token (urlopen ist ersetzt):

    python3 tests/test_telegram.py
"""
import contextlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

import _telegram  # noqa: E402
import subscribe  # noqa: E402

FAILS = []
TEST_MAIL = "lena.test@beispiel.de"
FAKE_ENV = {"TELEGRAM_BOT_TOKEN": "123:test", "TELEGRAM_CHAT_ID": "-100"}


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


class Antwort:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def anrufe_mitschreiben(fehler=False):
    anrufe = []

    def urlopen(req, timeout=None):
        anrufe.append((req.full_url, json.loads(req.data.decode("utf-8"))))
        if fehler:
            raise OSError("netz weg")
        return Antwort()
    return anrufe, urlopen


@contextlib.contextmanager
def anmeldung_klappt(ac_ok=True):
    with patched(subscribe, _submit=lambda f: (True, None) if ac_ok else (False, "upstream_http"),
                 kv_set=lambda *a, **k: True, ac_api_configured=lambda: False,
                 herkunft_merken=lambda a, k: None, form_connected=lambda: True):
        yield


def test_ohne_einrichtung():
    print("Ohne Token und Chat-ID: keine Meldung")
    anrufe, urlopen = anrufe_mitschreiben()
    with env(TELEGRAM_BOT_TOKEN=None, TELEGRAM_CHAT_ID=None), patched(_telegram.urllib.request, urlopen=urlopen), anmeldung_klappt():
        code, _ = subscribe.handle_subscribe({"email": TEST_MAIL, "name": "Lena"})
    check("Anmeldung gilt", code == 200)
    check("kein Aufruf an Telegram", anrufe == [])
    check("Diagnose: nicht eingerichtet", not _telegram.configured())


def test_meldung():
    print("Erfolgreiche Anmeldung: genau eine Meldung ohne Daten der Person")
    anrufe, urlopen = anrufe_mitschreiben()
    with env(**FAKE_ENV), patched(_telegram.urllib.request, urlopen=urlopen), anmeldung_klappt():
        code, _ = subscribe.handle_subscribe({"email": TEST_MAIL, "name": "Lena"})
        eingerichtet = _telegram.configured()
    check("Anmeldung gilt", code == 200)
    check("genau ein Aufruf", len(anrufe) == 1)
    url, daten = anrufe[0] if anrufe else ("", {})
    check("an sendMessage des Bots", url == "https://api.telegram.org/bot123:test/sendMessage")
    check("an die Gruppe", daten.get("chat_id") == "-100")
    text = daten.get("text", "")
    check("Text nennt die Anmeldung", "Anmeldung" in text and "Bauplan" in text)
    check("keine E-Mail und kein Name im Text", TEST_MAIL not in text and "Lena" not in text)
    check("Diagnose: eingerichtet", eingerichtet)


def test_keine_meldung():
    print("Intern und gescheiterte Anmeldung: keine Meldung")
    anrufe, urlopen = anrufe_mitschreiben()
    with env(**FAKE_ENV), patched(_telegram.urllib.request, urlopen=urlopen):
        with anmeldung_klappt():
            subscribe.handle_subscribe({"email": TEST_MAIL}, intern=True)
        check("interne Anmeldung meldet nicht", anrufe == [])
        with anmeldung_klappt(ac_ok=False):
            code, _ = subscribe.handle_subscribe({"email": TEST_MAIL})
        check("gescheiterte Anmeldung meldet nicht", code == 502 and anrufe == [])
        subscribe.handle_subscribe({"email": "keine-mail"})
        check("ungueltige E-Mail meldet nicht", anrufe == [])


def test_fehler_bricht_nichts():
    print("Telegram nicht erreichbar: Anmeldung gilt trotzdem")
    anrufe, urlopen = anrufe_mitschreiben(fehler=True)
    with env(**FAKE_ENV), patched(_telegram.urllib.request, urlopen=urlopen), anmeldung_klappt():
        code, res = subscribe.handle_subscribe({"email": TEST_MAIL})
    check("Anmeldung gilt", code == 200 and res.get("stored"))
    check("Versuch fand statt", len(anrufe) == 1)


if __name__ == "__main__":
    for fn in (test_ohne_einrichtung, test_meldung, test_keine_meldung, test_fehler_bricht_nichts):
        fn()
    print()
    if FAILS:
        print("FEHLGESCHLAGEN: %d" % len(FAILS))
        for f in FAILS:
            print(" - " + f)
        sys.exit(1)
    print("Telegram-Meldung bestaetigt.")
