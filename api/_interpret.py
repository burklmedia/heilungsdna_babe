"""
Textbausteine für Intuition mit Herz.
Der Gratis-Einblick (teaser) und die Voll-Analyse (full_analysis) werden
deterministisch aus den exakten Chart-Daten gebaut (0 € KI-Kosten).
Ton: warm, klar, gefühlvoll, in Du-Form. Ohne Gedankenstriche, ohne
"nicht ... sondern"-Konstruktionen. Menschen sollen sich wiedererkennen.
Die Zahlen bleiben immer die exakt berechneten aus _engine.py.
"""

TYPE_INFO = {
    "Generator": {
        "strategy": "Auf das Leben antworten",
        "signature": "Zufriedenheit", "not_self": "Frustration",
        "aura": "offen & umhüllend",
        "short": "Du bist die schöpferische Lebenskraft dieser Welt. Wenn du auf das antwortest, "
                 "was dich wirklich anzieht, wird deine Energie unerschöpflich und deine Arbeit "
                 "zu etwas, das dich erfüllt statt auslaugt.",
    },
    "Manifestierender Generator": {
        "strategy": "Antworten und dann informieren",
        "signature": "Zufriedenheit & Frieden", "not_self": "Frustration & Wut",
        "aura": "offen & umhüllend",
        "short": "In dir vereinen sich die Ausdauer des Generators und die Schnelligkeit des "
                 "Manifestors. Du gehst gern mehrere Schritte auf einmal, springst, probierst und "
                 "findest Abkürzungen. Genau so bist du richtig, auch wenn andere kürzer treten.",
    },
    "Manifestor": {
        "strategy": "Informieren, bevor du handelst",
        "signature": "Frieden", "not_self": "Wut",
        "aura": "verschlossen & initiierend",
        "short": "Du bist hier, um Dinge anzustoßen und in Bewegung zu bringen. Du brauchst keine "
                 "Erlaubnis, um loszugehen. Du brauchst nur den Mut, dein Umfeld mitzunehmen, "
                 "bevor du startest, dann öffnen sich dir die Türen.",
    },
    "Projektor": {
        "strategy": "Auf die Einladung warten",
        "signature": "Erfolg", "not_self": "Bitterkeit",
        "aura": "fokussiert & durchdringend",
        "short": "Du siehst Menschen und Zusammenhänge klarer als die meisten. Deine Gabe entfaltet "
                 "sich, sobald sie erkannt und eingeladen wird. Dann führst du mit einer Weisheit, "
                 "die andere kaum aufbringen.",
    },
    "Reflektor": {
        "strategy": "Einen Mondzyklus abwarten",
        "signature": "Überraschung", "not_self": "Enttäuschung",
        "aura": "widerspiegelnd & abtastend",
        "short": "Du bist ein seltener Spiegel deiner Umgebung und fühlst, wie es einem Ort und den "
                 "Menschen darin wirklich geht. Das ist eine kostbare, fast magische Gabe, die es "
                 "nur bei ganz wenigen gibt.",
    },
}

