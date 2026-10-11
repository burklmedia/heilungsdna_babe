"""
Selbsttest fuer /api/hoeren (Bauplan vorlesen). Ohne Netzwerk, ohne ElevenLabs:

    python3 tests/test_hoeren.py
"""
import base64
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

import hoeren  # noqa: E402
from analyze import build_result  # noqa: E402

FAILS = []
GEBURT = {"name": "Marie", "gender": "weiblich", "date": "1994-06-14", "time": "08:42", "place": "Köln",
          "lat": 50.94, "lon": 6.96, "tz": "Europe/Berlin"}


def check(name, cond):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


def d_param(b):
    return base64.urlsafe_b64encode(json.dumps(b, ensure_ascii=False).encode()).decode().rstrip("=")


def test_sprechtext():
    print("Sprechtext: aus dem Bericht, Denises Verbote, Laenge")
    t = hoeren.sprechtext(build_result(GEBURT)["full"], "Marie")
    saetze = re.findall(r"[^.!?]+[.!?]+", t)
    check("beginnt mit dem Namen", t.startswith("Hallo Marie."))
    check("kein Satz beginnt mit Vielleicht, Manchmal, Stell dir vor",
          not any(re.match(r"\s*(Vielleicht|Manchmal|Stell dir vor)\b", s) for s in saetze))
    check("keine Gedankenstriche", "–" not in t and "—" not in t)
    check("kein Emoji", not re.search(r"[\U0001F300-\U0001FAFF☀-➿]", t))
    check("kein Geburtsdatum oder Ort im Text", "1994" not in t and "Köln" not in t and "08:42" not in t)
    check("rund zwei Minuten (150 bis 330 Woerter)", 150 <= len(t.split()) <= 330)
    check("Profil ausgeschrieben", "1/3" not in t)


def test_handle():
    print("Schnittstelle: Eingaben, Schluessel, Grenzen")
    alt = hoeren.kv_incr_ttl
    try:
        hoeren.kv_incr_ttl = lambda k, ttl: 1
        code, art, _ = hoeren.handle({"d": "x"})
        check("ungueltiger Parameter 400", code == 400)
        os.environ.pop("ELEVENLABS_API_KEY", None)
        code, art, daten = hoeren.handle({"d": d_param(GEBURT)})
        check("ohne Schluessel 503 mit Hinweis", code == 503 and "Vorlesen" in daten.decode("utf-8"))
        hoeren.kv_incr_ttl = lambda k, ttl: hoeren.PRO_GERAET + 1 if ":rl:" in k else 1
        code, _, daten = hoeren.handle({"d": d_param(GEBURT)})
        check("Geraete-Grenze 429", code == 429)
        hoeren.kv_incr_ttl = lambda k, ttl: 1 if ":rl:" in k else 10 ** 6
        code, _, _ = hoeren.handle({"d": d_param(GEBURT)})
        check("Tages-Grenze 429", code == 429)
        aufrufe = []
        hoeren.kv_incr_ttl = lambda k, ttl: 1
        alt_tts = hoeren.tts
        hoeren.tts = lambda text: (aufrufe.append(text) or b"ID3audio", None)
        code, art, daten = hoeren.handle({"d": d_param(GEBURT)})
        hoeren.tts = alt_tts
        check("mit Stimme 200 und MP3", code == 200 and art == "audio/mpeg" and daten == b"ID3audio")
        check("genau ein Vorlese-Aufruf", len(aufrufe) == 1)
    finally:
        hoeren.kv_incr_ttl = alt


if __name__ == "__main__":
    for fn in (test_sprechtext, test_handle):
        fn()
    print()
    if FAILS:
        print("FEHLGESCHLAGEN: %d" % len(FAILS))
        for f in FAILS:
            print(" - " + f)
        sys.exit(1)
    print("Vorlesen bestaetigt.")
