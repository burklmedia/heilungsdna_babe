"""
Selbsttest fuer die reinen Anteile der Bauplan-Uebergabe.
Laeuft ohne KV, ohne Netzwerk und ohne pyswisseph:

    python3 tests/test_handoff.py

Geprueft werden die Subset-Extraktion (stabile Codes, keine Geburtsdaten) und
die challenge/verifier-Bindung. Es werden ausschliesslich synthetische Daten
verwendet, niemals echte Kundendaten.
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

import handoff  # noqa: E402

FAILS = []


def check(name, cond):
    if cond:
        print("  ok   " + name)
    else:
        print("  FAIL " + name)
        FAILS.append(name)


# Synthetisches Ergebnis in der Form, die analyze.build_result liefert.
SYNTHETIC = {
    "ok": True,
    "birth": {
        "name": "Testperson", "date": "01.01.1990", "time": "12:00",
        "place": "Berlin", "gender": "w", "lat": 52.52, "lon": 13.405,
        "tz": "Europe/Berlin",
    },
    "teaser": {"sun_sign": "Löwe", "moon_sign": "Fische"},
    "full": {
        "hd": {
            "type": "Manifestierender Generator",
            "authority": "Emotionale Autorität",
            "profile": "1/3",
            "definition": "Einfache Definition",
            "defined_centers": ["Kehle", "Sakral", "Solarplexus"],
            "open_centers": ["Kopf", "Ajna"],
            "gates": [1, 2, 3],
            "channels": ["1-8"],
        },
        "ascendant": {"sign": "Jungfrau"},
        "intuition": {"archetype": "Feuer", "tagline": "irgendein Text"},
        "numerology": {"lifepath": 7, "is_master": False},
        "sections": ["viel Deutungsprosa"],
        "natal_rows": [{"x": 1}],
    },
}


def test_subset_mapping():
    print("build_subset: stabile Codes")
    s = handoff.build_subset(SYNTHETIC, time_known=True)
    check("contractVersion", s["contractVersion"] == 1)
    check("timeKnown", s["timeKnown"] is True)
    check("hd.type -> MANIFESTING_GENERATOR", s["hd"]["type"] == "MANIFESTING_GENERATOR")
    check("hd.authority -> EMOTIONAL", s["hd"]["authority"] == "EMOTIONAL")
    check("hd.profile", s["hd"]["profile"] == "1/3")
    check("definedCenters gemappt", s["hd"]["definedCenters"] == ["THROAT", "SACRAL", "SOLAR_PLEXUS"])
    check("openCenters gemappt", s["hd"]["openCenters"] == ["HEAD", "AJNA"])
    check("sunSign -> LEO", s["astro"]["sunSign"] == "LEO")
    check("moonSign -> PISCES", s["astro"]["moonSign"] == "PISCES")
    check("ascSign -> VIRGO", s["astro"]["ascSign"] == "VIRGO")
    check("intuition.archetype", s["intuition"]["archetype"] == "Feuer")
    check("numerology.lifepath", s["numerology"]["lifepath"] == 7)


def test_no_birth_data_leaks():
    print("build_subset: keine Geburts- oder Rohdaten")
    s = handoff.build_subset(SYNTHETIC, time_known=True)
    blob = json.dumps(s, ensure_ascii=False)
    for forbidden in ["Testperson", "01.01.1990", "12:00", "Berlin", "52.52", "13.405",
                      "Europe/Berlin", "Deutungsprosa", "gates", "channels", "natal"]:
        check("kein Leak: " + forbidden, forbidden not in blob)
    check("keine Tore/Kanaele im hd", "gates" not in s["hd"] and "channels" not in s["hd"])


def test_time_unknown():
    print("build_subset: Geburtszeit unbekannt")
    s = handoff.build_subset(SYNTHETIC, time_known=False)
    check("timeKnown false", s["timeKnown"] is False)
    check("kein Aszendent ohne Zeit", "ascSign" not in s.get("astro", {}))
    check("Sonne bleibt", s["astro"]["sunSign"] == "LEO")


def test_unknown_values_dropped():
    print("build_subset: unbekannte Werte werden verworfen, nicht geraten")
    weird = json.loads(json.dumps(SYNTHETIC))
    weird["full"]["hd"]["type"] = "Etwas Neues"
    weird["full"]["hd"]["authority"] = "Unbekannte Autorität"
    weird["full"]["hd"]["defined_centers"] = ["Kehle", "Quatschzentrum"]
    weird["teaser"]["sun_sign"] = "Schlangenträger"
    s = handoff.build_subset(weird, time_known=True)
    check("kein erfundener Typ", "type" not in s.get("hd", {}))
    check("keine erfundene Autoritaet", "authority" not in s.get("hd", {}))
    check("nur bekannte Zentren", s["hd"]["definedCenters"] == ["THROAT"])
    check("kein erfundenes Zeichen", "sunSign" not in s.get("astro", {}))


def test_empty_result():
    print("build_subset: leeres Ergebnis")
    s = handoff.build_subset({}, time_known=False)
    check("nur Huelle, nichts erfunden", set(s.keys()) == {"contractVersion", "timeKnown"})


def test_challenge_binding():
    print("challenge/verifier-Bindung")
    verifier = "zufaelliger-verifier-wert-1234567890"
    challenge = handoff._b64url_sha256(verifier)
    check("deterministisch", challenge == handoff._b64url_sha256(verifier))
    check("laenge 43 (base64url sha256 ohne Padding)", len(challenge) == 43)
    check("kein Padding", "=" not in challenge)
    check("anderer verifier -> andere challenge", challenge != handoff._b64url_sha256(verifier + "x"))
    check("verifier nicht rekonstruierbar", verifier not in challenge)


if __name__ == "__main__":
    for fn in (test_subset_mapping, test_no_birth_data_leaks, test_time_unknown,
               test_unknown_values_dropped, test_empty_result, test_challenge_binding):
        fn()
    print()
    if FAILS:
        print("FEHLGESCHLAGEN: %d" % len(FAILS))
        for f in FAILS:
            print(" - " + f)
        sys.exit(1)
    print("Alle Handoff-Selbsttests bestanden.")
