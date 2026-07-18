"""
Textbausteine für Intuition mit Herz.
Der Gratis-Einblick (teaser) und die Voll-Analyse (full_analysis) werden
deterministisch aus den exakten Chart-Daten gebaut — 0 € KI-Kosten.
Später kann die Voll-Analyse mit Claude noch persönlicher getextet werden;
die Zahlen bleiben immer die exakt berechneten aus _engine.py.
"""

TYPE_INFO = {
    "Generator": {
        "strategy": "Auf das Leben antworten",
        "signature": "Zufriedenheit", "not_self": "Frustration",
        "aura": "offen & umhüllend",
        "short": "Du bist die schöpferische Lebenskraft. Wenn du auf das antwortest, "
                 "was dich wirklich anzieht, wird deine Energie unerschöpflich.",
    },
    "Manifestierender Generator": {
        "strategy": "Antworten – und dann informieren",
        "signature": "Zufriedenheit & Frieden", "not_self": "Frustration & Wut",
        "aura": "offen & umhüllend",
        "short": "Du vereinst die Ausdauer des Generators mit der Schnelligkeit des "
                 "Manifestors. Du gehst mehrere Schritte auf einmal – und das ist richtig so.",
    },
    "Manifestor": {
        "strategy": "Informieren, bevor du handelst",
        "signature": "Frieden", "not_self": "Wut",
        "aura": "verschlossen & abstoßend (initiierend)",
        "short": "Du bist hier, um Dinge anzustoßen und in Bewegung zu bringen. Du "
                 "brauchst keine Erlaubnis – nur den Mut, dein Umfeld mitzunehmen.",
    },
    "Projektor": {
        "strategy": "Auf die Einladung warten",
        "signature": "Erfolg", "not_self": "Bitterkeit",
        "aura": "fokussiert & durchdringend",
        "short": "Du siehst andere und Systeme klarer als die meisten. Deine Gabe "
                 "entfaltet sich, wenn sie erkannt und eingeladen wird.",
    },
    "Reflektor": {
        "strategy": "Einen Mondzyklus abwarten",
        "signature": "Überraschung", "not_self": "Enttäuschung",
        "aura": "widerspiegelnd & abtastend",
        "short": "Du bist ein seltener Spiegel deiner Umgebung. Du fühlst, wie es einem "
                 "Ort und den Menschen darin wirklich geht – ein kostbares Geschenk.",
    },
}

AUTHORITY_INFO = {
    "Emotionale Autorität": "Deine Klarheit kommt nicht im Moment, sondern über die Zeit. "
        "Warte eine emotionale Welle ab – es gibt keine Wahrheit im Jetzt, nur im Verlauf.",
    "Sakrale Autorität": "Dein Bauch weiß es sofort. Ein spontanes Ja fühlt sich ausdehnend an, "
        "ein Nein zieht sich zusammen. Vertraue diesem Körperlaut vor dem Kopf.",
    "Milz-Autorität (Splenisch)": "Deine Wahrheit spricht leise und nur einmal – als spontane "
        "Ahnung im Hier und Jetzt. Lerne, diesem ersten Impuls zu trauen.",
    "Ego-/Herz-Autorität": "Entscheide aus dem, was dein Herz wirklich will und wofür deine "
        "Willenskraft brennt. Deine Wahrheit liegt in deinem echten Wollen.",
    "Selbst-projizierte Autorität": "Deine Wahrheit hörst du, wenn du sie aussprichst. Rede mit "
        "einem vertrauten Menschen – nicht um Rat, sondern um dich selbst zu hören.",
    "Mond-Autorität (Reflektor)": "Triff große Entscheidungen nicht überstürzt. Lass einen ganzen "
        "Mondzyklus vergehen und sprich mit vielen – die Klarheit reift von selbst.",
    "Mentale Autorität (Umgebung)": "Du hast keine innere Autorität im Körper – dein Umfeld ist "
        "dein Resonanzraum. Sprich alles aus und spüre, welche Umgebung sich stimmig anfühlt.",
}

PROFILE_LINES = {
    1: "Forscherin", 2: "Eremitin", 3: "Märtyrerin",
    4: "Netzwerkerin", 5: "Häretikerin", 6: "Vorbild",
}
PROFILE_NAMES = {
    "1/3": "Forscherin / Märtyrerin", "1/4": "Forscherin / Netzwerkerin",
    "2/4": "Eremitin / Netzwerkerin", "2/5": "Eremitin / Häretikerin",
    "3/5": "Märtyrerin / Häretikerin", "3/6": "Märtyrerin / Vorbild",
    "4/6": "Netzwerkerin / Vorbild", "4/1": "Netzwerkerin / Forscherin",
    "5/1": "Häretikerin / Forscherin", "5/2": "Häretikerin / Eremitin",
    "6/2": "Vorbild / Eremitin", "6/3": "Vorbild / Märtyrerin",
}

