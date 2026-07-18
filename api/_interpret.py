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

# Chiron – „die Urwunde und zugleich der Ort deiner größten Heilkraft" – nach Zeichen
CHIRON_SIGN = {
    "Widder": "Deine Wunde berührt das schlichte Recht, dazusein und zu wollen. Deine Heilung: "
              "deinen Platz einnehmen, ohne dich dafür zu entschuldigen – und andere darin bestärken.",
    "Stier": "Deine Wunde dreht sich um Wert und Sicherheit. Deine Heilung: zu spüren, dass dein "
             "Wert nicht an Besitz oder Leistung hängt – du bist wertvoll, einfach so.",
    "Zwillinge": "Deine Wunde sitzt in Stimme und Gehörtwerden. Deine Heilung: dein eigenes Wort "
                 "ernst zu nehmen und auszusprechen – auch wenn es zittert.",
    "Krebs": "Deine Wunde berührt Zugehörigkeit und Geborgenheit. Deine Heilung: dir selbst zur "
             "Heimat zu werden, statt sie nur im Außen zu suchen.",
    "Löwe": "Deine Wunde liegt im Gesehenwerden und im schöpferischen Ausdruck. Deine Heilung: "
            "dich zu zeigen, weil es dich freut – nicht, weil du Applaus brauchst.",
    "Jungfrau": "Deine Wunde flüstert, du seist nicht gut genug. Deine Heilung: das Unvollkommene "
                "anzunehmen und zu erkennen, dass du schon jetzt genügst.",
    "Waage": "Deine Wunde zeigt sich in Beziehungen und im Ringen um Fairness. Deine Heilung: "
             "in Verbindung bei dir zu bleiben, statt dich selbst zu verlieren.",
    "Skorpion": "Deine Wunde berührt Ohnmacht und Tiefe. Deine Heilung: dem Wandel zu vertrauen – "
                "was zerbricht, macht Platz für das, was echter ist.",
    "Schütze": "Deine Wunde sitzt im Sinn und im Glauben. Deine Heilung: deiner eigenen Wahrheit "
               "zu folgen statt geliehener Überzeugungen.",
    "Steinbock": "Deine Wunde dreht sich um Autorität und Leistung. Deine Heilung: deinen Wert "
                 "jenseits von Erfolg und Anerkennung zu fühlen.",
    "Wassermann": "Deine Wunde ist das Gefühl, anders und außen vor zu sein. Deine Heilung: dein "
                  "Anderssein als Geschenk zu feiern – genau da gehörst du hin.",
    "Fische": "Deine Wunde berührt Grenzen und eine große Sehnsucht. Deine Heilung: Mitgefühl "
              "zuerst dir selbst zu schenken und deine Weichheit als Stärke zu sehen.",
}


def profile_name(profile):
    return PROFILE_NAMES.get(profile, " / ".join(
        PROFILE_LINES.get(int(x), "") for x in profile.split("/")))


PROFILE_DESC = {
    "1/3": "Du brauchst festen Boden unter den Füßen – und lernst zugleich durch Ausprobieren, was trägt.",
    "1/4": "Du gräbst in die Tiefe und teilst dein Wissen mit den Menschen, die dir nahe sind.",
    "2/4": "Du hast ein natürliches Talent, das erst durch andere gerufen wird – dein Netzwerk trägt dich.",
    "2/5": "Du bist die stille Begabte, die immer wieder für Lösungen nach vorn geholt wird.",
    "3/5": "Du lernst durch Erfahrung und wirst zur Person, die für andere Probleme löst.",
    "3/6": "Erst probierst du dich durchs Leben, dann wirst du zum lebenden Vorbild.",
    "4/6": "Du baust auf Beziehungen und reifst mit den Jahren zu einem Menschen, dem man vertraut.",
    "4/1": "Du stehst auf festem Fundament und wirkst über deine engen Verbindungen.",
    "5/1": "Man projiziert Erwartungen auf dich – dein solides Wissen macht dich zur Retterin in der Not.",
    "5/2": "Du wirst für praktische Lösungen gerufen und ziehst dich danach wieder gern zurück.",
    "6/2": "Du bist ein natürliches Vorbild mit einer Gabe, die andere in dir sehen.",
    "6/3": "Du reifst über drei Lebensphasen zu einem weisen, geerdeten Vorbild.",
}


def teaser(chart):
    """Der kostenlose Funke – jetzt ausführlicher, aber ohne das volle Bild."""
    hd = chart["hd"]
    t = TYPE_INFO.get(hd["type"], {})
    sun = chart["natal"]["Sonne"]
    moon = chart["natal"]["Mond"]
    defined = hd.get("defined_centers", [])
    return {
        "type": hd["type"],
        "type_short": t.get("short", ""),
        "profile": hd["profile"],
        "profile_name": profile_name(hd["profile"]),
        "profile_desc": PROFILE_DESC.get(hd["profile"], ""),
        "authority": hd["authority"],
        "authority_desc": AUTHORITY_INFO.get(hd["authority"], ""),
        "strategy": t.get("strategy", ""),
        "signature": t.get("signature", ""),
        "not_self": t.get("not_self", ""),
        "aura": t.get("aura", ""),
        "hook": t.get("short", ""),
        "sun_sign": sun["sign"],
        "moon_sign": moon["sign"],
        "defined_centers": defined,
        "definition": hd.get("definition", ""),
        # Was hinter dem E-Mail-Gate wartet (Appetitmacher, ohne Inhalt):
        "locked_preview": [
            "Dein vollständiges Geburtshoroskop – alle Planeten auf die Bogenminute",
            "Dein Aszendent & Medium Coeli – wie du wirkst und wohin dein Weg zeigt",
            "Dein Chiron – deine Urwunde und der Ort deiner größten Heilkraft",
            "Deine definierten & offenen Zentren – wo du Kraft schöpfst, wo du dich verlierst",
            "Deine persönliche Deutung in Klartext – dein roter Faden fürs Leben",
        ],
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

    defined = hd.get("defined_centers", [])
    open_c = hd.get("open_centers", [])
    sections.append({
        "title": "Deine Zentren",
        "headline": f"{len(defined)} definiert · {len(open_c)} offen",
        "body": "Definierte Zentren sind deine verlässliche, gleichbleibende Energie – hier bist "
                "du dir treu und kannst dich auf dich verlassen. Offene Zentren sind deine "
                "Weisheits- und Lernräume: Hier nimmst du andere feinfühlig auf und bist formbar – "
                "und genau hier entsteht Druck, wenn du dich verbiegst, um dazuzugehören.",
        "facts": [("Definiert", ", ".join(defined) or "keine"),
                  ("Offen", ", ".join(open_c) or "keine")],
    })

    chi = chart["natal"].get("Chiron")
    if chi:
        facts = [("Stellung", f"{chi['sym']} {chi['sign']} {chi['text']}")]
        if chi.get("house"):
            facts.append(("Haus", f"H{chi['house']}"))
        sections.append({
            "title": "Dein Chiron – Wunde & Heilung",
            "headline": f"Chiron in {chi['sign']} {chi['text']}",
            "body": CHIRON_SIGN.get(chi["sign"], "Chiron zeigt die Stelle, an der du verletzlich "
                    "bist – und genau dort liegt deine besondere Kraft, andere zu heilen."),
            "facts": facts,
        })

    natal_rows = []
    for b in ["Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn",
              "Uranus", "Neptun", "Pluto", "Chiron", "Nordknoten", "Südknoten"]:
        p = chart["natal"].get(b)
        if not p:
            continue
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
