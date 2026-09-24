"""
Selbsttest fuer die ActiveCampaign-Anbindung des Bauplans.
Laeuft ohne Netzwerk, ohne KV und ohne echte Schluessel:

    python3 tests/test_activecampaign.py

Geprueft werden die Anmeldung ueber das AC-Formular (api/subscribe.py) und
das Setzen von Feldern bei bestehenden Kontakten (api/_ac.py), dazu wie
Feedback und Themenwahl damit umgehen. Alle Netzwerkaufrufe laufen gegen
eine Attrappe, es werden nur synthetische Adressen verwendet.
"""
import contextlib
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

import _ac  # noqa: E402
import subscribe  # noqa: E402
import topic  # noqa: E402
import feedback  # noqa: E402

FAILS = []
TEST_MAIL = "lena.test@beispiel.de"
TEST_KEY = "testschluessel-123"


def check(name, cond):
    if cond:
        print("  ok   " + name)
    else:
        print("  FAIL " + name)
        FAILS.append(name)


class FakeResponse:
    def __init__(self, body):
        self.body = body.encode("utf-8") if isinstance(body, str) else body

    def read(self, n=None):
        return self.body if n is None else self.body[:n]

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeNet:
    """Ersetzt urllib.request.urlopen. Antworten werden der Reihe nach
    ausgegeben: ein String/Dict ist eine Antwort, eine Exception wird geworfen."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.calls = []

    def __call__(self, req, timeout=None):
        body = req.data.decode("utf-8") if req.data else None
        self.calls.append({"url": req.full_url, "method": req.get_method(),
                           "headers": {k.lower(): v for k, v in req.header_items()},
                           "body": body, "timeout": timeout})
        if not self.answers:
            raise AssertionError("unerwarteter Netzwerkaufruf: " + req.full_url)
        a = self.answers.pop(0)
        if isinstance(a, Exception):
            raise a
        return FakeResponse(json.dumps(a) if isinstance(a, dict) else a)


def http_error(code):
    return urllib.error.HTTPError("https://x.invalid", code, "err", {}, io.BytesIO(b""))


@contextlib.contextmanager
def net(*answers):
    fake = FakeNet(*answers)
    old = urllib.request.urlopen
    urllib.request.urlopen = fake
    try:
        yield fake
    finally:
        urllib.request.urlopen = old


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


@contextlib.contextmanager
def form(u="3", f="7", or_="00000000-test-form"):
    old = dict(subscribe.FORM)
    subscribe.FORM.update({"u": u, "f": f, "or": or_})
    try:
        yield
    finally:
        subscribe.FORM.clear()
        subscribe.FORM.update(old)


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


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = fn(*a, **k)
    return res, buf.getvalue()


D_OK = "eyJuYW1lIjoiTGVuYSIsImRhdGUiOiIxOTkwLTA1LTE3In0"


# ---------------------------------------------------------------------------
# Anmeldung ueber das Formular
# ---------------------------------------------------------------------------

def test_subscribe_validation():
    print("Anmeldung: Eingaben pruefen, bevor irgendetwas rausgeht")
    with form(), net() as fake:
        (code, res), _ = quiet(subscribe.handle_subscribe, {"email": "keine-mail", "name": "Lena"})
        check("kaputte Adresse -> 400", code == 400 and res.get("ok") is False)
        (code, res), _ = quiet(subscribe.handle_subscribe, {"email": "a@b.de" + "x" * 260})
        check("ueberlange Adresse -> 400", code == 400)
        (code, res), _ = quiet(subscribe.handle_subscribe, {"email": ["a@b.de"]})
        check("Adresse kein Text -> 400", code == 400)
        check("dabei kein Netzwerkaufruf", fake.calls == [])


def test_form_connected():
    print("Anmeldung: Formular 5 ist verbunden")
    check("u, f und or gesetzt", subscribe.form_connected())
    check("Formular 5", subscribe.FORM["f"] == "5")
    check("Bauplan-Link = field[4], Token = field[5]",
          subscribe.FELD_BAUPLAN_PDF == "field[4]" and subscribe.FELD_FEEDBACK_TOKEN == "field[5]")


def test_subscribe_not_connected():
    print("Anmeldung: ohne verbundenes Formular keine stille Annahme")
    with form("", "", ""), net() as fake, patched(subscribe, kv_set=lambda *a, **k: True):
        (code, res), _ = quiet(subscribe.handle_subscribe, {"email": TEST_MAIL, "name": "Lena"})
    check("503 not_configured", code == 503 and res.get("error") == "not_configured")
    check("stored=false, damit die Seite einen Fehler zeigt", res.get("stored") is False)
    check("kein Netzwerkaufruf", fake.calls == [])


def test_subscribe_payload():
    print("Anmeldung: Datensatz an proc.php")
    with form(), net("_show_thank_you(7, 'Danke', '', '')") as fake, \
            patched(subscribe, kv_set=lambda *a, **k: True):
        (code, res), log = quiet(subscribe.handle_subscribe,
                                 {"email": "  " + TEST_MAIL + " ", "name": "  Lena  " + "x" * 100, "d": D_OK})
    check("200 und stored", code == 200 and res == {"ok": True, "stored": True})
    check("genau ein Aufruf", len(fake.calls) == 1)
    call = fake.calls[0]
    sent = dict(urllib.parse.parse_qsl(call["body"], keep_blank_values=True))
    check("Endpunkt ist proc.php von burkl-media",
          call["url"] == "https://burkl-media.activehosted.com/proc.php" and call["method"] == "POST")
    check("als Formular kodiert", call["headers"].get("content-type") == "application/x-www-form-urlencoded")
    check("Formular-IDs u, f, or", sent.get("u") == "3" and sent.get("f") == "7"
          and sent.get("or") == "00000000-test-form")
    check("act=sub, v=2, jsonp=true", sent.get("act") == "sub" and sent.get("v") == "2" and sent.get("jsonp") == "true")
    check("E-Mail getrimmt", sent.get("email") == TEST_MAIL)
    check("Vorname getrimmt und auf 80 Zeichen", sent.get("firstname", "").startswith("Lena")
          and len(sent.get("firstname", "")) == 80)
    check("Bauplan-Link in field[4]", sent.get("field[4]") == D_OK)
    check("Feedback-Token in field[5]", len(sent.get("field[5]", "")) >= 20)
    check("keine weiteren Felder", set(sent) == {"u", "f", "s", "c", "m", "act", "v", "or", "email",
                                                  "firstname", "jsonp", "field[4]", "field[5]"})
    check("keine E-Mail im Log", TEST_MAIL not in log)


def test_subscribe_optional_fields():
    print("Anmeldung: Bauplan-Link und Token nur, wenn gueltig bzw. gespeichert")
    for label, d in (("Sonderzeichen", "abc$%&"), ("zu lang", "a" * 2001), ("kein Text", 12345)):
        with form(), net("_show_thank_you()") as fake, patched(subscribe, kv_set=lambda *a, **k: True):
            (code, res), _ = quiet(subscribe.handle_subscribe, {"email": TEST_MAIL, "name": "Lena", "d": d})
        sent = dict(urllib.parse.parse_qsl(fake.calls[0]["body"], keep_blank_values=True))
        check("d %s -> ohne field[4], Anmeldung laeuft trotzdem" % label,
              code == 200 and "field[4]" not in sent)
    with form(), net("_show_thank_you()") as fake, patched(subscribe, kv_set=lambda *a, **k: False):
        (code, res), _ = quiet(subscribe.handle_subscribe, {"email": TEST_MAIL, "name": "Lena", "d": D_OK})
    sent = dict(urllib.parse.parse_qsl(fake.calls[0]["body"], keep_blank_values=True))
    check("ohne KV kein Token (waere nicht aufloesbar)", code == 200 and "field[5]" not in sent)


def test_subscribe_errors():
    print("Anmeldung: Fehler von ActiveCampaign landen als Fehler auf der Seite")
    cases = (
        ("_show_error", "_show_error('7', 'Formulare müssen ein E-Mail-Feld enthalten', '', '')", "upstream_rejected"),
        ("HTTP 500", http_error(500), "upstream_http"),
        ("nicht erreichbar", urllib.error.URLError("timed out"), "upstream_unreachable"),
    )
    for label, answer, error in cases:
        with form(), net(answer), patched(subscribe, kv_set=lambda *a, **k: True):
            (code, res), log = quiet(subscribe.handle_subscribe, {"email": TEST_MAIL, "name": "Lena"})
        check("%s -> 502 %s" % (label, error), code == 502 and res.get("error") == error)
        check("%s -> stored=false" % label, res.get("stored") is False)
        check("%s -> keine E-Mail im Log" % label, TEST_MAIL not in log)


def test_subscribe_dry_run():
    print("Anmeldung: lokaler Probelauf schickt nichts")
    with form("", "", ""), net() as fake, patched(subscribe, DRY_RUN=True, kv_set=lambda *a, **k: True):
        (code, res), _ = quiet(subscribe.handle_subscribe, {"email": TEST_MAIL, "name": "Lena", "d": D_OK})
    check("200 mit dry_run, auch ohne verbundenes Formular", code == 200 and res.get("dry_run") is True)
    check("kein Netzwerkaufruf", fake.calls == [])


# ---------------------------------------------------------------------------
# Felder bei bestehenden Kontakten
# ---------------------------------------------------------------------------

def test_api_base():
    print("AC_API_URL: nur echte ActiveCampaign-Adressen")
    check("api-us1 mit Schraegstrich", _ac.api_base("https://burkl-media.api-us1.com/") == "https://burkl-media.api-us1.com")
    check("activehosted mit Pfad", _ac.api_base("https://burkl-media.activehosted.com/api/3") == "https://burkl-media.activehosted.com")
    for bad in ("http://burkl-media.api-us1.com", "https://example.com", "https://burkl-media.api-us1.com:8443",
                "https://u:p@burkl-media.api-us1.com", "", None, "https://burkl-media.api-us1.com.evil.de"):
        check("abgelehnt: %r" % (bad,), _ac.api_base(bad) is None)


def test_set_fields_not_configured():
    print("Felder: ohne Schluessel kein Aufruf")
    with env(AC_API_URL=None, AC_API_KEY=None), net() as fake:
        res, _ = quiet(_ac.set_fields, TEST_MAIL, {"6": "yes"})
    check("nicht_konfiguriert", res == (False, "nicht_konfiguriert"))
    check("kein Netzwerkaufruf", fake.calls == [])
    with env(AC_API_URL="https://example.com", AC_API_KEY=TEST_KEY), net() as fake:
        res, _ = quiet(_ac.set_fields, TEST_MAIL, {"6": "yes"})
    check("fremde Adresse -> ungueltige_adresse ohne Aufruf", res == (False, "ungueltige_adresse") and fake.calls == [])


def test_set_fields_existing_contact():
    print("Felder: bestehender Kontakt wird aktualisiert")
    found = {"contacts": [{"id": "41", "email": "andere@beispiel.de"}, {"id": "42", "email": "Lena.Test@Beispiel.de"}]}
    with env(AC_API_URL="https://burkl-media.api-us1.com", AC_API_KEY=TEST_KEY), \
            net(found, {"contact": {"id": "42"}}) as fake:
        res, log = quiet(_ac.set_fields, " Lena.Test@beispiel.de ", {"6": "yes"})
    check("gesetzt", res == (True, "gesetzt"))
    check("zwei Aufrufe: suchen, dann aendern", len(fake.calls) == 2)
    get, put = fake.calls[0], fake.calls[1]
    check("Suche per E-Mail, klein geschrieben und kodiert",
          get["method"] == "GET" and get["url"] == "https://burkl-media.api-us1.com/api/3/contacts?email=lena.test%40beispiel.de")
    check("Schluessel im Kopf Api-Token", get["headers"].get("api-token") == TEST_KEY)
    check("PUT auf den passenden Kontakt 42", put["method"] == "PUT"
          and put["url"] == "https://burkl-media.api-us1.com/api/3/contacts/42")
    check("nur fieldValues im Body", json.loads(put["body"]) == {"contact": {"fieldValues": [{"field": "6", "value": "yes"}]}})
    check("Zeitlimit gesetzt", all(c["timeout"] for c in fake.calls))
    check("weder E-Mail noch Schluessel im Log", TEST_MAIL not in log and TEST_KEY not in log)


def test_set_fields_never_creates():
    print("Felder: unbekannte Adresse wird nie angelegt")
    with env(AC_API_URL="https://burkl-media.api-us1.com", AC_API_KEY=TEST_KEY), \
            net({"contacts": [{"id": "41", "email": "andere@beispiel.de"}]}) as fake:
        res, _ = quiet(_ac.set_fields, TEST_MAIL, {"7": "decision"})
    check("kein_kontakt", res == (False, "kein_kontakt"))
    check("nur die Suche, kein Schreibaufruf", len(fake.calls) == 1 and fake.calls[0]["method"] == "GET")


def test_set_fields_errors():
    print("Felder: Fehler werfen nie")
    with env(AC_API_URL="https://burkl-media.api-us1.com", AC_API_KEY=TEST_KEY):
        with net(http_error(403)):
            res, log = quiet(_ac.set_fields, TEST_MAIL, {"6": "yes"})
        check("403 -> http_403", res == (False, "http_403"))
        with net(urllib.error.URLError(TimeoutError("timed out"))):
            res, log = quiet(_ac.set_fields, TEST_MAIL, {"6": "yes"})
        check("Zeitueberschreitung -> timeout", res == (False, "timeout"))
        with net(urllib.error.URLError(OSError("Name or service not known burkl-media.api-us1.com"))):
            res, log = quiet(_ac.set_fields, TEST_MAIL, {"6": "yes"})
        check("Netzfehler -> netz", res == (False, "netz"))
        check("Adresse aus der Fehlermeldung nicht im Log", "api-us1" not in log)


def test_update_contact_transition():
    print("Uebergang: Altkontakte aus MailerLite")
    ac = dict(AC_API_URL="https://burkl-media.api-us1.com", AC_API_KEY=TEST_KEY)
    with env(MAILERLITE_API_KEY="ml-test", **ac), \
            net({"contacts": [{"id": "42", "email": TEST_MAIL}]}, {"contact": {"id": "42"}}) as fake:
        res, _ = quiet(_ac.update_contact, TEST_MAIL, {"feedback_given": "yes"})
    check("AC-Kontakt -> activecampaign, MailerLite unberuehrt",
          res == (True, "activecampaign") and all("mailerlite" not in c["url"] for c in fake.calls))
    with env(MAILERLITE_API_KEY="ml-test", **ac), net({"contacts": []}, {"data": {"id": "9"}}, {"data": {"id": "9"}}) as fake:
        res, _ = quiet(_ac.update_contact, TEST_MAIL, {"beta_topic": "energy"})
    check("nur in MailerLite -> mailerlite", res == (True, "mailerlite"))
    ml = [c for c in fake.calls if "mailerlite" in c["url"]]
    check("MailerLite: erst pruefen, dann Feld setzen", [c["method"] for c in ml] == ["GET", "POST"])
    check("MailerLite bekommt den alten Feldnamen",
          json.loads(ml[1]["body"]) == {"email": TEST_MAIL, "fields": {"beta_topic": "energy"}})
    with env(MAILERLITE_API_KEY="ml-test", **ac), net({"contacts": []}, http_error(404)) as fake:
        res, _ = quiet(_ac.update_contact, TEST_MAIL, {"beta_topic": "energy"})
    check("in keinem Dienst -> Fehler", res[0] is False)
    check("MailerLite legt nie an (kein POST nach 404)", all(c["method"] != "POST" for c in fake.calls))
    with env(MAILERLITE_API_KEY=None, **ac), net({"contacts": []}) as fake:
        res, _ = quiet(_ac.update_contact, TEST_MAIL, {"beta_topic": "energy"})
    check("ohne MailerLite-Schluessel kein Umweg", res == (False, "kein_kontakt") and len(fake.calls) == 1)


# ---------------------------------------------------------------------------
# Feedback und Themenwahl
# ---------------------------------------------------------------------------

def test_topic_requires_contact_write():
    print("Themenwahl: ohne Write beim Kontakt keine Zaehlung, Sperre wird frei")
    deleted, counted = [], []
    with patched(topic, kv_get=lambda k: TEST_MAIL, kv_setnx=lambda k, v, ttl=None: True,
                 kv_del=lambda k: deleted.append(k) or True, incr=lambda keys: counted.extend(keys),
                 update_contact=lambda email, fields: (False, "kein_kontakt")):
        code, res = topic.handle_topic({"t": "tok123", "topic": "energy"})
    check("503 crm_failed", code == 503 and res.get("error") == "crm_failed")
    check("Sperre wieder frei", deleted == ["imh:topicdone:tok123"])
    check("nichts gezaehlt", counted == [])
    seen = []
    with patched(topic, kv_get=lambda k: TEST_MAIL, kv_setnx=lambda k, v, ttl=None: True,
                 kv_del=lambda k: True, incr=lambda keys: counted.extend(keys),
                 update_contact=lambda email, fields: seen.append((email, fields)) or (True, "activecampaign")):
        code, res = topic.handle_topic({"t": "tok123", "topic": "energy"})
    check("Erfolg -> 200", code == 200 and res.get("ok") is True)
    check("Feld beta_topic mit der aufgeloesten E-Mail", seen == [(TEST_MAIL, {"beta_topic": "energy"})])
    check("danach gezaehlt", any(k.endswith("topic:energy") for k in counted))


def test_feedback_best_effort():
    print("Feedback: Speichern klappt auch, wenn der Kontakt-Write scheitert")
    seen = []
    with patched(feedback, kv_get=lambda k: TEST_MAIL, kv_setnx=lambda k, v, ttl=None: True,
                 kv_del=lambda k: True, push_feedback=lambda r, key="imh:feedback": True,
                 update_contact=lambda email, fields: seen.append(fields) or (False, "netz")):
        code, res = feedback.handle_feedback({"t": "tok123", "helpfulness_score": "9"})
    check("200 und gespeichert", code == 200 and res.get("stored") is True)
    check("crm=false gemeldet", res.get("crm") is False)
    check("feedback_given=yes versucht", seen == [{"feedback_given": "yes"}])


if __name__ == "__main__":
    for fn in (
        test_form_connected,
        test_subscribe_validation,
        test_subscribe_not_connected,
        test_subscribe_payload,
        test_subscribe_optional_fields,
        test_subscribe_errors,
        test_subscribe_dry_run,
        test_api_base,
        test_set_fields_not_configured,
        test_set_fields_existing_contact,
        test_set_fields_never_creates,
        test_set_fields_errors,
        test_update_contact_transition,
        test_topic_requires_contact_write,
        test_feedback_best_effort,
    ):
        fn()
    print()
    if FAILS:
        print("FEHLGESCHLAGEN: %d" % len(FAILS))
        for f in FAILS:
            print(" - " + f)
        sys.exit(1)
    print("ActiveCampaign-Anbindung bestaetigt.")