CENTER_MEANING = {
    "Kopf": "Inspiration & mentaler Druck", "Ajna": "Denken & Konzeptualisieren",
    "Kehle": "Ausdruck & Manifestation", "G": "Identität, Liebe & Richtung",
    "Herz": "Willenskraft & Selbstwert", "Milz": "Intuition, Gesundheit & Instinkt",
    "Sakral": "Lebenskraft & Arbeitsenergie", "Solarplexus": "Emotionen & Gefühlswellen",
    "Wurzel": "Antrieb, Stress & Druck",
}


def profile_name(profile):
    return PROFILE_NAMES.get(profile, " / ".join(
        PROFILE_LINES.get(int(x), "") for x in profile.split("/")))


def teaser(chart):
    """Der kleine kostenlose Funke – ein Fingerzeig, kein volles Bild."""
    hd = chart["hd"]
    t = TYPE_INFO.get(hd["type"], {})
    return {
        "type": hd["type"],
        "profile": hd["profile"],
        "profile_name": profile_name(hd["profile"]),
        "authority": hd["authority"],
        "strategy": t.get("strategy", ""),
        "hook": t.get("short", ""),
        "sun_sign": chart["natal"]["Sonne"]["sign"],
    }


def full_analysis(chart):
    """Die vollständige, liebevoll aufbereitete Analyse (nach E-Mail)."""
    hd = chart["hd"]
    t = TYPE_INFO.get(hd["type"], {})
    name = chart.get("name") or "du"
    sun = chart["natal"]["Sonne"]
    moon = chart["natal"]["Mond"]
    asc = chart.get("ascendant")

    sections = []
    sections.append({
        "title": "Dein Human-Design-Typ",
        "headline": hd["type"],
        "body": t.get("short", ""),
        "facts": [
            ("Strategie", t.get("strategy", "")),
            ("Innere Autorität", hd["authority"]),
            ("Signatur (im Flow)", t.get("signature", "")),
            ("Nicht-Selbst-Thema", t.get("not_self", "")),
        ],
    })
    sections.append({
        "title": "Deine innere Autorität",
        "headline": hd["authority"],
        "body": AUTHORITY_INFO.get(hd["authority"], ""),
        "facts": [],
    })
    sections.append({
        "title": "Dein Profil",
        "headline": f"{hd['profile']} · {profile_name(hd['profile'])}",
        "body": "Dein Profil beschreibt die Rolle, in der sich dein Weg entfaltet – "
                "die bewusste (erste Zahl) und die unbewusste Seite (zweite Zahl) deiner Natur.",
        "facts": [("Definition", hd["definition"]),
                  ("Definierte Zentren", ", ".join(hd["defined_centers"]) or "keine")],
    })

    natal_rows = []
    for b in ["Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn",
              "Uranus", "Neptun", "Pluto"]:
        p = chart["natal"][b]
        natal_rows.append({
            "sym": p.get("sym_body", ""), "body": b,
            "pos": f"{p['sym']} {p['sign']} {p['text']}",
            "house": p.get("house"),
        })
    natal_extra = []
    if asc:
        natal_extra.append({"sym": "AC", "body": "Aszendent",
                            "pos": f"{asc['sym']} {asc['sign']} {asc['text']}", "house": 1})
        mc = chart["mc"]
        natal_extra.append({"sym": "MC", "body": "Medium Coeli",
                           "pos": f"{mc['sym']} {mc['sign']} {mc['text']}", "house": 10})

    closing = (f"{name}, dein roter Faden: Lebe deine Strategie – "
               f"{t.get('strategy','').lower()} – und vertraue deiner {hd['authority']}. "
               f"Wenn sich etwas stimmig anfühlt, ist es dein Weg, auch wenn er "
               f"nicht der geradlinige ist. 🤍")

    return {
        "name": name,
        "hd": hd,
        "sections": sections,
        "natal_rows": natal_rows + natal_extra,
        "ascendant": asc,
        "closing": closing,
        "note": "Symbolische Deutung zur Selbstreflexion – kein Ersatz für Beratung, "
                "keine Diagnose. Alle Positionen exakt berechnet (tropisch, Ganzzeichen-Häuser).",
    }