AUTHORITY_INFO = {
    "Emotionale Autorität": "Deine Klarheit reift über die Zeit. Warte bei allem Wichtigen eine "
        "Gefühlswelle ab und schlaf ein paar Nächte darüber. Deine Wahrheit zeigt sich erst im "
        "Verlauf, wenn sich das Auf und Ab gelegt hat und Ruhe einkehrt.",
    "Sakrale Autorität": "Dein Bauch weiß es sofort. Ein echtes Ja fühlt sich weit und lebendig an, "
        "ein Nein zieht sich leise zusammen. Vertraue diesem Körperlaut noch vor dem Kopf, denn er "
        "lügt dich nie an.",
    "Milz-Autorität (Splenisch)": "Deine Wahrheit spricht leise und meist nur ein einziges Mal, als "
        "feine Ahnung im Augenblick. Lerne, diesem ersten, stillen Impuls zu trauen. Er schützt "
        "dich und führt dich sicherer, als jede lange Grübelei es könnte.",
    "Ego-/Herz-Autorität": "Deine Wahrheit liegt in deinem echten Wollen. Frag dich bei jeder "
        "Entscheidung, was dein Herz wirklich begehrt und wofür deine Kraft brennt, und geh von "
        "dort aus los.",
    "Selbst-projizierte Autorität": "Deine Wahrheit hörst du, wenn du sie aussprichst. Rede mit "
        "einem vertrauten Menschen und lausche dabei vor allem deiner eigenen Stimme. In deinen "
        "eigenen Worten liegt schon die Antwort.",
    "Mond-Autorität (Reflektor)": "Lass große Entscheidungen einen ganzen Mondzyklus reifen. Sprich "
        "mit vielen Menschen und schlaf viele Nächte darüber. Die Klarheit stellt sich von ganz "
        "allein ein, wenn du ihr die Zeit gibst.",
    "Mentale Autorität (Umgebung)": "Dein Umfeld ist dein Resonanzraum. Sprich alles laut aus und "
        "spüre genau, an welchem Ort und mit welchen Menschen dein Weg sich stimmig anfühlt. Die "
        "richtige Umgebung zeigt dir deine Richtung.",
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
PROFILE_DESC = {
    "1/3": "Du brauchst festen Boden unter den Füßen und ein sicheres Fundament aus Wissen. "
           "Zugleich lernst du durch eigenes Ausprobieren, durch Versuch und Irrtum, was im Leben "
           "wirklich trägt.",
    "1/4": "Du gräbst gern in die Tiefe, bis du eine Sache wirklich verstanden hast, und teilst "
           "dein Wissen dann mit den Menschen, die dir nahe sind. Über sie öffnen sich dir Wege.",
    "2/4": "Du trägst ein natürliches Talent in dir, das oft im Verborgenen ruht, bis andere es "
           "in dir sehen und dich rufen. Dein Netzwerk trägt dich, wenn du dich rufen lässt.",
    "2/5": "Du bist die stille Begabte, die sich gern zurückzieht und doch immer wieder nach vorn "
           "geholt wird, um eine Lösung zu bringen.",
    "3/5": "Du lernst durch eigene Erfahrung, mit allen Umwegen, und wirst zu der Person, die für "
           "andere praktische Lösungen findet, weil sie selbst durch vieles gegangen ist.",
    "3/6": "Zuerst probierst du dich durchs Leben, mit Höhen und Tiefen und manchem Umweg. Später "
           "wächst du zu einem lebenden Vorbild heran, das aus echter Erfahrung spricht.",
    "4/6": "Du baust auf echte, warme Beziehungen und reifst mit den Jahren zu einem Menschen, dem "
           "andere von Herzen vertrauen.",
    "4/1": "Du stehst auf einem festen Fundament und wirkst vor allem über deine engen, "
           "verlässlichen Verbindungen in die Welt.",
    "5/1": "Menschen projizieren viel auf dich und erwarten Lösungen, oft mehr, als dir bewusst "
           "ist. Dein solides, tiefes Wissen macht dich zu der, die in der Not wirklich hilft.",
    "5/2": "Du wirst für praktische Lösungen gerufen und ziehst dich danach gern wieder in deinen "
           "eigenen, ruhigen Raum zurück.",
    "6/2": "Du bist ein natürliches Vorbild mit einer Gabe, die andere oft früher in dir sehen als "
           "du selbst.",
    "6/3": "Du reifst über drei Lebensphasen hinweg, mit viel Erfahrung, zu einem weisen und "
           "geerdeten Vorbild.",
}

CENTER_MEANING = {
    "Kopf": "Inspiration und mentaler Druck", "Ajna": "Denken und Verstehen",
    "Kehle": "Ausdruck und Manifestation", "G": "Identität, Liebe und Richtung",
    "Herz": "Willenskraft und Selbstwert", "Milz": "Intuition, Gesundheit und Instinkt",
    "Sakral": "Lebenskraft und Arbeitsenergie", "Solarplexus": "Emotionen und Gefühlswellen",
    "Wurzel": "Antrieb, Druck und Stress",
}

# Chiron: die tiefe Wunde und zugleich der Ort deiner größten Heilkraft, nach Zeichen.
CHIRON_SIGN = {
    "Widder": "Deine tiefste Wunde berührt das schlichte Recht, da zu sein und zu wollen. Deine "
              "Heilung liegt darin, deinen Platz einzunehmen, ohne dich dafür zu entschuldigen, "
              "und andere in genau diesem Mut zu bestärken.",
    "Stier": "Deine Wunde dreht sich um Wert und Sicherheit und um die leise Angst, nicht genug zu "
             "haben. Deine Heilung beginnt in dem Moment, in dem du spürst, dass dein Wert an "
             "nichts hängt und du kostbar bist, einfach weil es dich gibt.",
    "Zwillinge": "Deine Wunde sitzt in deiner Stimme und im Gehörtwerden. Deine Heilung geschieht, "
                 "wenn du dein eigenes Wort ernst nimmst und aussprichst, auch dann, wenn es "
                 "zittert.",
    "Krebs": "Deine Wunde berührt Zugehörigkeit und Geborgenheit, das Gefühl, irgendwo wirklich "
             "hinzugehören. Deine Heilung liegt darin, dir selbst zur Heimat zu werden und die "
             "Nähe zuerst in dir zu finden.",
    "Löwe": "Deine Wunde liegt im Gesehenwerden und im schöpferischen Ausdruck. Deine Heilung "
            "beginnt, wenn du dich zeigst, weil es dich von innen freut, ganz frei vom Applaus "
            "der anderen.",
    "Jungfrau": "Deine Wunde flüstert dir zu, du seist nicht gut genug. Deine Heilung liegt darin, "
                "das Unfertige liebevoll anzunehmen und zu erkennen, dass du schon in diesem "
                "Moment genügst.",
    "Waage": "Deine Wunde zeigt sich in Beziehungen und im Ringen um Gerechtigkeit. Deine Heilung "
             "geschieht, wenn du in der Verbindung mit anderen bei dir selbst bleibst.",
    "Skorpion": "Deine Wunde berührt Ohnmacht und die ganz großen Tiefen. Deine Heilung liegt im "
                "Vertrauen in den Wandel, denn was zerbricht, macht Raum für etwas Echteres.",
    "Schütze": "Deine Wunde sitzt im Glauben und in der Frage nach dem Sinn. Deine Heilung "
               "beginnt, wenn du deiner eigenen Wahrheit folgst statt geliehener Überzeugungen.",
    "Steinbock": "Deine Wunde dreht sich um Leistung und Anerkennung. Deine Heilung liegt darin, "
                 "deinen Wert weit jenseits von Erfolg und Applaus zu fühlen.",
    "Wassermann": "Deine Wunde ist das alte Gefühl, anders und außen vor zu sein. Deine Heilung "
                  "geschieht, wenn du dein Anderssein als Geschenk feierst, denn genau dorthin "
                  "gehörst du.",
    "Fische": "Deine Wunde berührt deine Grenzen und eine große, manchmal namenlose Sehnsucht. "
              "Deine Heilung beginnt, wenn du dein Mitgefühl zuerst dir selbst schenkst und deine "
              "Weichheit als Stärke begreifst.",
}

SIGN_ELEMENT = {
    "Widder": "Feuer", "Stier": "Erde", "Zwillinge": "Luft", "Krebs": "Wasser",
    "Löwe": "Feuer", "Jungfrau": "Erde", "Waage": "Luft", "Skorpion": "Wasser",
    "Schütze": "Feuer", "Steinbock": "Erde", "Wassermann": "Luft", "Fische": "Wasser",
}

# Emotionale Zeichen-Essenz (2 Sätze), fließt hinter dem Planeten-Satz weiter.
SIGN_EMOTION = {
    "Widder": "Du trägst ein Feuer in dir, das losgehen will, sobald es etwas spürt. Warten fällt "
              "dir schwer, und genau diese mutige Direktheit bringt Bewegung in dein Leben und in "
              "das der Menschen um dich herum.",
    "Stier": "Du sehnst dich nach Ruhe, Sicherheit und Dingen, die bleiben. Du genießt mit allen "
             "Sinnen und schenkst anderen ein Gefühl von Verlässlichkeit, auf das man sich wirklich "
             "stützen kann.",
    "Zwillinge": "Dein Geist ist immer in Bewegung, neugierig auf alles, was es zu entdecken und zu "
                 "bereden gibt. Du kommst über Worte in Verbindung und bringst Leichtigkeit "
                 "dorthin, wo es sonst schwer würde.",
    "Krebs": "Du fühlst tiefer, als du es oft nach außen zeigst, und Nähe ist für dich wie ein "
             "Zuhause. Du spürst feinfühlig, was andere brauchen, und schaffst Räume, in denen "
             "Menschen sich geborgen fühlen.",
    "Löwe": "In dir wohnt eine Wärme, die gesehen werden möchte und andere zum Leuchten bringt. "
            "Wenn du aus dem Herzen heraus lebst, ziehst du Menschen an und schenkst ihnen Mut.",
    "Jungfrau": "Du hast ein feines Gespür für das, was noch besser werden kann, und einen echten "
                "Wunsch zu helfen. Deine Liebe zeigt sich im Detail, in der Sorgfalt und in der "
                "stillen Art, für andere da zu sein.",
    "Waage": "Du sehnst dich nach Harmonie, Schönheit und einem Miteinander auf Augenhöhe. Du "
             "spürst Ungleichgewicht sofort und hast die Gabe, zwischen Menschen wieder Frieden "
             "herzustellen.",
    "Skorpion": "Du gehst dorthin in die Tiefe, wo es echt wird und andere lieber wegschauen. "
                "Deine Intensität kann verwandeln, und du hast die Kraft, aus Krisen gestärkt "
                "hervorzugehen.",
    "Schütze": "In dir lebt eine Weite, die nach Sinn, Freiheit und dem großen Ganzen sucht. Du "
               "brauchst Horizont, um zu atmen, und steckst andere mit deinem Vertrauen ins Leben "
               "an.",
    "Steinbock": "Du trägst eine stille Kraft und Ausdauer in dir, die über Jahre etwas Bleibendes "
                 "aufbaut. Verantwortung schreckt dich nicht, und auf dein Wort kann man sich "
                 "verlassen.",
    "Wassermann": "Du bist auf eine schöne Weise anders und siehst die Welt von einem Punkt aus, "
                  "den sonst kaum jemand einnimmt. Deine Freiheit ist dir heilig, und dein eigener "
                  "Weg macht auch anderen Mut, sie selbst zu sein.",
    "Fische": "Du spürst mehr, als sich in Worte fassen lässt, und trägst ein großes Mitgefühl in "
              "dir. Deine Weichheit ist eine Stärke, und deine Fantasie öffnet Türen zu einer Welt "
              "hinter der sichtbaren.",
}

PLANET_MEANING = {
    "Sonne": "Wesenskern und Lebensenergie", "Mond": "Gefühlswelt und innerer Hafen",
    "Merkur": "Denken und Sprache", "Venus": "Liebe und Werte",
    "Mars": "Antrieb und Durchsetzung", "Jupiter": "Wachstum und Vertrauen",
    "Saturn": "Reife und Struktur", "Uranus": "Freiheit und Erneuerung",
    "Neptun": "Sehnsucht und Spiritualität", "Pluto": "Wandlung und Tiefe",
    "Chiron": "Wunde und Heilkraft", "AC": "Deine Wirkung nach außen",
    "DC": "Was du im Partner suchst", "MC": "Berufung und Rolle in der Welt",
    "IC": "Wurzeln und innerstes Zuhause",
}
PLANET_INTRO = {
    "Sonne": "Deine Sonne ist dein innerster Kern, das Licht, mit dem du durch die Welt gehst, und "
             "die Kraft, die dich morgens trägt.",
    "Mond": "Dein Mond ist dein Gefühl, dein inneres Kind und der Ort, an den du dich zurückziehst, "
            "wenn du dich sicher fühlen willst.",
    "Merkur": "Merkur ist deine Art zu denken, zu reden und die Welt in Worte zu fassen.",
    "Venus": "Venus ist deine Art zu lieben, zu genießen und zu spüren, was dir wirklich kostbar "
             "ist.",
    "Mars": "Mars ist dein Feuer, dein Antrieb und die Art, wie du für dich einstehst und Dinge ins "
            "Rollen bringst.",
    "Jupiter": "Jupiter ist der Ort in dir, an dem du wächst, vertraust und das Leben größer "
               "denkst.",
    "Saturn": "Saturn ist dein innerer Lehrmeister, der zeigt, wo du reifst, Verantwortung "
              "übernimmst und etwas Tragfähiges baust.",
    "Uranus": "Uranus ist der Teil von dir, der frei sein will, der aufbricht und Dinge neu denkt.",
    "Neptun": "Neptun ist deine Sehnsucht, deine Fantasie und deine Verbindung zu etwas Größerem.",
    "Pluto": "Pluto ist deine Tiefe, deine Wandlungskraft und die Fähigkeit, dich immer wieder neu "
             "zu erschaffen.",
    "AC": "Dein Aszendent ist der erste Eindruck, den du hinterlässt, die Tür, durch die andere "
          "dich betreten.",
    "DC": "Dein Deszendent zeigt, was du dir in einem anderen Menschen ersehnst und was dich in "
          "Beziehungen anzieht.",
    "MC": "Dein MC ist dein höchster Punkt am Himmel, deine Berufung und die Spur, die du in der "
          "Welt hinterlassen möchtest.",
    "IC": "Dein IC ist deine Wurzel, dein innerstes Zuhause und der Boden, aus dem du gewachsen "
          "bist.",
}
HOUSE_MEANING = {
    1: "dein Ich, dein Auftreten und deinen ersten Eindruck",
    2: "deinen Selbstwert, deinen Besitz und dein Gefühl von Sicherheit",
    3: "dein Denken, dein Reden und deinen Alltag",
    4: "dein Zuhause, deine Familie und deine Wurzeln",
    5: "deine Kreativität, deine Liebe und deine Lebensfreude",
    6: "deinen Alltag, deine Arbeit und deine Gesundheit",
    7: "deine Partnerschaft und deine engen Beziehungen",
    8: "deine Tiefe, deine Wandlung und tiefe Verbundenheit",
    9: "deinen Sinn, die Ferne und dein Weltbild",
    10: "deine Berufung, deine Ziele und deine Rolle in der Welt",
    11: "deine Freundschaften, deine Visionen und deine Zukunft",
    12: "deinen Rückzug, deine Träume und das Verborgene in dir",
}
ANGLE_HOUSE = {"AC": 1, "DC": 7, "MC": 10, "IC": 4}
_ANGLES = ("AC", "DC", "MC", "IC")


def _pos_desc(key, sign, house):
    if key == "Chiron":
        base = CHIRON_SIGN.get(sign, "Chiron zeigt, wo du verletzlich bist, und genau dort liegt "
                               "deine besondere Kraft, andere zu heilen.")
    else:
        base = PLANET_INTRO.get(key, "") + " " + SIGN_EMOTION.get(sign, "")
    if house and key not in _ANGLES:
        base += (f" In deinem Leben spielt sich das vor allem im {house}. Haus ab, deinem "
                 f"Lebensfeld für {HOUSE_MEANING.get(house, 'diesen Bereich')}.")
    return base.strip()


def profile_name(profile):
    return PROFILE_NAMES.get(profile, " / ".join(
        PROFILE_LINES.get(int(x), "") for x in profile.split("/")))


def teaser(chart):
    """Der kostenlose Funke: ausführlich genug zum Neugierigmachen, ohne das volle Bild."""
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
        "locked_preview": [
            "Dein vollständiges Geburtshoroskop mit allen Planeten auf die Bogenminute",
            "Dein Aszendent und dein MC, also wie du wirkst und wohin dein Weg zeigt",
            "Dein Chiron, deine tiefe Wunde und der Ort deiner größten Heilkraft",
            "Deine definierten und offenen Zentren, wo du Kraft schöpfst und wo du dich verlierst",
            "Deine persönliche Deutung in Klartext, dein roter Faden fürs Leben",
        ],
    }


def full_analysis(chart):
    """Die vollständige, liebevoll aufbereitete Analyse (nach der E-Mail)."""
    hd = chart["hd"]
    t = TYPE_INFO.get(hd["type"], {})
    name = chart.get("name") or "du"
    asc = chart.get("ascendant")

    sections = []
    sections.append({
        "title": "Dein Human-Design-Typ",
        "headline": hd["type"],
        "body": t.get("short", ""),
        "facts": [
            ("Strategie", t.get("strategy", "")),
            ("Innere Autorität", hd["authority"]),
            ("Signatur im Flow", t.get("signature", "")),
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
        "body": ("Dein Profil beschreibt die Rolle, in der sich dein Weg entfaltet. Die erste Zahl "
                 "lebst du bewusst, die zweite wirkt eher aus dem Verborgenen und wird oft von "
                 "anderen zuerst in dir gesehen. " + PROFILE_DESC.get(hd["profile"], "")),
        "facts": [("Definition", hd["definition"]),
                  ("Definierte Zentren", ", ".join(hd["defined_centers"]) or "keine")],
    })

    defined = hd.get("defined_centers", [])
    open_c = hd.get("open_centers", [])
    sections.append({
        "title": "Deine Zentren",
        "headline": f"{len(defined)} definiert · {len(open_c)} offen",
        "body": ("Deine definierten Zentren sind deine verlässliche, gleichbleibende Energie. Hier "
                 "bist du dir treu und kannst dich auf dich verlassen. Deine offenen Zentren sind "
                 "deine Weisheits- und Lernräume. Hier nimmst du andere fein auf und bleibst "
                 "beweglich, und genau hier entsteht Druck, wenn du dich verbiegst, um "
                 "dazuzugehören. Wenn du das erkennst, verlierst du dich seltener in fremden "
                 "Erwartungen."),
        "facts": [("Definiert", ", ".join(defined) or "keine"),
                  ("Offen", ", ".join(open_c) or "keine")],
    })

    chi = chart["natal"].get("Chiron")
    if chi:
        facts = [("Stellung", f"{chi['sym']} {chi['sign']} {chi['text']}")]
        if chi.get("house"):
            facts.append(("Haus", f"H{chi['house']}"))
        sections.append({
            "title": "Dein Chiron, Wunde und Heilung",
            "headline": f"Chiron in {chi['sign']} {chi['text']}",
            "body": CHIRON_SIGN.get(chi["sign"], "Chiron zeigt die Stelle, an der du verletzlich "
                    "bist, und genau dort liegt deine besondere Kraft, andere zu heilen."),
            "facts": facts,
        })

    # Reihenfolge Natal: Sonne, Mond, dann die Achsen (AC/DC/MC/IC), dann die Planeten.
    natal_rows = []
    mc = dc = ic = None
    if asc:
        mc = chart["mc"]
        dc = chart.get("descendant")
        ic = chart.get("ic")

    def _row(sym, body, p, house):
        return {"sym": sym, "body": body, "pos": f"{p['sym']} {p['sign']} {p['text']}",
                "house": house}

    nat = chart["natal"]
    if nat.get("Sonne"):
        natal_rows.append(_row(nat["Sonne"].get("sym_body", "☉"), "Sonne", nat["Sonne"], nat["Sonne"].get("house")))
    if nat.get("Mond"):
        natal_rows.append(_row(nat["Mond"].get("sym_body", "☽"), "Mond", nat["Mond"], nat["Mond"].get("house")))
    if asc:
        natal_rows.append(_row("AC", "Aszendent", asc, 1))
        natal_rows.append(_row("DC", "Deszendent", dc, 7))
        natal_rows.append(_row("MC", "Medium Coeli", mc, 10))
        natal_rows.append(_row("IC", "Imum Coeli", ic, 4))
    for b in ["Merkur", "Venus", "Mars", "Jupiter", "Saturn", "Uranus",
              "Neptun", "Pluto", "Chiron", "Nordknoten", "Südknoten"]:
        p = nat.get(b)
        if p:
            natal_rows.append(_row(p.get("sym_body", ""), b, p, p.get("house")))

    closing = (f"{name}, wenn du nur eine Sache aus all dem mitnimmst, dann diese: Du darfst deiner "
               f"eigenen Art vertrauen. Lebe deine Strategie, {t.get('strategy','').lower()}, und "
               f"hör auf deine {hd['authority'].lower()}. Immer wenn sich etwas von innen stimmig "
               f"anfühlt, bist du auf deinem Weg, auch wenn er kurviger verläuft als der von "
               f"anderen. 🤍")

    # Geometrie für das Horoskop-Rad (exakte ekliptikale Längen)
    geo = None
    if asc:
        planets = []
        for wb in ["Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn",
                   "Uranus", "Neptun", "Pluto", "Chiron", "Nordknoten"]:
            p = nat.get(wb)
            if p and "lon" in p:
                planets.append({"name": wb, "sym": p.get("sym_body", ""),
                                "lon": p["lon"], "house": p.get("house")})
        geo = {"asc": asc["lon"], "dc": dc["lon"], "mc": mc["lon"], "ic": ic["lon"],
               "planets": planets}

    # Aufklappbare Positionskarten (Natal). Reihenfolge: Sonne, Mond, AC, DC, MC, IC, dann Planeten.
    positions = []

    def _pos(key, label, p, house):
        return {
            "key": key, "label": label, "sym": p.get("sym_body", key) if key not in _ANGLES else key,
            "signSymbol": p["sym"], "sign": p["sign"], "deg": p["text"],
            "element": SIGN_ELEMENT.get(p["sign"], ""), "house": house,
            "house_meaning": HOUSE_MEANING.get(house, "") if house else "",
            "meaning": PLANET_MEANING.get(key, ""), "desc": _pos_desc(key, p["sign"], house),
        }

    if nat.get("Sonne"):
        positions.append(_pos("Sonne", "Sonne", nat["Sonne"], nat["Sonne"].get("house")))
    if nat.get("Mond"):
        positions.append(_pos("Mond", "Mond", nat["Mond"], nat["Mond"].get("house")))
    if asc:
        positions.append(_pos("AC", "Aszendent", asc, 1))
        positions.append(_pos("DC", "Deszendent", dc, 7))
        positions.append(_pos("MC", "Medium Coeli", mc, 10))
        positions.append(_pos("IC", "Imum Coeli", ic, 4))
    for k in ["Merkur", "Venus", "Mars", "Jupiter", "Saturn", "Uranus",
              "Neptun", "Pluto", "Chiron"]:
        p = nat.get(k)
        if p:
            positions.append(_pos(k, k, p, p.get("house")))

    _defset = set(hd["defined_centers"])
    hd_centers = [{"name": c, "defined": c in _defset, "meaning": CENTER_MEANING.get(c, "")}
                  for c in ["Kopf", "Ajna", "Kehle", "G", "Herz", "Milz", "Sakral",
                            "Solarplexus", "Wurzel"]]

    return {
        "name": name,
        "hd": hd,
        "sections": sections,
        "natal_rows": natal_rows,
        "positions": positions,
        "hd_centers": hd_centers,
        "ascendant": asc,
        "geo": geo,
        "closing": closing,
        "note": "Symbolische Deutung zur Selbstreflexion. Kein Ersatz für Beratung, keine Diagnose. "
                "Alle Positionen exakt berechnet (tropischer Tierkreis, Ganzzeichen-Häuser).",
    }
