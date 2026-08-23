"""
Textbausteine für Intuition mit Herz.
Der Gratis-Einblick (teaser) und die Voll-Analyse (full_analysis) werden
deterministisch aus den exakten Chart-Daten gebaut (0 € KI-Kosten).
Ton: warm, klar, gefühlvoll, in Du-Form. Ohne Gedankenstriche, ohne
"nicht ... sondern"-Konstruktionen. Menschen sollen sich wiedererkennen.
Die Zahlen bleiben immer die exakt berechneten aus _engine.py.
"""
import re
from datetime import date

TYPE_INFO = {
    "Generator": {
        "strategy": "Auf das Leben antworten",
        "signature": "Zufriedenheit", "not_self": "Frustration",
        "aura": "offen & umhüllend",
        "short": "Du bist die schöpferische Lebenskraft dieser Welt. In dir steckt eine Energie, die "
                 "anpacken will, sobald sie das Richtige spürt. Vielleicht hast du dich oft "
                 "gezwungen, Dinge zu tun, die dir eigentlich die Kraft rauben, und dich danach leer "
                 "gefühlt. Wenn du nur noch auf das antwortest, was dich wirklich anzieht, wird deine "
                 "Energie fast unerschöpflich. Dann wird Arbeit zu etwas, das dich erfüllt statt "
                 "auslaugt.",
    },
    "Manifestierender Generator": {
        "strategy": "Antworten und dann informieren",
        "signature": "Zufriedenheit & Frieden", "not_self": "Frustration & Wut",
        "aura": "offen & umhüllend",
        "short": "In dir vereinen sich zwei Kräfte: die Ausdauer des Generators und die "
                 "Schnelligkeit des Manifestors. Du gehst gern mehrere Schritte auf einmal, springst, "
                 "probierst, findest Abkürzungen. Vielleicht hat man dir früher gesagt, du seist zu "
                 "sprunghaft oder zu ungeduldig. Aber genau so bist du richtig. Du darfst schnell "
                 "sein, Umwege gehen und Dinge wieder abbrechen, die sich nicht mehr stimmig "
                 "anfühlen.",
    },
    "Manifestor": {
        "strategy": "Informieren, bevor du handelst",
        "signature": "Frieden", "not_self": "Wut",
        "aura": "verschlossen & initiierend",
        "short": "Du bist hier, um Dinge anzustoßen und in Bewegung zu bringen. In dir lebt eine "
                 "Kraft, die nicht auf Erlaubnis wartet. Vielleicht bist du früh angeeckt, weil du "
                 "gemacht hast, was du wolltest, und hast dann gelernt, dich zusammenzunehmen. Du "
                 "brauchst keine Erlaubnis, um loszugehen. Du brauchst nur den Mut, dein Umfeld "
                 "mitzunehmen, bevor du startest. Dann öffnen sich dir die Türen, statt sich dir in "
                 "den Weg zu stellen.",
    },
    "Projektor": {
        "strategy": "Auf die Einladung warten",
        "signature": "Erfolg", "not_self": "Bitterkeit",
        "aura": "fokussiert & durchdringend",
        "short": "Du siehst Menschen und Zusammenhänge klarer als die meisten. Oft weißt du, was "
                 "jemand braucht, bevor er es selbst versteht. Vielleicht hast du dich trotzdem oft "
                 "übersehen oder erschöpft gefühlt, weil du versucht hast, mitzuhalten wie alle "
                 "anderen. Deine Gabe ist nicht das Dauerschuften. Sie entfaltet sich, sobald sie "
                 "erkannt und eingeladen wird. Dann führst du mit einer Weisheit, die kaum jemand "
                 "aufbringt.",
    },
    "Reflektor": {
        "strategy": "Einen Mondzyklus abwarten",
        "signature": "Überraschung", "not_self": "Enttäuschung",
        "aura": "widerspiegelnd & abtastend",
        "short": "Du bist ein seltener Spiegel deiner Umgebung. Du fühlst, wie es einem Ort und den "
                 "Menschen darin wirklich geht, oft stärker, als dir lieb ist. Vielleicht hast du "
                 "dich manchmal wie ein Chamäleon gefühlt, mal so, mal so, je nachdem, wo du bist. "
                 "Das ist keine Unbeständigkeit. Das ist deine kostbare, fast magische Gabe, die es "
                 "nur bei ganz wenigen Menschen gibt. Du brauchst nur die richtigen Orte und "
                 "Menschen um dich, dann blühst du auf.",
    },
}

AUTHORITY_INFO = {
    "Emotionale Autorität": "Deine Klarheit reift über die Zeit. Vielleicht kennst du das: Heute "
        "bist du Feuer und Flamme, morgen dagegen, und du weißt kaum noch, was jetzt stimmt. Das "
        "ist kein Wankelmut. So funktionierst du. Warte bei allem Wichtigen eine Gefühlswelle ab "
        "und schlaf ein paar Nächte darüber. Deine Wahrheit zeigt sich erst im Verlauf, wenn sich "
        "das Auf und Ab gelegt hat und Ruhe einkehrt.",
    "Sakrale Autorität": "Dein Bauch weiß es sofort. Ein echtes Ja fühlt sich weit und lebendig an, "
        "ein Nein zieht sich leise zusammen. Vielleicht hast du dir dieses klare Körpergefühl oft "
        "ausgeredet, weil dein Kopf vernünftiger klang. Aber dein Bauch lügt dich nie an. Lerne "
        "wieder, diesem Körperlaut zu trauen, noch bevor der Kopf anfängt zu rechnen.",
    "Milz-Autorität (Splenisch)": "Deine Wahrheit spricht leise und meist nur ein einziges Mal, als "
        "feine Ahnung im Augenblick. Kennst du dieses erste, stille Bauchgefühl, das du oft "
        "weggedacht hast, um es später zu bereuen? Genau das ist deine Führung. Lerne, diesem "
        "ersten Impuls zu trauen. Er schützt dich und führt dich sicherer, als jede lange Grübelei "
        "es je könnte.",
    "Ego-/Herz-Autorität": "Deine Wahrheit liegt in deinem echten Wollen. Vielleicht hast du oft "
        "getan, was von dir erwartet wurde, und dich dabei selbst verloren. Frage dich bei jeder "
        "Entscheidung ehrlich: Was will mein Herz wirklich, und wofür brennt meine Kraft? Nur was "
        "du aus vollem Herzen willst, wirst du auch durchhalten. Alles andere kostet dich mehr, als "
        "es dir gibt.",
    "Selbst-projizierte Autorität": "Deine Wahrheit hörst du, wenn du sie aussprichst. Vielleicht "
        "denkst du Entscheidungen endlos im Kopf durch und kommst doch nicht weiter. Rede mit einem "
        "vertrauten Menschen und lausche dabei vor allem deiner eigenen Stimme. Achte weniger auf "
        "den Rat, den du bekommst, und mehr auf das, was aus dir selbst herauskommt. Darin liegt "
        "schon die Antwort.",
    "Mond-Autorität (Reflektor)": "Lass große Entscheidungen einen ganzen Mondzyklus reifen, "
        "ungefähr einen Monat. Vielleicht hast du dich oft unter Druck setzen lassen, schnell zu "
        "entscheiden, und es später bereut. Du brauchst diese Zeit wirklich. Sprich mit vielen "
        "Menschen und schlaf viele Nächte darüber. Die Klarheit stellt sich von ganz allein ein, "
        "wenn du ihr den Raum gibst.",
    "Mentale Autorität (Umgebung)": "Dein Umfeld ist dein Resonanzraum. Du hast keine feste innere "
        "Stimme im Körper, die sofort Ja oder Nein sagt, und das hat dich vielleicht oft "
        "verunsichert. Das ist völlig in Ordnung. Sprich alles laut aus und spüre genau, an welchem "
        "Ort und mit welchen Menschen dein Weg sich stimmig anfühlt. Die richtige Umgebung zeigt "
        "dir deine Richtung.",
}

# Autorität in einer Form, die sich sauber mitten in einen Satz einfügt.
# (Reines .lower() würde das Substantiv "Autorität" fälschlich kleinschreiben.)
AUTHORITY_PHRASE = {
    "Emotionale Autorität": "emotionale Autorität",
    "Sakrale Autorität": "sakrale Autorität",
    "Milz-Autorität (Splenisch)": "Milz-Autorität",
    "Ego-/Herz-Autorität": "Herz-Autorität",
    "Selbst-projizierte Autorität": "selbst-projizierte Autorität",
    "Mond-Autorität (Reflektor)": "Mond-Autorität",
    "Mentale Autorität (Umgebung)": "mentale Autorität",
}

def auth_phrase(auth):
    """Autorität, klein eingebettet in einen Fließsatz, aber grammatisch korrekt."""
    return AUTHORITY_PHRASE.get(auth, auth)


# Strategie, Signatur und Nicht-Selbst-Thema mitten im Satz. Ein blindes .lower()
# würde hier die Substantive kleinschreiben ("auf das leben antworten").
STRATEGY_PHRASE = {
    "Auf das Leben antworten": "auf das Leben antworten",
    "Antworten und dann informieren": "antworten und dann informieren",
    "Informieren, bevor du handelst": "informieren, bevor du handelst",
    "Auf die Einladung warten": "auf die Einladung warten",
    "Einen Mondzyklus abwarten": "einen Mondzyklus abwarten",
}


def strat_phrase(strat):
    """Strategie, klein eingebettet in einen Fließsatz, Substantive bleiben groß."""
    return STRATEGY_PHRASE.get(strat, strat)


# Kurzform der zwölf Häuser für den Fließtext. Die ausführliche HOUSE_MEANING-Fassung
# zählt drei Begriffe auf und wiederholte damit fast immer ein Wort aus dem Satz daneben
# ("dem Lebensfeld für deinen Alltag … deine Stimmung hängt stark an deinem Alltag").
HOUSE_SHORT = {
    1: "dein Selbst", 2: "Werte und Sicherheit", 3: "Denken und Austausch",
    4: "Wurzeln und Zuhause", 5: "Ausdruck und Freude", 6: "Alltag und Gesundheit",
    7: "deine Beziehungen", 8: "Tiefe und Wandlung", 9: "Sinn und Weite",
    10: "deine Berufung", 11: "Gemeinschaft und Zukunft", 12: "Rückzug und Verborgenes",
}


def aufzaehlung(items):
    """Aufzählung mit "und" statt einer langen Kommakette am Ende."""
    items = [str(x) for x in items if x]
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " und " + items[-1]


def amp_phrase(text):
    """Kaufmanns-Und gehört in eine Tabelle, nicht in einen Fließtext."""
    return str(text or "").replace(" & ", " und ")


def meaning_phrase(planet):
    """Planeten-Thema mitten im Satz. Substantive bleiben groß, nur der Artikel nicht."""
    return PLANET_MEANING.get(planet, "")

PROFILE_LINES = {
    1: "Fundament", 2: "Rückzug", 3: "Erfahrung",
    4: "Netzwerk", 5: "Lösung", 6: "Vorbild",
}
PROFILE_NAMES = {
    "1/3": "Fundament / Erfahrung", "1/4": "Fundament / Netzwerk",
    "2/4": "Rückzug / Netzwerk", "2/5": "Rückzug / Lösung",
    "3/5": "Erfahrung / Lösung", "3/6": "Erfahrung / Vorbild",
    "4/6": "Netzwerk / Vorbild", "4/1": "Netzwerk / Fundament",
    "5/1": "Lösung / Fundament", "5/2": "Lösung / Rückzug",
    "6/2": "Vorbild / Rückzug", "6/3": "Vorbild / Erfahrung",
}
PROFILE_DESC = {
    "1/3": "Du brauchst festen Boden unter den Füßen und ein sicheres Fundament aus Wissen. "
           "Zugleich lernst du durch eigenes Ausprobieren, durch Versuch und Irrtum, was im Leben "
           "wirklich trägt.",
    "1/4": "Du gräbst gern in die Tiefe, bis du eine Sache wirklich verstanden hast, und teilst "
           "dein Wissen dann mit den Menschen, die dir nahe sind. Über sie öffnen sich dir Wege.",
    "2/4": "Du trägst ein natürliches Talent in dir, das oft im Verborgenen ruht, bis andere es "
           "in dir sehen und dich rufen. Dein Netzwerk trägt dich, wenn du dich rufen lässt.",
    "2/5": "Du bist das stille Talent, das sich gern zurückzieht und doch immer wieder nach vorn "
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
           "ist. Dein solides, tiefes Wissen macht dich zu dem Menschen, der in der Not wirklich hilft.",
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

# "Was du damit machst" für ein DEFINIERTES Zentrum, je Zentrum konkret.
# (Für offene Zentren dient das jeweilige "tip"-Feld aus CENTER_INFO als Handlung.)
CENTER_USE_DEF = {
    "Kopf": "Vertraue deinen eigenen Fragen und Ideen und teile sie ruhig. Du musst sie nicht "
            "rechtfertigen, sie stecken andere ganz von selbst an. Lass dir von außen keine fremden "
            "Denkaufgaben aufdrücken, du hast genug eigene.",
    "Ajna": "Steh zu deiner Meinung und sprich sie klar aus, sie gibt anderen Halt. Bleibe dabei "
            "bewusst neugierig auf andere Blickwinkel, damit aus deiner Festigkeit nie Sturheit wird.",
    "Kehle": "Sprich, wenn du wirklich etwas zu sagen hast, und rede nicht lange drumherum. Deine "
             "Worte tragen. Nutze diese Stimme bewusst, statt sie mit ständigem Reden zu verbrauchen.",
    "G": "Folge deinem inneren Kompass, auch wenn andere zweifeln. Triff deine "
         "Richtungsentscheidungen aus diesem Gefühl heraus, nicht nach der Meinung anderer.",
    "Herz": "Setze deine Willenskraft gezielt für das ein, was dir wirklich wichtig ist, und halte "
            "deine Versprechen. Pass nur auf, dich nicht ständig zu überfordern, nur weil du so viel "
            "durchziehen kannst. Gönn dir auch Ruhe.",
    "Milz": "Höre auf dein erstes, leises Bauchgefühl, es ist meist richtig. Handle im Moment danach, "
            "statt es lange zu zerdenken. Dieser Instinkt schützt dich, wenn du ihm vertraust.",
    "Sakral": "Setze deine Energie für das ein, was dich wirklich anzieht, und höre bei einem klaren "
              "Nein aus dem Bauch auf. So bleibt deine Kraft erhalten. Zwing dich zu nichts, das dich "
              "innerlich leer macht.",
    "Solarplexus": "Gib deinen Gefühlen Zeit und triff Wichtiges nie mitten in der Welle. Schlaf über "
                   "Entscheidungen und warte, bis Ruhe einkehrt. Dann ist deine Klarheit da.",
    "Wurzel": "Nutze deinen inneren Antrieb, um Dinge Schritt für Schritt anzugehen, ohne dich hetzen "
              "zu lassen. Du kannst Druck in ruhige Bewegung verwandeln, das ist deine stille Stärke.",
}

# Was definiert und offen wirklich bedeuten, je Zentrum.
CENTER_DEEP = {
    "Kopf": {
        "def": "Dein Kopf ist definiert. Du hast eine feste, eigene Art, dich inspirieren zu lassen und über Dinge nachzudenken. Deine Fragen und Ideen kommen wirklich aus dir. Verlasse dich darauf, statt dir ständig neue Fragen von außen aufdrücken zu lassen.",
        "open": "Dein Kopf ist offen. Du zerdenkst oft Fragen und Probleme, die gar nicht deine sind. Der Druck, alles verstehen und beantworten zu müssen, kommt von außen. Was du tun kannst: Nicht jede Frage, die auftaucht, musst du lösen. Lass die meisten einfach ziehen.",
    },
    "Ajna": {
        "def": "Deine Ajna ist definiert. Du hast eine feste, verlässliche Art zu denken und dir eine Meinung zu bilden. Deine Sicht auf die Dinge ist stabil. Das gibt dir Sicherheit, kann aber auch stur machen. Bleibe bewusst offen für neue Blickwinkel.",
        "open": "Deine Ajna ist offen. Deine Meinungen sind beweglich und passen sich der Lage an. Vielleicht tust du manchmal sicherer, als du bist. Das ist keine Schwäche. Du darfst sagen: Ich bin mir noch nicht sicher. Genau diese Offenheit macht dich mit der Zeit weise.",
    },
    "Kehle": {
        "def": "Deine Kehle ist definiert. Du hast eine feste, verlässliche Art, dich auszudrücken und Dinge in die Welt zu bringen. Wenn du sprichst, hat es Gewicht. Vertraue darauf und rede nicht lange drumherum.",
        "open": "Deine Kehle ist offen. Wie und wann du dich ausdrückst, hängt stark von der Umgebung ab. Vielleicht spürst du manchmal Druck, unbedingt etwas sagen zu müssen, um dazuzugehören. Warte, bis du wirklich angesprochen oder eingeladen wirst. Dann werden deine Worte gehört.",
    },
    "G": {
        "def": "Dein G-Zentrum ist definiert. Du trägst einen festen inneren Kompass für deine Identität und deine Richtung im Leben. Im Kern weißt du, wer du bist, auch wenn der Weg mal unklar ist. Vertraue dieser inneren Konstante.",
        "open": "Dein G-Zentrum ist offen. Wer du bist und wohin du willst, fühlt sich je nach Umgebung anders an. Das kann verunsichern. Der Schlüssel ist der richtige Ort: An den falschen Orten verlierst du dich, an den richtigen findest du dich. Achte sehr genau darauf, wo und mit wem du dich aufhältst.",
    },
    "Herz": {
        "def": "Dein Herzzentrum ist definiert. Du hast eine verlässliche Willenskraft. Du kannst dir etwas vornehmen und es durchziehen, und Versprechen kannst du halten. Achte nur darauf, dich nicht ständig zu überfordern.",
        "open": "Dein Herzzentrum ist offen. Du musst dir und anderen nichts beweisen, auch wenn du es oft trotzdem versuchst. Vielleicht kennst du das Gefühl, ständig zeigen zu müssen, dass du genug wert bist. Du bist es längst. Du musst deinen Wert nicht erkämpfen.",
    },
    "Milz": {
        "def": "Deine Milz ist definiert. Du hast einen verlässlichen Instinkt für Sicherheit und Gesundheit, ein festes, leises Bauchgefühl im Hier und Jetzt. Vertraue dieser ruhigen, konstanten Ahnung.",
        "open": "Deine Milz ist offen. Du hältst manchmal an Dingen, Menschen oder Gewohnheiten fest, die dir nicht guttun, aus Angst vor dem Loslassen. Diese Angst kennst du vielleicht gut. Was du tun kannst: Nicht jede Angst ist deine eigene, vieles nimmst du nur auf. Traue dich, loszulassen, was dich klein hält.",
    },
    "Sakral": {
        "def": "Dein Sakral ist definiert. Du hast eine kraftvolle, erneuerbare Lebens- und Arbeitsenergie. Wenn du tust, was dich wirklich anzieht, ist sie fast unerschöpflich. Wichtig ist nur, dass du auf dein klares Ja und Nein aus dem Bauch hörst und dich nicht zu Dingen zwingst.",
        "open": "Dein Sakral ist offen. Du hast keine gleichbleibende Arbeitsenergie, und das ist völlig in Ordnung. Vielleicht hast du dich oft gehetzt und über deine Grenzen hinaus gearbeitet, um mitzuhalten. Das musst du nicht. Lerne, rechtzeitig aufzuhören, statt bis zur Erschöpfung weiterzumachen.",
    },
    "Solarplexus": {
        "def": "Dein Solarplexus ist definiert. Du erlebst Gefühle in Wellen, mal hoch, mal tief, und das ist deine ganz normale Art zu fühlen. Triff wichtige Entscheidungen nie mitten im Hoch oder Tief. Warte, bis die Welle sich gelegt hat.",
        "open": "Dein Solarplexus ist offen. Du nimmst die Stimmungen anderer stark auf und hältst sie schnell für deine eigenen. Vielleicht meidest du Streit, um bloß die Harmonie zu wahren. Was du tun kannst: Frage dich, wessen Gefühl das gerade ist. Und traue dich, auch unangenehme Wahrheiten auszusprechen.",
    },
    "Wurzel": {
        "def": "Deine Wurzel ist definiert. Du hast einen festen, verlässlichen Umgang mit Druck und Antrieb. Stress kannst du in Bewegung umsetzen, ohne dich davon jagen zu lassen.",
        "open": "Deine Wurzel ist offen. Du spürst oft einen Druck, Dinge schnell erledigen zu müssen, nur um den Stress endlich loszuwerden. Dieser Druck ist meist geliehen, er gehört gar nicht dir. Was du tun kannst: Nichts muss sofort. Nimm dir den Druck bewusst raus und mach eins nach dem anderen.",
    },
}

# Tiefe Zentren-Deutung: Thema, was Definiert bedeutet, was Offen bedeutet, was du tun kannst,
# plus eine kurze Gaben- und Schattenformel (für Stärke- und Herausforderungs-Analyse).
CENTER_INFO = {
    "Kopf": {
        "theme": "Inspiration und mentaler Druck",
        "defined": "Du hast eine eigene, verlässliche Quelle für Inspiration. Fragen und Ideen kommen "
                   "bei dir von innen, in einem festen Rhythmus, und du inspirierst andere oft, ohne "
                   "es selbst zu merken.",
        "open": "Dein Kopf nimmt den Denkdruck der ganzen Welt auf. Du zerdenkst oft Fragen, die gar "
                "nicht deine sind, und fühlst dich mental unter Druck gesetzt.",
        "tip": "Frage dich immer wieder: Ist das gerade wirklich meine Frage, oder denke ich für "
               "jemand anderen mit? Lass die los, die nicht zu dir gehört.",
        "gift": "eine eigene, verlässliche Inspiration",
        "shadow": "das Zerdenken von Fragen, die gar nicht deine sind",
        "says_def": "Dass in dir eine eigene Quelle für Inspiration sprudelt. Deine Gedanken und "
                    "Ideen kommen aus dir selbst, in ihrem ganz eigenen Takt, und du musst nicht "
                    "warten, bis dich jemand von außen anstößt. Menschen in deiner Nähe fangen oft an, "
                    "größer und freier zu denken, ganz ohne dass du es merkst. Du bist ein stiller "
                    "Funke für andere.",
        "says_open": "Dass du ein neugieriger, offener Geist bist, der die Fragen der ganzen Welt "
                     "in sich aufnimmt. Das ist eine Gabe, kein Defekt. Nur liegst du deshalb "
                     "manchmal nachts wach über Problemen, die sich am Morgen längst von selbst "
                     "gelöst haben. Sobald du das eine vom anderen trennen kannst, wird aus dem "
                     "ewigen Grübeln eine echte, ruhige Weisheit.",
    },
    "Ajna": {
        "theme": "Denken und Verstehen",
        "defined": "Du hast eine feste Art zu denken und stabile Überzeugungen. Deine Meinung steht, "
                   "und genau das gibt anderen Halt.",
        "open": "Du denkst flexibel und kannst dich in viele Sichtweisen hineinversetzen. Innerlich "
                "fühlst du dich dabei oft unsicher und tust manchmal so, als wüsstest du es genau.",
        "tip": "Du darfst offen sagen, dass du es noch nicht sicher weißt. Deine geistige Offenheit "
               "ist Weisheit, kein Makel.",
        "gift": "klare, verlässliche Überzeugungen",
        "shadow": "die Unsicherheit hinter vorgespielter Sicherheit",
        "says_def": "Dass du innerlich einen festen Standpunkt hast, an dem sich andere festhalten "
                    "können. In einer Welt voller schwankender Meinungen bist du der ruhige Pol, der "
                    "weiß, was er denkt. Das gibt den Menschen um dich herum Halt und Sicherheit. Deine "
                    "einzige Achtsamkeit: Lass deine Festigkeit nicht zur Sturheit werden, bleibe "
                    "bewusst offen für einen neuen Blickwinkel.",
        "says_open": "Dass du kein sturer Kopf bist, sondern ein wunderbar beweglicher. Du kannst dich "
                     "in die verschiedensten Sichtweisen hineindenken, das macht dich klug, offen und "
                     "verständnisvoll. Der Preis dafür: Du fühlst dich innerlich oft unsicher und "
                     "spielst dann nach außen Gewissheit vor, um nicht angreifbar zu sein. Du darfst "
                     "ehrlich sagen: Ich weiß es noch nicht. Genau in dieser Offenheit reift deine "
                     "Weisheit.",
    },
    "Kehle": {
        "theme": "Ausdruck und Manifestation",
        "defined": "Du hast eine konsistente Stimme und eine klare Art, dich auszudrücken und Dinge "
                   "in die Welt zu bringen.",
        "open": "Du redest manchmal, um Aufmerksamkeit zu bekommen oder um die Stille zu füllen, und "
                "fühlst dich danach oft unwohl.",
        "tip": "Warte, bis du wirklich gefragt wirst oder etwas von selbst raus will. Dann hat dein "
               "Wort echtes Gewicht.",
        "gift": "eine klare, tragende Stimme",
        "shadow": "das Reden aus Druck oder für Anerkennung",
        "says_def": "Dass deine Stimme Gewicht hat. Wenn du etwas sagst, dann sitzt es, weil "
                    "hinter deinen Worten etwas Festes steht. Menschen hören dir zu, weil sie "
                    "spüren, dass du meinst, was du sagst. Das ist seltener, als du denkst, und es "
                    "öffnet dir Türen, ohne dass du dafür laut werden musst.",
        "says_open": "Dass du ein feines Gespür dafür hast, was in einem Raum gerade gesagt werden "
                     "will. Deine Worte sind nicht immer gleich, sie passen sich an, und das ist "
                     "eine Kunst, keine Schwäche. Deine stärksten Sätze kommen, wenn man dich "
                     "wirklich fragt. Dann hat dein Wort auf einmal ein Gewicht, das du dir vorher "
                     "nie zugetraut hättest.",
    },
    "G": {
        "theme": "Identität, Liebe und Richtung",
        "defined": "Du hast ein stabiles Gefühl dafür, wer du bist und wohin du willst. Deine "
                   "Richtung kommt von innen.",
        "open": "Du suchst deine Identität und deine Richtung oft im Außen, in Menschen und an Orten. "
                "Mal fühlst du dich so, mal ganz anders.",
        "tip": "Der richtige Ort ist für dich entscheidend. Du musst nicht wissen, wer du bist, wähle "
               "einfach die Umgebung, in der du dich am meisten nach dir selbst anfühlst.",
        "gift": "ein festes Gefühl für dich und deine Richtung",
        "shadow": "die Suche nach dir selbst im Außen",
        "says_def": "Dass du einen inneren Kompass trägst, der auch dann nicht verlorengeht, wenn "
                    "der Weg gerade unklar ist. Diese innere Konstante ist ein großes Geschenk, "
                    "nach dem viele Menschen ihr Leben lang suchen. Du trägst sie längst in dir. "
                    "Vertraue ihr, gerade wenn draußen alles wackelt.",
        "says_open": "Dass du ein wandlungsfähiger Mensch bist, der sich über Orte und Beziehungen "
                     "immer wieder neu erlebt, mal so, mal ganz anders. Das ist keine "
                     "Identitätsschwäche, das ist eine seltene Beweglichkeit. Deine große Lebenslektion: "
                     "Der richtige Ort verändert alles für dich. An den falschen Plätzen und neben den "
                     "falschen Menschen verlierst du dich, an den richtigen findest du nach Hause. "
                     "Wähle deine Umgebung mit größter Sorgfalt, sie formt dich mehr als bei jedem "
                     "anderen.",
    },
    "Herz": {
        "theme": "Willenskraft und Selbstwert",
        "defined": "Du hast eine verlässliche Willenskraft und ein natürliches Gespür für deinen "
                   "Wert. Wenn du etwas versprichst, hältst du es auch.",
        "open": "Du versuchst dich manchmal zu beweisen und versprichst mehr, als dir guttut, um "
                "deinen Wert zu zeigen.",
        "tip": "Du musst dir und niemandem etwas beweisen. Dein Wert steht nicht zur Debatte, er ist "
               "einfach da.",
        "gift": "eine echte, verlässliche Willenskraft",
        "shadow": "das ständige Sich-beweisen-Müssen",
        "says_def": "Dass du dir etwas vornehmen und es auch wirklich durchziehen kannst. Dein "
                    "Wille ist verlässlich, dein Wort gilt, und tief in dir weißt du um deinen "
                    "eigenen Wert, ohne ihn jemandem beweisen zu müssen. Das ist eine seltene "
                    "innere Stärke, und sie macht dich zu einem Menschen, auf dessen Zusage sich "
                    "andere wirklich verlassen können.",
        "says_open": "Dass du ein Mensch bist, dessen Wert nicht an Leistung hängt. Du kennst "
                     "dieses Gefühl vermutlich gut: dich zeigen müssen, immer wieder belegen, dass "
                     "du genug bist. Aber höre kurz zu: Du bist längst genug, und zwar ohne eine "
                     "einzige Bedingung. Du darfst aufhören zu kämpfen und dich einfach ausruhen.",
    },
    "Milz": {
        "theme": "Intuition, Gesundheit und Instinkt",
        "defined": "Du hast ein spontanes, verlässliches Körperwissen und einen guten Instinkt für "
                   "das, was dir guttut.",
        "open": "Du hältst manchmal aus Angst an Dingen, Menschen oder Gewohnheiten fest, die dir "
                "längst nicht mehr guttun.",
        "tip": "Frage dich ehrlich: Halte ich hier an etwas fest, das mir eigentlich schadet? Du "
               "darfst loslassen, es nimmt dir nichts weg.",
        "gift": "ein feiner, gesunder Instinkt",
        "shadow": "das Festhalten aus Angst",
        "says_def": "Dass du einen leisen, verlässlichen Wächter in dir trägst, der im Hier und Jetzt "
                    "genau weiß, was dir guttut und was nicht. Ein feines Körperwissen, das dich "
                    "schützt, sobald du ihm zuhörst. Viele Menschen haben diesen ruhigen inneren "
                    "Instinkt nicht und müssen alles mühsam erdenken. Du spürst es einfach. Traue "
                    "dieser stillen, ersten Ahnung.",
        "says_open": "Dass du ein feinfühliger Mensch bist, der die Stimmung, die Gesundheit und "
                     "das Wohl anderer stark mitbekommt. Dass dir das Loslassen schwerfällt, hat "
                     "einen einfachen Grund: Das Vertraute fühlt sich sicherer an als alles "
                     "Unbekannte. Aber vieles von dieser Angst ist gar nicht deine, du hast sie "
                     "nur aufgenommen. Wenn du das erkennst, wirst du erstaunlich frei und mutig.",
    },
    "Sakral": {
        "theme": "Lebenskraft und Arbeitsenergie",
        "defined": "Du hast eine kraftvolle, nachhaltige Energie, sobald du das tust, was dich "
                   "wirklich anspringt. Dann kennst du kaum Müdigkeit.",
        "open": "Du spürst oft nicht, wann genug ist, und arbeitest über deine Grenze hinaus, bis du "
                "ganz leer bist.",
        "tip": "Lerne zu fühlen, wann genug genug ist. Du musst dich nicht leeren, um wertvoll zu "
               "sein.",
        "gift": "eine tiefe, tragende Lebenskraft",
        "shadow": "das Nicht-Spüren, wann genug ist",
        "says_def": "Dass in dir ein kraftvoller, erneuerbarer Motor steckt. Diese Ausdauer ist "
                    "ein Geschenk, um das viele dich beneiden. Deine einzige Aufgabe: auf dein "
                    "klares Ja und Nein aus dem Bauch zu hören und dich nie zu etwas zu zwingen. "
                    "Was dich anspringt, füllt dich. Was du dir abringst, leert dich.",
        "says_open": "Dass du nicht dafür gebaut bist, wie eine Maschine durchzuarbeiten, und das "
                     "ist völlig in Ordnung. Du hast keine gleichbleibende Arbeitsenergie, dafür "
                     "aber eine besondere Weisheit über Energie selbst und darüber, wann etwas "
                     "genug ist. Deine Lektion: rechtzeitig aufhören, statt dich bis zur "
                     "Erschöpfung durchzuschleppen, nur um mitzuhalten. Ruhe ist bei dir kein "
                     "Versagen, sie ist Teil deiner Natur.",
    },
    "Solarplexus": {
        "theme": "Emotionen und Gefühlswellen",
        "defined": "Du hast einen eigenen emotionalen Rhythmus. Dein Auf und Ab gehört zu dir, und "
                   "deine Klarheit kommt mit der Zeit.",
        "open": "Du nimmst die Gefühle anderer auf und verstärkst sie, und du meidest gern Konflikte, "
                "nur um die Stimmung zu halten.",
        "tip": "Frage dich mitten im Gefühl: Ist das gerade meins, oder habe ich es aufgenommen? Gehe "
               "kurz auf Abstand, dann klärt es sich.",
        "gift": "eine tiefe, echte Gefühlswelt",
        "shadow": "das Aufnehmen fremder Emotionen und das Meiden von Konflikt",
        "says_def": "Dass du ein tief fühlender Mensch mit einem ganz eigenen emotionalen Rhythmus "
                    "bist. Deine Gefühle kommen in Wellen, mal hoch, mal tief, und das ist deine "
                    "normale, gesunde Art zu fühlen, kein Makel und keine Launenhaftigkeit. Deine "
                    "Klarheit reift mit der Zeit, nie im Sturm. Triff darum nichts Wichtiges mitten in "
                    "der Welle, sondern erst, wenn Ruhe eingekehrt ist. Dann trägt deine Entscheidung.",
        "says_open": "Dass du ein außergewöhnlich empathischer Mensch bist, der die Gefühle im Raum "
                     "aufnimmt wie ein Schwamm. Du spürst sofort, wie es anderen geht, oft bevor sie "
                     "es selbst merken. Deine Herausforderung: Du hältst fremde Stimmungen schnell für "
                     "deine eigenen und meidest Streit, nur um bloß die Harmonie zu wahren. Frage dich "
                     "öfter ehrlich: Ist dieses Gefühl gerade wirklich meins? Und traue dich, auch das "
                     "Unbequeme auszusprechen. Deine Feinfühligkeit ist eine Gabe, wenn du bei dir "
                     "bleibst.",
    },
    "Wurzel": {
        "theme": "Antrieb, Druck und Stress",
        "defined": "Du hast einen eigenen, gleichmäßigen Druckrhythmus, der dich verlässlich "
                   "antreibt, ohne dich zu hetzen.",
        "open": "Du hetzt oft, um den Druck endlich loszuwerden, und tust Dinge übereilt, nur damit "
                "sie vom Tisch sind.",
        "tip": "Du musst dich nicht beeilen, um frei zu sein. Der Druck ist nicht deiner, du darfst "
               "dir Zeit lassen.",
        "gift": "ein ruhiger, tragender Antrieb",
        "shadow": "das Hetzen, um den Druck loszuwerden",
        "says_def": "Dass du mit Druck und Stress umgehen kannst, ohne dich davon jagen zu lassen. "
                    "Wo andere kopflos und hektisch werden, bleibst du in deinem Takt. Das ist "
                    "eine stille, verlässliche Stärke, auf die sich auch die Menschen um dich "
                    "herum stützen können.",
        "says_open": "Dass du ein Mensch bist, der viel Energie aus dem Wunsch zieht, endlich "
                     "fertig zu sein. Noch schnell dies, noch rasch das. Nur ist dieser Druck "
                     "meistens geliehen, du hast ihn irgendwann nur aufgenommen. Deine Lektion: "
                     "Nichts muss sofort. Wenn du eins nach dem anderen machst, hört das ständige "
                     "Gehetztsein auf, und du findest zu einer Ruhe, die dir vorher unmöglich "
                     "schien.",
    },
}

# Chiron: die tiefe Wunde und zugleich der Ort deiner größten Heilkraft, nach Zeichen.
CHIRON_SIGN = {
    "Widder": "Tief in dir sitzt die Frage, ob du überhaupt wollen darfst. Vielleicht hast du früh "
              "gelernt, dich zurückzunehmen, damit es keinen Ärger gibt. Deine Wünsche kamen "
              "zuletzt, wenn überhaupt. Und wenn du doch mal für dich eingestanden bist, kam hinterher "
              "dieses schlechte Gefühl, als wärst du zu viel. Deine Heilung beginnt an dem Tag, an "
              "dem du spürst: Du darfst wollen. Du darfst Platz einnehmen. Und du musst dich dafür "
              "bei niemandem entschuldigen. Weil du diesen Kampf so gut kennst, kannst du andere "
              "ermutigen, endlich für sich selbst loszugehen.",
    "Stier": "In dir lebt eine leise Angst, dass es nicht reicht. Nicht genug Geld, nicht genug "
             "Sicherheit, nicht genug von dem, was dich hält. Vielleicht hältst du deshalb fest, "
             "sorgst vor, und trotzdem stellt sich dieses ruhige Genug-Gefühl selten ein. Ganz tief "
             "geht es um deinen eigenen Wert und um die stille Sorge, ohne Leistung oder Besitz "
             "nichts wert zu sein. Deine Heilung beginnt, wenn du spürst: Dein Wert hängt an nichts. "
             "Du bist kostbar, einfach weil es dich gibt. Und weil du diese Angst kennst, schenkst du "
             "anderen genau die Sicherheit, die dir selbst so oft gefehlt hat.",
    "Zwillinge": "Deine Wunde sitzt in deiner Stimme. Vielleicht hat man dir früh das Gefühl "
                 "gegeben, deine Worte zählen nicht. Zu viel, zu wirr, zu unwichtig. Also hast du "
                 "gelernt, dich klein zu reden oder lieber zu schweigen. Bis heute zögerst du "
                 "manchmal, das zu sagen, was wirklich in dir ist. Deine Heilung beginnt, wenn du "
                 "dein eigenes Wort wieder ernst nimmst und es aussprichst, auch wenn deine Stimme "
                 "zittert. Weil du weißt, wie es sich anfühlt, überhört zu werden, hörst du anderen "
                 "wirklich zu.",
    "Krebs": "Ganz tief in dir wohnt die Frage, ob du irgendwo wirklich dazugehörst. Vielleicht hast "
             "du dich als Kind oft allein gefühlt, auch mitten unter Menschen. Also bist du die "
             "geworden, die für andere sorgt, damit du gebraucht wirst und nicht verloren gehst. Aber "
             "wer sorgt für dich? Deine Heilung beginnt, wenn du dir selbst ein Zuhause wirst. Wenn "
             "du die Geborgenheit, die du überall gesucht hast, zuerst in dir findest. Und weil du "
             "diese Sehnsucht so gut kennst, gibst du anderen ein Gefühl von Heimat, das sie nie "
             "vergessen.",
    "Löwe": "Deine Wunde liegt im Gesehenwerden. Vielleicht hast du dich als Kind gezeigt, mit "
            "deiner Freude, deiner ganzen Kreativität, und irgendjemand hat es kleingemacht. Seitdem "
            "gibt es diesen leisen Zweifel: Darf ich strahlen? Ist das nicht zu viel? Also hältst du "
            "dich zurück und spielst nie deine volle Größe. Deine Heilung beginnt, wenn du dich "
            "zeigst, weil es dich von innen freut, ganz ohne auf den Applaus der anderen zu warten. "
            "Weil du diesen Schmerz kennst, siehst du das Licht in anderen und hilfst ihnen, es zu "
            "zeigen.",
    "Jungfrau": "Deine Wunde flüstert dir zu, du seist nicht ganz gut genug. Ganz leise: fast gut, "
                "du musst nur noch das eine verbessern. Und dann das nächste. Vielleicht behandelst "
                "du dich wie ein Projekt, das nie fertig wird, und siehst überall, was noch fehlt, "
                "zuallererst bei dir selbst. Deine Heilung beginnt, wenn du das Unfertige liebevoll "
                "annimmst und begreifst: Du genügst schon jetzt, genau so wie du bist. Und weil du "
                "weißt, wie schwer dieser Satz ist, kannst du ihn einem anderen Menschen schenken.",
    "Waage": "Deine Wunde zeigt sich in Beziehungen. Vielleicht hast du gelernt, dass Frieden "
             "wichtiger ist als deine eigene Meinung. Also hast du dich angepasst, nachgegeben, dich "
             "kleiner gemacht, damit die Verbindung heil bleibt. Und irgendwann wusstest du kaum "
             "noch, was du eigentlich willst. Deine Heilung beginnt, wenn du in der Nähe zu anderen "
             "bei dir selbst bleibst. Eine echte Verbindung hält es aus, dass du du bist. Weil du "
             "diesen Balanceakt kennst, spürst du sofort, wo zwischen Menschen etwas aus dem Lot ist.",
    "Skorpion": "Deine Wunde berührt Ohnmacht und die ganz großen Tiefen. Vielleicht hast du früh "
                "erlebt, wie es ist, wenn dir der Boden weggezogen wird und du keine Kontrolle hast. "
                "Seitdem hältst du lieber fest, wachst und gehst auf Nummer sicher, damit dir das nie "
                "wieder passiert. Aber diese Wachsamkeit ist unendlich anstrengend. Deine Heilung "
                "beginnt, wenn du dem Wandel wieder vertraust. Was zerbricht, macht Raum für etwas "
                "Echteres. Und weil du selbst durch dunkle Nächte gegangen bist, kannst du bei "
                "anderen bleiben, wenn es sonst niemand aushält.",
    "Schütze": "Deine Wunde sitzt im Glauben und in der Frage nach dem Sinn. Vielleicht wurde dir "
               "früh eine Wahrheit übergestülpt, die sich nie ganz nach dir angefühlt hat. Oder du "
               "hast den Glauben an etwas Größeres irgendwann verloren. Seitdem gibt es diese Leere, "
               "dieses Suchen nach dem Wofür. Deine Heilung beginnt, wenn du deiner eigenen Wahrheit "
               "folgst und wieder an etwas glauben darfst, das sich von innen richtig anfühlt. Und "
               "weil du diese Suche kennst, gibst du anderen Hoffnung und Weite.",
    "Steinbock": "Deine Wunde dreht sich um Leistung und Anerkennung. Vielleicht hast du früh "
                 "gespürt, dass Liebe an Bedingungen hängt: sei stark, sei erfolgreich, mach keine "
                 "Fehler. Also hast du funktioniert, dich zusammengerissen, geliefert. Und tief "
                 "drinnen bleibt die Angst, ohne all das nicht genug zu sein. Deine Heilung beginnt, "
                 "wenn du deinen Wert weit jenseits von Erfolg und Applaus fühlst und ausruhen "
                 "darfst, ohne schlechtes Gewissen. Und weil du weißt, wie schwer diese Rüstung ist, "
                 "gibst du anderen die Erlaubnis, einfach Mensch zu sein.",
    "Wassermann": "Deine Wunde ist das alte Gefühl, anders zu sein und nirgends ganz "
                  "dazuzugehören. Vielleicht standst du schon als Kind ein bisschen am Rand und hast "
                  "beobachtet, während die anderen einfach mitgemacht haben. Das hat wehgetan. Also "
                  "hast du dich noch mehr zurückgezogen oder dich überangepasst. Deine Heilung "
                  "beginnt, wenn du dein Anderssein als Geschenk feierst. Genau da, wo du dich fremd "
                  "gefühlt hast, liegt dein Beitrag. Und weil du weißt, wie sich Außenseiter fühlen, "
                  "gibst du anderen das Gefühl, willkommen zu sein, so wie sie sind.",
    "Fische": "Deine Wunde berührt deine Grenzen und eine große, oft namenlose Sehnsucht. Du spürst "
              "so viel, meist mehr als du tragen kannst, und nimmst die Gefühle anderer auf wie ein "
              "Schwamm. Vielleicht weißt du manchmal gar nicht, wo du aufhörst und der andere "
              "anfängt. Und diese Sehnsucht nach etwas, das größer ist als der Alltag, findet selten "
              "einen Ort. Deine Heilung beginnt, wenn du dein Mitgefühl zuerst dir selbst schenkst, "
              "deine Weichheit als Stärke begreifst und lernst, dich sanft abzugrenzen. Weil du so "
              "tief fühlst, tröstest du andere allein durch deine Gegenwart.",
}

# Ein konkreter, liebevoller Tipp, wie man mit der jeweiligen Chiron-Wunde arbeitet.
CHIRON_HEAL_TIP = {
    "Widder": "Übe das Wollen in kleinen Dosen. Sage dir einmal am Tag, laut oder leise, was du gerade "
              "möchtest, ganz ohne Rechtfertigung. Diese Wunde heilt nicht durch Nachdenken, sondern "
              "indem du dir immer wieder erlaubst, Platz einzunehmen, bis es sich normal anfühlt. Sei "
              "dabei geduldig mit dir, du lernst gerade etwas, das dir früh abtrainiert wurde.",
    "Stier": "Erinnere dich täglich an deinen Wert jenseits von Leistung und Besitz. Leg abends eine "
             "Hand aufs Herz und sage dir: Ich bin genug, einfach weil es mich gibt. Und übe, im Kleinen "
             "zu genießen, was schon da ist, statt ständig mehr abzusichern. Jeder Moment echter "
             "Ruhe ist ein Schritt der Heilung.",
    "Zwillinge": "Fang klein an, deiner Stimme wieder zu trauen. Sprich einen Gedanken aus, den du "
                 "sonst geschluckt hättest, auch wenn deine Stimme dabei zittert. Es muss nicht laut "
                 "sein und nicht perfekt. Jedes Mal, wenn du dich hörbar machst, heilt ein Stück dieser "
                 "alten Wunde, und du merkst: Deine Worte zählen doch.",
    "Krebs": "Werde dir selbst zum sicheren Ort. Sorge einmal am Tag ganz bewusst für dich, so "
             "liebevoll, wie du es sonst für andere tust. Diese Wunde heilt, wenn du die Geborgenheit, "
             "die du überall im Außen gesucht hast, langsam in dir selbst aufbaust. Du darfst dein "
             "eigenes Zuhause werden.",
    "Löwe": "Zeige dich in kleinen Schritten, ohne auf Applaus zu warten. Tu etwas, das dir wirklich "
            "Freude macht, und lass dich dabei sehen. Diese Wunde heilt, wenn dein Strahlen aus deiner "
            "eigenen Freude kommt und nicht mehr von der Bestätigung anderer abhängt. Fang bei den "
            "Menschen an, bei denen du dich sicher fühlst.",
    "Jungfrau": "Übe, das Unfertige liebevoll anzunehmen. Sage dir, wenn der innere Kritiker anspringt: "
                "Ich genüge schon jetzt, genau so. Behandle dich so nachsichtig, wie du einen guten "
                "Freund behandeln würdest, der einen Fehler macht. Diese Wunde heilt in der "
                "Sanftheit, nie im Perfektionieren.",
    "Waage": "Übe, in der Nähe zu anderen bei dir selbst zu bleiben. Sprich eine ehrliche Meinung aus, "
             "auch wenn sie unbequem ist und den Frieden kurz stört. Diese Wunde heilt, wenn du "
             "erlebst: Eine echte Verbindung hält es aus, dass du du bist. Du musst dich nicht "
             "kleinmachen, um geliebt zu werden.",
    "Skorpion": "Übe, dem Wandel wieder zu vertrauen, erst mal in kleinen Dingen. Lass bewusst etwas "
                "los, das du sonst festhältst, und schaue, dass du es überlebst. Diese Wunde heilt, "
                "wenn du erlebst, dass nach jedem Zerbrechen Raum für etwas Echteres entsteht. "
                "Kontrolle war dein Schutz, Vertrauen wird deine Freiheit.",
    "Schütze": "Such wieder nach dem, was sich von innen wahr anfühlt, statt nach übernommenen "
               "Wahrheiten. Frage dich bei allem, was du glaubst: Ist das wirklich meins, oder wurde es "
               "mir gesagt? Diese Wunde heilt, wenn du deiner eigenen inneren Richtung folgst und dir "
               "erlaubst, wieder an etwas zu glauben, das dich von innen wärmt.",
    "Steinbock": "Übe, dich auszuruhen, ohne schlechtes Gewissen. Erlaube dir, mal nichts zu leisten "
                 "und trotzdem wertvoll zu sein. Diese Wunde heilt, wenn du im Körper spürst: Du musst "
                 "dir Liebe nicht durch Erfolg verdienen. Fang mit kleinen Pausen an, in denen du "
                 "einfach nur da sein darfst.",
    "Wassermann": "Feiere dein Anderssein, statt es zu verstecken oder zu überspielen. Zeige dich genau "
                  "da, wo du dich sonst fremd fühlst, und finde die Menschen, bei denen du nicht "
                  "dazupassen musst. Diese Wunde heilt, wenn du begreifst: Genau dein anderer Blick "
                  "ist dein Geschenk an die Welt, nicht dein Makel.",
    "Fische": "Übe, dich sanft abzugrenzen, ohne dich dabei schuldig zu fühlen. Frage dich öfter: Ist "
              "dieses Gefühl gerade meins, oder habe ich es aufgenommen? Und schenke dein großes "
              "Mitgefühl zuerst dir selbst. Dann trägt es dich, statt dich zu erschöpfen. Grenzen sind "
              "für dich keine Härte, sondern Selbstschutz.",
}

# Mondknoten-Achse (nach Nordknoten-Zeichen):
#   higher = Higher Self (Nordknoten, wohin du wächst)
#   lower  = Lower Self (Südknoten, dein vertrautes Rückfall-Muster)
#   task   = Lebensaufgabe in einem Satz
#   task_tip = konkreter Weg, wie man diese Lebensaufgabe erfüllt
#   tools  = konkrete Impulse für den Alltag (5-6 pro Achse)
NODE_AXIS = {
    "Widder": {
        "higher": "Du bist hier, um für dich selbst einzustehen. Um deine eigenen Impulse ernst zu nehmen und den Schritt nach vorn zu wagen, auch wenn ihn dir niemand abnimmt. Es geht darum, endlich du zu sein, laut und lebendig, statt immer die nette, angepasste Version.",
        "lower": "Dein vertrautes Muster ist Anpassung. Du willst gefallen, glättest jeden Konflikt und schaust zuerst, was die anderen brauchen. Wahrscheinlich hast du früh gelernt, dass du geliebt wirst, wenn du pflegeleicht bist. Das fühlt sich sicher an. Aber am Ende bist du für alle da, nur nicht für dich.",
        "task": "Deine Lebensaufgabe: dich selbst an die erste Stelle setzen, ohne schlechtes Gewissen.",
        "task_tip": "Fang klein an. Du erfüllst diese Aufgabe nicht mit einem großen Befreiungsschlag, sondern in den vielen leisen Momenten, in denen du dich fragst „Und was will eigentlich ich?“ und dann danach handelst. Jedes ehrliche Nein zu anderen ist ein Ja zu dir. Je öfter du das übst, desto natürlicher fühlt es sich an, für dich selbst da zu sein.",
        "tools": ["Frage dich bei Entscheidungen zuerst: Was will eigentlich ich?", "Übe kleine, klare Ansagen im Alltag, statt dich anzupassen und später innerlich zu grollen.", "Mach den ersten Schritt bewusst allein. Mut wächst im Tun.", "Sage einmal am Tag bewusst nein, ohne dich lang zu erklären.", "Merke dir Momente, in denen du dich übergangen fühlst, das sind deine Übungsfelder.", "Beweg deinen Körper, wenn Wut hochkommt, statt sie herunterzuschlucken."],
    },
    "Stier": {
        "higher": "Du wächst über Ruhe, Beständigkeit und Selbstwert. Du darfst deinem eigenen Tempo vertrauen, das Einfache genießen und Dinge bauen, die bleiben. Weniger Drama, mehr Boden unter den Füßen.",
        "lower": "Dein vertrautes Muster sucht Intensität, Krise und Kontrolle. Du hinterfragst alles bis auf den Grund und misstraust der Ruhe, als wäre sie nur die Stille vor dem Sturm. Diese Daueranspannung kennst du gut. Sie hat dich einmal beschützt. Heute erschöpft sie dich nur noch.",
        "task": "Deine Lebensaufgabe: spüren, dass Sicherheit und Genuss erlaubt sind und nicht erkämpft werden müssen.",
        "task_tip": "Gehe diesen Weg über deinen Körper, nicht über den Kopf. Deine Aufgabe erfüllt sich immer dann, wenn du innehältst und etwas einfach genießt, ohne es dir vorher verdienen zu müssen. Übe, in Ruhe auszuhalten, dass gerade nichts brennt und trotzdem alles gut ist. Genau in diesen stillen Momenten wächst du.",
        "tools": ["Bau dir feste kleine Routinen, die dir guttun.", "Wenn du ins Grübeln kippst, komm zurück in den Körper: Natur, Essen, Berührung.", "Vertraue darauf, dass etwas auch dann bleibt, wenn du es nicht kontrollierst.", "Genieß bewusst eine Sache am Tag mit allen Sinnen, ganz ohne Ziel.", "Wenn Misstrauen hochkommt, frage dich: Ist die Gefahr echt oder nur ein alter Reflex?", "Bleibe bei einer guten Sache, statt sie aus Unruhe zu zerreden."],
    },
    "Zwillinge": {
        "higher": "Du wächst über Neugier und Nähe im Alltag. Du bist hier, um Fragen zu stellen, wirklich zuzuhören und in den vielen kleinen Verbindungen präsent zu sein. Das Leben findet im Kleinen statt, direkt vor dir.",
        "lower": "Dein vertrautes Muster will recht haben und die große Wahrheit verkünden. Du weißt schon Bescheid, belehrst und überspringst das Detail. Vielleicht fühlst du dich sicherer, wenn du der bist, der die Antwort hat. Aber genau das entfernt dich vom echten Gegenüber.",
        "task": "Deine Lebensaufgabe: mehr fragen als dozieren und im Nahen ankommen.",
        "task_tip": "Übe dich zuerst im Zuhören, bevor du im Reden gut sein willst. Deine Aufgabe erfüllt sich in den kleinen, echten Gesprächen deines Alltags, wenn du wirklich neugierig bleibst, statt die Antwort schon zu kennen. Stelle eine Frage mehr, als dir angenehm ist, und lass dich von der Antwort überraschen.",
        "tools": ["Stelle echte Fragen und höre zu Ende zu, bevor du deine Meinung sagst.", "Sammle konkrete Fakten statt fertiger Überzeugungen.", "Pflege die kleinen Kontakte in deinem Alltag, dort liegt gerade dein Wachstum.", "Frage heute jemanden etwas und frage dann noch einmal nach.", "Lass ein Gespräch offen enden, ohne das letzte Wort zu haben.", "Notier dir konkrete Beobachtungen aus deinem Tag statt großer Theorien."],
    },
    "Krebs": {
        "higher": "Du wächst über Gefühl und Nähe. Du darfst dich selbst nähren, verletzlich sein und dich anlehnen. Du musst nicht die Starke sein, die alles allein trägt.",
        "lower": "Dein vertrautes Muster greift zu Kontrolle, Pflicht und Härte gegen dich selbst. Du trägst alles allein und organisierst deine Gefühle weg, weil du gelernt hast, dass Schwäche gefährlich ist. Diese Rüstung ist schwer. Und einsam.",
        "task": "Deine Lebensaufgabe: dich lehnen und fühlen dürfen, ohne die Kontrolle zu verlieren.",
        "task_tip": "Diese Aufgabe erfüllst du nicht durch mehr Leisten, sondern durch mehr Zulassen. Fang damit an, dich selbst zu fragen, wie es dir gerade wirklich geht, bevor du für alle anderen sorgst. Jedes Mal, wenn du Hilfe annimmst, statt alles allein zu tragen, kommst du deiner Aufgabe ein Stück näher.",
        "tools": ["Frage dich öfter: Wie geht es mir gerade? statt: Was muss ich noch leisten?", "Lass Nähe zu und bitte um Hilfe, auch wenn es ungewohnt ist.", "Gönn dir Fürsorge, ohne sie dir erst zu verdienen.", "Erlaube dir einmal am Tag, verletzlich zu sein statt stark.", "Sage jemandem ehrlich, wie es dir geht, ohne es abzuschwächen.", "Wenn du in Kontrolle kippst, atme und frage: Was fühle ich gerade?"],
    },
    "Löwe": {
        "higher": "Du wächst über Sichtbarkeit und Herz. Du bist hier, um aus dir heraus zu schaffen, Freude auszudrücken und deine eigene Bühne einzunehmen. Dein Strahlen darf gesehen werden.",
        "lower": "Dein vertrautes Muster versteckt dich in der Gruppe. Du bleibst cool, distanziert und willst bloß nicht auffallen. Vielleicht ist es dir sicherer, einer von vielen zu sein, als dich einzeln zu zeigen und vielleicht abgelehnt zu werden. Aber im Verstecken verkümmert dein Herz.",
        "task": "Deine Lebensaufgabe: dich zeigen und dein Herz sprechen lassen, auch wenn es sich exponiert anfühlt.",
        "task_tip": "Deine Aufgabe wächst mit jedem kleinen Mut, sichtbar zu sein. Warte nicht, bis du dich sicher genug fühlst, das Gefühl kommt erst durch das Tun. Zeige etwas von dir, auch wenn dein Herz dabei klopft. Genau in diesen Momenten wirst du zu dem Menschen, der du sein sollst.",
        "tools": ["Erlaube dir, im Mittelpunkt zu stehen, statt dich hinter dem Wir zu verstecken.", "Schaff etwas, das wirklich von dir kommt, und zeige es.", "Sage öfter ich statt man, vor allem bei deinen Wünschen.", "Teil heute etwas, das von Herzen von dir kommt, mit einem Menschen.", "Nimm ein Kompliment an, ohne es kleinzureden.", "Tu etwas, das dir Freude macht, ganz ohne Nutzen."],
    },
    "Jungfrau": {
        "higher": "Du wächst über Struktur und geerdete Fürsorge. Du darfst im Alltag ankommen, dir mit klaren, kleinen Schritten helfen und im Konkreten wirken. Ordnung im Außen bringt Ruhe in dein Innen.",
        "lower": "Dein vertrautes Muster verliert sich, flüchtet oder lässt sich treiben. Grenzen verschwimmen, und du rutschst schnell in das Gefühl, dass das Leben einfach mit dir passiert. Der Rückzug ins Diffuse fühlt sich weich an. Aber er hält dich davon ab, dein Leben wirklich anzupacken.",
        "task": "Deine Lebensaufgabe: im Alltag ankommen und dir mit klaren Schritten selbst helfen.",
        "task_tip": "Diese Aufgabe erfüllt sich im Konkreten, nicht im großen Plan. Nimm dir eine kleine Sache vor und bring sie zu Ende, das erdet dich mehr als jede gute Absicht. Kümmere dich Schritt für Schritt um deinen Körper, deinen Raum, deinen Tag. Ordnung im Kleinen bringt Ruhe ins Große.",
        "tools": ["Bring Ordnung in eine kleine Ecke deines Lebens, das erdet dich sofort.", "Setze klare Grenzen, statt in allem zu verschwimmen.", "Kümmere dich konkret um deinen Körper und deinen Alltag, Schritt für Schritt.", "Bring heute eine einzige Sache zu Ende, egal wie klein.", "Sorg konkret für deinen Körper: Wasser, Schlaf, Bewegung.", "Wenn du dich verlierst, mach eine kleine, greifbare Aufgabe."],
    },
    "Waage": {
        "higher": "Du wächst über Beziehung und Ausgleich. Du bist hier, um andere einzubeziehen, fair zu sein und gemeinsam zu gehen, statt alles allein zu stemmen. Verbindung macht dich nicht schwächer, sie macht dich reicher.",
        "lower": "Dein vertrautes Muster zieht alles im Alleingang durch. Du bist ungeduldig, gehst zu schnell vor und übergehst die anderen. Wahrscheinlich hast du gelernt, dass du dich auf niemanden verlassen kannst, außer auf dich. Das macht dich stark, aber auch sehr einsam.",
        "task": "Deine Lebensaufgabe: den anderen wirklich mitdenken und gemeinsam statt gegeneinander handeln.",
        "task_tip": "Deine Aufgabe erfüllt sich, sobald du andere wirklich mit an den Tisch holst, statt alles allein zu stemmen. Übe, um eine Meinung zu bitten, bevor du entscheidest, und auszuhalten, dass es dadurch langsamer geht. Verbindung ist hier dein Wachstum, nicht deine Schwäche.",
        "tools": ["Hol dir vor Entscheidungen bewusst die Sicht des anderen ein.", "Übe Geduld, wenn dich der Impuls packt, sofort allein loszurennen.", "Such Kompromisse aktiv, statt sie als Niederlage zu sehen.", "Bitte heute jemanden um seine Sicht, bevor du entscheidest.", "Halte einmal inne, wenn du am liebsten sofort allein loslegst.", "Lass dir helfen und nimm die Hilfe wirklich an."],
    },
    "Skorpion": {
        "higher": "Du wächst über Tiefe und echte Verbindung. Du darfst dich einlassen, teilen, die Kontrolle loslassen und dich verwandeln. Erst wenn du dich wirklich zeigst, wird Nähe echt.",
        "lower": "Dein vertrautes Muster hält fest. An Besitz, an Gewohntem, an dem, was sicher ist. Veränderung fühlt sich teuer und bedrohlich an, also bleibst du lieber beim Bekannten, auch wenn es dich längst nicht mehr nährt. Diese Bequemlichkeit ist ein weiches Gefängnis.",
        "task": "Deine Lebensaufgabe: dich einlassen und loslassen, auch wenn es unbequem wird.",
        "task_tip": "Diese Aufgabe erfüllt sich im bewussten Loslassen. Fang mit etwas Kleinem an, das du nur aus Gewohnheit festhältst, und lass es gehen. Jedes Mal, wenn du dem Wandel vertraust, statt festzuklammern, wirst du freier. Was echt ist, bleibt auch ohne deinen festen Griff.",
        "tools": ["Lass bewusst etwas los, an dem du aus Gewohnheit festhältst.", "Wag echte Tiefe, statt an der Oberfläche sicher zu bleiben.", "Frage dich: Halte ich das, weil es stimmt, oder nur, weil es vertraut ist?", "Lass heute eine Kleinigkeit los, an der du hängst.", "Sage einem Menschen etwas Echtes, das du sonst für dich behältst.", "Vertraue darauf, dass nach einem Ende Platz für Neues entsteht."],
    },
    "Schütze": {
        "higher": "Du wächst über Sinn, Weite und Vertrauen. Du bist hier, um für deine eigene Wahrheit einzustehen und das große Bild zu sehen. Nicht jede Kleinigkeit muss belegt sein, manches darfst du einfach glauben.",
        "lower": "Dein vertrautes Muster verzettelt sich. Du sammelst alle Meinungen, bleibst an der Oberfläche und legst dich bloß nicht fest. Solange du dich nicht entscheidest, kann nichts schiefgehen, denkst du. Aber diese ständige Unverbindlichkeit lässt dich nie irgendwo ankommen.",
        "task": "Deine Lebensaufgabe: dich auf deine eigene Wahrheit festlegen und ihr folgen.",
        "task_tip": "Deine Aufgabe erfüllst du, indem du dich entscheidest und dranbleibst, statt ewig weiterzusammeln. Wähle eine Richtung, die sich von innen richtig anfühlt, und gehe sie eine Weile, auch ohne alle Informationen. Vertrauen wächst, wenn du dich festlegst, nicht davor.",
        "tools": ["Triff eine Entscheidung und bleibe eine Weile dran, statt neu zu sammeln.", "Frage nach dem Warum hinter den Fakten, nicht nur nach mehr Fakten.", "Vertraue deiner inneren Richtung, auch ohne alle Informationen.", "Triff heute eine Entscheidung, die du schon zu lange aufschiebst.", "Bleibe eine Weile bei einer Sache, bevor du Neues suchst.", "Frage dich: Fühlt sich das von innen wahr an? und folge dem."],
    },
    "Steinbock": {
        "higher": "Du wächst über Verantwortung und Struktur. Du darfst erwachsen werden, dir sichtbare Ziele setzen und erwachsen und verlässlich für dich selbst sorgen. Du darfst dein Leben in die Hand nehmen.",
        "lower": "Dein vertrautes Muster macht dich klein und abhängig. Du verkriechst dich im Vertrauten und wartest leise, dass jemand kommt und es für dich löst. Vielleicht fühlt sich Verantwortung wie eine zu große Last an. Aber im Warten bleibst du in einer Rolle, die dir längst zu eng ist.",
        "task": "Deine Lebensaufgabe: selbst die verantwortliche, erwachsene Person in deinem Leben sein und deine Ziele ernst nehmen.",
        "task_tip": "Diese Aufgabe erfüllst du, indem du aufhörst zu warten, dass jemand kommt und es für dich löst. Nimm eine Sache in deinem Leben ganz in die Hand, so klein sie auch ist. Setze dir ein echtes Ziel und gehe den ersten Schritt. Du darfst dir selbst der verlässliche Erwachsene sein, den du dir früher gewünscht hättest.",
        "tools": ["Setze dir ein konkretes Ziel und gehe es in kleinen, festen Schritten an.", "Übernimm Verantwortung für deine Lage, statt zu warten.", "Tröste dich selbst und mach dann den nächsten Schritt.", "Übernimm heute für eine Sache selbst die volle Verantwortung.", "Mach den ersten kleinen Schritt auf ein Ziel zu, noch heute.", "Frage dich: Worauf warte ich gerade? und werde selbst aktiv."],
    },
    "Wassermann": {
        "higher": "Du wächst über Gemeinschaft und Freiheit. Du bist hier, um mit genau deinem Anderssein zu etwas Größerem beizutragen. Du gehörst dazu, ohne dich verbiegen zu müssen.",
        "lower": "Dein vertrautes Muster braucht Anerkennung und den Mittelpunkt. Es geht schnell um dich, um dein Bild, um die Frage, wie du dastehst. Wahrscheinlich hast du gelernt, dass du nur zählst, wenn du besonders bist. Aber dieser Hunger nach Applaus macht nie wirklich satt.",
        "task": "Deine Lebensaufgabe: Teil von etwas Größerem sein, ohne ständig gesehen werden zu müssen.",
        "task_tip": "Deine Aufgabe erfüllt sich, sobald du etwas beiträgst, ohne auf Applaus zu schielen. Such dir eine Sache, die größer ist als du, und gib dich hinein. Die Erfüllung liegt nicht im Gesehenwerden, sondern im Dazugehören, ganz als der eigene Mensch, der du bist.",
        "tools": ["Trage zu einer Sache bei, ohne auf Applaus zu warten.", "Freu dich am Erfolg anderer, statt ihn mit deinem zu vergleichen.", "Steh zu deinem Anderssein, es ist dein Beitrag, nicht dein Makel.", "Trage heute zu etwas bei, ohne dass es jemand mitbekommt.", "Freu dich ehrlich über den Erfolg eines anderen Menschen.", "Schließ dich einer Sache an, die größer ist als du."],
    },
    "Fische": {
        "higher": "Du wächst über Vertrauen und Mitgefühl. Du darfst loslassen, weich werden und dich mit etwas Größerem verbinden. Du musst nicht alles im Griff haben, um sicher zu sein.",
        "lower": "Dein vertrautes Muster perfektioniert und kontrolliert. Du verlierst dich in Kritik, Sorge und Analyse, weil dir das ein Gefühl von Kontrolle gibt. Solange du an allem arbeitest, kann dich nichts überraschen, glaubst du. Aber dieses ständige Anspannen raubt dir die Leichtigkeit.",
        "task": "Deine Lebensaufgabe: vertrauen und loslassen, statt alles kontrollieren zu wollen.",
        "task_tip": "Diese Aufgabe erfüllst du, indem du bewusst etwas unperfekt lässt und dann merkst: Die Welt trägt trotzdem. Übe, die Kontrolle für Momente aus der Hand zu geben und einfach zu vertrauen. Deine Weichheit ist keine Schwäche, sie ist dein Weg. Je öfter du loslässt, desto leichter wird dein Leben.",
        "tools": ["Lass bewusst etwas unperfekt und schaue, dass die Welt trotzdem trägt.", "Nimm dir Momente der Stille, in denen du nichts optimieren musst.", "Sei so sanft mit dir, wie du es mit einem lieben Menschen wärst.", "Lass heute bewusst eine Sache unfertig und beobachte, was passiert.", "Nimm dir zehn Minuten Stille, in denen nichts verbessert werden muss.", "Gib die Kontrolle über eine Kleinigkeit ab und vertraue darauf."],
    },
}

SIGN_ELEMENT = {
    "Widder": "Feuer", "Stier": "Erde", "Zwillinge": "Luft", "Krebs": "Wasser",
    "Löwe": "Feuer", "Jungfrau": "Erde", "Waage": "Luft", "Skorpion": "Wasser",
    "Schütze": "Feuer", "Steinbock": "Erde", "Wassermann": "Luft", "Fische": "Wasser",
}

# Emotionale Zeichen-Essenz (2 Sätze), fließt hinter dem Planeten-Satz weiter.
SIGN_EMOTION = {
    "Widder": "Du trägst ein Feuer in dir, das losgehen will, sobald es etwas spürt. Warten fällt "
              "dir schwer, und manchmal bist du schneller unterwegs, als dein Umfeld folgen kann. "
              "Genau diese mutige Direktheit bringt Bewegung in dein Leben und erlaubt dir, für dich "
              "einzustehen, wenn es darauf ankommt.",
    "Stier": "Du sehnst dich nach Ruhe, Sicherheit und Dingen, die bleiben. Du genießt mit allen "
             "Sinnen und brauchst festen Boden unter den Füßen, um dich wirklich fallen zu lassen. "
             "Menschen fühlen sich bei dir geborgen, weil du eine Verlässlichkeit ausstrahlst, auf "
             "die man sich stützen kann.",
    "Zwillinge": "Dein Geist ist ständig in Bewegung, neugierig auf alles, was es zu entdecken und "
                 "zu bereden gibt. Du kommst über Worte in Verbindung und bringst Leichtigkeit "
                 "dorthin, wo es sonst schwer würde. Manchmal springst du von Thema zu Thema, und "
                 "genau diese wache Vielseitigkeit ist dein Geschenk.",
    "Krebs": "Du fühlst tiefer, als du es oft nach außen zeigst, und Nähe ist für dich wie ein "
             "Zuhause. Du spürst feinfühlig, was andere brauchen, oft bevor sie es selbst wissen. In "
             "deiner Gegenwart fühlen sich Menschen sicher und gehalten, weil du Räume schaffst, in "
             "denen man einfach sein darf.",
    "Löwe": "In dir wohnt eine Wärme, die gesehen werden will und andere zum Leuchten bringt. Wenn "
            "du aus dem Herzen heraus lebst, ziehst du Menschen an und schenkst ihnen Mut. Du bist "
            "am schönsten, wenn du dich traust, groß zu sein, ganz ohne dich dafür zu entschuldigen.",
    "Jungfrau": "Du hast ein feines Gespür für das, was noch besser werden kann, und einen echten "
                "Wunsch zu helfen. Deine Liebe zeigt sich im Detail, in der Sorgfalt und in der "
                "stillen Art, für andere da zu sein. Wenn du diese Güte auch dir selbst schenkst, "
                "wird deine Gabe zur Quelle statt zur Last.",
    "Waage": "Du sehnst dich nach Harmonie, Schönheit und einem Miteinander auf Augenhöhe. Du "
             "spürst Ungleichgewicht sofort und hast die Gabe, zwischen Menschen wieder Frieden zu "
             "stiften. Deine Aufgabe ist, dabei nie dich selbst zu vergessen, denn ein echter "
             "Ausgleich schließt dich mit ein.",
    "Skorpion": "Du gehst dorthin in die Tiefe, wo es echt wird und andere lieber wegschauen. Deine "
                "Intensität kann verwandeln, und du hast die Kraft, aus Krisen gestärkt "
                "hervorzugehen. Menschen spüren, dass sie dir nichts vormachen können, und genau das "
                "macht dich zu jemandem, dem man wirklich vertraut.",
    "Schütze": "In dir lebt eine Weite, die nach Sinn, Freiheit und dem großen Ganzen sucht. Du "
               "brauchst Horizont, um zu atmen, und steckst andere mit deinem Vertrauen ins Leben "
               "an. Wenn du deiner eigenen Wahrheit folgst, wirst du zu dem Menschen, der anderen "
               "wieder Hoffnung gibt.",
    "Steinbock": "Du trägst eine stille Kraft und Ausdauer in dir, die über Jahre etwas Bleibendes "
                 "aufbaut. Verantwortung schreckt dich nicht, und auf dein Wort kann man sich "
                 "verlassen. Dein wichtiger Lernweg ist, dir zu erlauben, auch mal zu ruhen, ohne "
                 "dich dafür schuldig zu fühlen.",
    "Wassermann": "Du bist auf eine schöne Weise anders und siehst die Welt von einem Punkt aus, "
                  "den sonst kaum jemand einnimmt. Deine Freiheit ist dir heilig, und dein eigener "
                  "Weg macht auch anderen Mut, sie selbst zu sein. Genau da, wo du dich manchmal "
                  "fremd gefühlt hast, liegt dein wertvollster Beitrag.",
    "Fische": "Du spürst mehr, als sich in Worte fassen lässt, und trägst ein großes Mitgefühl in "
              "dir. Deine Weichheit ist eine Stärke, und deine Fantasie öffnet Türen zu einer Welt "
              "hinter der sichtbaren. Wenn du lernst, dich sanft abzugrenzen, wird dein tiefes "
              "Fühlen zum Geschenk, ohne dich zu überfluten.",
}

# Mehrere gleichwertige Fassungen je Sternzeichen. Stehen bei jemandem drei Planeten
# im selben Zeichen, bekam bisher jeder wortwörtlich denselben Text. Jetzt rotiert die
# Deutung durch, sodass sich innerhalb eines Bauplans nichts wiederholt.
# Fassung 0 ist jeweils der bisherige Text aus SIGN_EMOTION.
# Weitere gleichwertige Fassungen je Sternzeichen. Stehen bei jemandem drei Planeten
# im selben Zeichen, bekam bisher jeder wortwörtlich denselben Text. Zusammen mit
# SIGN_EMOTION ergibt das vier Fassungen, durch die die Deutung durchrotiert.
SIGN_VOICES_EXTRA = {
    "Widder": [
        "In dir sitzt ein Startimpuls, der keine langen Vorreden mag. Du merkst sofort, wenn etwas "
        "dran ist, und bist oft schon unterwegs, während andere noch überlegen. Diese Klarheit im "
        "Handeln ist deine Kraft, auch wenn sie hin und wieder anecken darf.",
        "Du bist am lebendigsten, wenn etwas anfängt. Stillstand macht dich unruhig, und du sagst "
        "lieber einmal zu deutlich, was du willst, als es hinunterzuschlucken. Genau dieser Mut "
        "zur ersten Bewegung öffnet dir Türen, vor denen andere stehen bleiben.",
        "Deine Energie will nach vorn. Du gehst Dinge frontal an, ohne Umweg, und ziehst andere "
        "durch dein Tempo einfach mit. Wenn du lernst, kurz innezuhalten, bevor du losläufst, wird "
        "aus deinem Feuer eine Kraft, die trägt statt zu verbrennen.",
    ],
    "Stier": [
        "Du brauchst Dinge, die halten. Schnelle Wechsel machen dich nicht schneller, sie machen "
        "dich müde, denn deine Kraft kommt aus dem, was bleibt. Was du einmal aufgebaut hast, hat "
        "Bestand, und darauf können sich Menschen wirklich stützen.",
        "In dir wohnt eine ruhige Beharrlichkeit, die sich nicht hetzen lässt. Du nimmst dir Zeit "
        "für Schönes, für gutes Essen, für Berührung, für alles, was der Körper versteht. Diese "
        "Sinnlichkeit ist keine Nebensache, sie ist deine Art, im Leben anzukommen.",
        "Du bist ein Mensch mit Bodenhaftung. Erst wenn du sicher stehst, kannst du dich wirklich "
        "öffnen, und dieses Bedürfnis nach festem Grund ist völlig berechtigt. Wenn du deinen "
        "Boden hast, wirst du großzügig, warm und erstaunlich unerschütterlich.",
    ],
    "Zwillinge": [
        "Du denkst in Verbindungen. Wo andere ein Thema sehen, siehst du drei, und du bringst "
        "Menschen und Ideen zusammen, die sonst nie voneinander gehört hätten. Diese schnelle "
        "Auffassungsgabe ist ein Geschenk, auch wenn sie dich manchmal selbst überholt.",
        "Sprache ist dein Zuhause. Du klärst dich, indem du redest, und ein gutes Gespräch tut dir "
        "oft mehr als jede Ruhepause. Deine Leichtigkeit nimmt schweren Momenten die Wucht, und "
        "das merken die Menschen um dich herum sofort.",
        "Du langweilst dich schneller als andere, und das ist keine Unart. Dein Kopf braucht "
        "Futter, Wechsel und neue Eindrücke, um wach zu bleiben. Wenn du dir erlaubst, viele Dinge "
        "gleichzeitig zu lieben, statt dich zu einer Sache zu zwingen, blühst du auf.",
    ],
    "Krebs": [
        "Du nimmst Stimmungen auf wie ein Schwamm, oft ohne es zu wollen. Zuhause ist für dich "
        "kein Ort, sondern ein Gefühl, und du baust es überall dort, wo du dich sicher fühlst. "
        "Diese Fähigkeit, Geborgenheit herzustellen, haben nur wenige Menschen.",
        "Dein Panzer ist echt, und dahinter liegt etwas sehr Weiches. Du zeigst es nicht jedem, "
        "und das ist auch richtig so. Wer es sehen darf, erlebt eine Zärtlichkeit und eine Treue, "
        "die selten geworden sind.",
        "Du erinnerst dich an Dinge, die andere längst vergessen haben, an Sätze, an Blicke, an "
        "kleine Verletzungen. Dieses Gedächtnis des Herzens macht dich verletzlich und zugleich "
        "unglaublich fürsorglich. Achte darauf, dass du auch dich selbst mit dieser Sorgfalt "
        "behandelst.",
    ],
    "Löwe": [
        "Du hast eine natürliche Ausstrahlung, die einen Raum wärmer macht. Wenn du dich "
        "zurücknimmst, um bloß niemanden zu überstrahlen, wird es für alle grauer, nicht nur für "
        "dich. Dein Leuchten ist kein Egoismus, es ist ein Geschenk an andere.",
        "In dir steckt eine große Freigebigkeit. Du gibst gern, du feierst gern, und du gönnst "
        "anderen ihren Moment von Herzen. Was du dafür brauchst, ist echte Anerkennung, und die "
        "darfst du ruhig einfordern, statt heimlich darauf zu warten.",
        "Du willst mit dem Herzen bei der Sache sein, sonst geht es nicht. Halbe Dinge langweilen "
        "dich, und Verstellung fällt dir schwer. Genau diese Echtheit ist der Grund, warum "
        "Menschen dir folgen, lange bevor du irgendetwas beweisen musst.",
    ],
    "Jungfrau": [
        "Du siehst die Details, die anderen entgehen. Was für dich selbstverständlich ist, "
        "empfinden andere als große Aufmerksamkeit, und deine Hilfe kommt fast immer genau dort "
        "an, wo sie gebraucht wird. Nur der Maßstab, den du an dich selbst legst, darf "
        "freundlicher werden.",
        "Ordnung ist für dich kein Zwang, sie ist Beruhigung. Wenn außen etwas an seinem Platz "
        "ist, wird es innen leiser, und aus dieser Klarheit heraus bewegst du erstaunlich viel. "
        "Deine Sorgfalt ist eine Form von Liebe, die selten laut wird.",
        "Du willst Dinge richtig machen, nicht schnell. Das kostet dich manchmal Nerven, bringt "
        "aber eine Verlässlichkeit hervor, auf die sich Menschen blind verlassen. Erlaube dir "
        "zwischendurch, etwas gut sein zu lassen, bevor es perfekt ist.",
    ],
    "Waage": [
        "Du merkst sofort, wenn zwischen Menschen etwas kippt. Diese Antenne macht dich zu "
        "jemandem, bei dem Gespräche wieder möglich werden, und du bringst Leichtigkeit in "
        "Situationen, die festgefahren wirken. Achte nur darauf, dass du dabei eine eigene Meinung "
        "behalten darfst.",
        "Schönheit ist für dich kein Luxus. Ein stimmiger Raum, ein guter Ton zwischen Menschen, "
        "ein Bild, das passt, all das nährt dich wirklich. Du gestaltest, wo andere nur "
        "einrichten, und das spürt jeder, der zu dir kommt.",
        "Entscheidungen fallen dir schwer, weil du beide Seiten wirklich siehst. Das ist keine "
        "Schwäche, das ist Gerechtigkeitssinn. Wenn du übst, dich trotzdem zu entscheiden, auch "
        "wenn nicht alle zufrieden sind, wächst du weit über dich hinaus.",
    ],
    "Skorpion": [
        "Oberflächliches hält dich nicht. Du willst wissen, was wirklich läuft, und du merkst es "
        "meistens, bevor es jemand ausspricht. Diese Klarheit kann unbequem sein, sie macht dich "
        "aber zu einem Menschen, dem man die Wahrheit zutraut.",
        "Du hast schon mehr als einmal etwas hinter dir gelassen und bist als jemand anderes "
        "wieder aufgetaucht. Diese Fähigkeit, dich zu häuten, ist deine größte Kraft. Was dich "
        "fast umgeworfen hat, ist am Ende zu deinem Fundament geworden.",
        "Deine Gefühle sind kein Rinnsal, sie sind ein Strom. Du liebst, misstraust und schützt "
        "mit ganzer Wucht, und halbe Sachen gibt es bei dir nicht. Solange du diese Kraft nicht "
        "gegen dich selbst richtest, ist sie eine echte Verwandlungskraft.",
    ],
    "Schütze": [
        "Du brauchst das Gefühl, dass es weitergeht. Enge Räume, enge Regeln und enge Gedanken "
        "rauben dir Luft, und du findest fast immer eine Tür, wo andere eine Wand sehen. Dieser "
        "Optimismus ist keine Naivität, er ist gelebtes Vertrauen.",
        "Dich zieht die große Frage, nicht das Kleingedruckte. Du willst verstehen, wofür das "
        "alles gut ist, und teilst deine Erkenntnisse gern und laut. Menschen kommen zu dir, wenn "
        "sie den Blick wieder heben wollen.",
        "Ehrlichkeit ist dir wichtiger als Höflichkeit, und das eckt hin und wieder an. Dafür weiß "
        "jeder, woran er bei dir ist. Wenn du deine Direktheit mit ein wenig Wärme umhüllst, wird "
        "sie zu genau dem, was andere brauchen.",
    ],
    "Steinbock": [
        "Du denkst in Jahren, nicht in Wochen. Was du beginnst, soll tragen, und dafür nimmst du "
        "Umwege und Mühe in Kauf, die andere längst gescheut hätten. Diese Geduld ist der Grund, "
        "warum bei dir etwas entsteht, das bleibt.",
        "Verantwortung hast du oft früh übernommen, vielleicht früher als nötig. Du bist der "
        "Mensch, der die Dinge trägt, wenn es eng wird, und das wissen alle um dich herum. Dir "
        "selbst darfst du dieselbe Nachsicht schenken, die du anderen so leicht gibst.",
        "Nach außen wirkst du ruhig und gefasst, während innen ein hoher Anspruch arbeitet. Erfolg "
        "fühlt sich für dich selten nach genug an. Erlaube dir, das Erreichte wirklich "
        "anzuschauen, bevor du schon das Nächste angehst.",
    ],
    "Wassermann": [
        "Du denkst um die Ecke, und zwar ohne es zu üben. Regeln überzeugen dich nur, wenn sie "
        "einen Sinn haben, und du fragst nach, wo andere nicken. Dieser eigene Kopf hat dich "
        "manchmal einsam gemacht und bringt dich am Ende immer weiter.",
        "Du siehst schon, wohin es geht, während andere noch beim Jetzt sind. Dieses Vorausdenken "
        "macht dich zu jemandem, der Dinge in Bewegung bringt, auch wenn es erst viel später "
        "jemand versteht. Bleibe deinem Blick treu, auch wenn er unbequem ist.",
        "Freiheit ist für dich keine Laune, sie ist eine Lebensbedingung. Nähe geht bei dir nur "
        "mit Luft zum Atmen, und wer das versteht, bekommt eine ungewöhnlich treue Verbundenheit. "
        "Deine Art, anders zu sein, gibt anderen die Erlaubnis, es auch zu sein.",
    ],
    "Fische": [
        "Die Grenze zwischen dir und anderen ist dünn. Du fühlst mit, ohne es zu entscheiden, und "
        "trägst dann Stimmungen mit dir herum, die nie deine waren. Dieselbe Durchlässigkeit ist "
        "der Grund, warum Menschen sich bei dir verstanden fühlen.",
        "In dir lebt eine reiche innere Welt, in die du dich zurückziehen kannst. Musik, Bilder, "
        "Träume und Stille sind für dich keine Flucht, sie sind Nahrung. Aus dieser Quelle kommt "
        "eine Schöpferkraft, um die viele dich beneiden.",
        "Du sehnst dich nach etwas, das größer ist als der Alltag, und diese Sehnsucht "
        "verschwindet nie ganz. Sie macht dich weich und manchmal auch traurig. Wenn du ihr einen "
        "Platz gibst, statt sie zu betäuben, wird sie zu deinem tiefsten Kompass.",
    ],
}

# Fassung 0 ist immer der Text aus SIGN_EMOTION, damit beide nie auseinanderlaufen.
SIGN_VOICES = {sg: [txt] + SIGN_VOICES_EXTRA.get(sg, [])
               for sg, txt in SIGN_EMOTION.items()}


_ECHO_STOP = {"deine", "deiner", "deinem", "deinen", "menschen", "leben", "andere",
              "anderen", "dinge", "dingen", "diese", "dieser"}


def _schlagworte(text):
    """Sinntragende Substantive eines Textes, klein und ohne Füllwörter."""
    return {w.lower() for w in re.findall(r"[A-ZÄÖÜ][a-zäöüß]{4,}", text or "")} - _ECHO_STOP


def sign_voice(sign, seen=None, ohne_echo=""):
    """Zeichentext für eine Position.

    `seen` merkt sich die schon vergebenen Fassungen, damit zwei Planeten im selben
    Zeichen nie denselben Text bekommen. `ohne_echo` ist der Text, der direkt davor
    steht, also die Planeteneinleitung. Wo es geht, wird eine Fassung gewählt, die
    kein Wort daraus wiederholt, sonst steht "Feuer" oder "Kraft" zweimal im Absatz.
    """
    voices = SIGN_VOICES.get(sign) or [SIGN_EMOTION.get(sign, "")]
    if seen is None:
        return voices[0]
    benutzt = seen.setdefault("_zeichen", {}).setdefault(sign, [])
    frei = [i for i in range(len(voices)) if i not in benutzt] or list(range(len(voices)))
    echo = _schlagworte(ohne_echo)
    wahl = next((i for i in frei if not (_schlagworte(voices[i]) & echo)), frei[0])
    benutzt.append(wahl)
    return voices[wahl]



# Kurzform der Zeichenstärke für das Kapitel "Deine größten Stärken". Dort stand
# vorher der komplette SIGN_EMOTION-Absatz, also wortgleich das, was ohnehin schon
# auf der Sonnen-Karte im Natalchart steht.
SIGN_STRENGTH = {
    "Widder": "dein Mut, den ersten Schritt zu machen, und deine Fähigkeit, für dich einzustehen, "
        "wenn es darauf ankommt",
    "Stier": "deine Verlässlichkeit und die Ruhe, mit der du etwas aufbaust, das wirklich hält",
    "Zwillinge": "deine wache Neugier und die Leichtigkeit, mit der du Menschen und Gedanken "
        "verbindest",
    "Krebs": "dein feines Gespür für das, was andere brauchen, und deine Gabe, Geborgenheit zu "
        "schaffen",
    "Löwe": "deine Herzenswärme und die Kraft, andere zum Leuchten zu bringen, einfach weil du da "
        "bist",
    "Jungfrau": "dein Blick fürs Detail und die stille Sorgfalt, mit der du für andere da bist",
    "Waage": "dein Sinn für Ausgleich und Schönheit und die Gabe, zwischen Menschen wieder Frieden "
        "zu stiften",
    "Skorpion": "deine Tiefe und die seltene Kraft, aus Krisen gestärkt hervorzugehen",
    "Schütze": "deine Weite, dein Vertrauen ins Leben und die Art, wie du anderen wieder Hoffnung "
        "machst",
    "Steinbock": "deine Ausdauer und die stille Kraft, über Jahre etwas Bleibendes zu bauen",
    "Wassermann": "dein eigener Blick auf die Welt und der Mut, anders zu sein und andere darin zu "
        "bestärken",
    "Fische": "dein großes Mitgefühl und deine Fantasie, die Türen öffnet, wo andere nur Wände "
        "sehen",
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
    "Mars": "Mars ist dein Antrieb, deine Durchsetzungskraft und die Art, wie du für dich "
            "einstehst und etwas ins Rollen bringst.",
    "Jupiter": "Jupiter ist der Ort in dir, an dem du wächst, vertraust und das Leben größer "
               "denkst.",
    "Saturn": "Saturn ist dein innerer Lehrmeister, der zeigt, wo du reifst, Verantwortung "
              "übernimmst und etwas Tragfähiges baust.",
    "Uranus": "Uranus ist der Teil von dir, der frei sein will, der aufbricht und alles neu "
              "denkt.",
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
HOUSE_TITLE = {
    1: "Das Selbst", 2: "Werte & Sicherheit", 3: "Denken & Austausch", 4: "Wurzeln & Zuhause",
    5: "Ausdruck & Freude", 6: "Alltag & Gesundheit", 7: "Beziehung", 8: "Tiefe & Wandlung",
    9: "Sinn & Weite", 10: "Berufung", 11: "Gemeinschaft & Zukunft", 12: "Rückzug & Verborgenes",
}
ANGLE_HOUSE = {"AC": 1, "DC": 7, "MC": 10, "IC": 4}
_ANGLES = ("AC", "DC", "MC", "IC")

# Planet in Haus: was der Planet ganz konkret in diesem Lebensfeld bewirkt (aus deinem
# Nachschlagewerk, in Du-Form, ohne Gedankenstriche).
PLANET_HOUSE = {
    "Sonne": {
        1: "du verwirklichst dich am stärksten über deine Persönlichkeit und deine pure Präsenz",
        2: "deine Identität hängt eng an deinen Werten, deinem Besitz und deinem Selbstwert",
        3: "du findest zu dir selbst über Reden, Lernen und deine wache Neugier",
        4: "deine tiefste Kraft liegt im Privaten, in Familie und in deinen Wurzeln",
        5: "du blühst richtig auf, wenn du kreativ bist, liebst, spielst und dich zeigst",
        6: "du findest Sinn in deiner Arbeit, im Dienst an anderen und in einem gesunden Alltag",
        7: "du findest dich selbst vor allem in und durch deine engen Beziehungen",
        8: "du wächst über Krisen, über Tiefe und über echte, radikale Wandlung",
        9: "du bist im Kern sinnsuchend, gern unterwegs und teilst dein Wissen von Herzen gern",
        10: "deine Berufung und deine öffentliche Rolle prägen, wer du bist",
        11: "du gehst auf in Gruppen, in Idealen und in großen Zukunftsvisionen",
        12: "deine Kraft wirkt im Stillen, im Rückzug und im Spirituellen",
    },
    "Mond": {
        1: "deine Gefühle sind sichtbar, und deine Stimmung prägt dein ganzes Auftreten",
        2: "du brauchst ein Stück materielle Sicherheit, um dich emotional geborgen zu fühlen",
        3: "du denkst und sprichst gefühlvoll und bist deinen Geschwistern oft besonders nah",
        4: "du hast eine tiefe Familienbindung, dein Zuhause ist dein sicherer Anker",
        5: "du drückst deine Gefühle kreativ aus und hast ein inniges Verhältnis zu Kindern",
        6: "deine Stimmung hängt stark an deinem Alltag, und du sorgst von Herzen gern für andere",
        7: "du sehnst dich nach emotionaler Nähe und Anlehnung in der Partnerschaft",
        8: "du fühlst tief und intensiv und sehnst dich nach echter Verschmelzung",
        9: "du hast ein feines Gespür für Sinn und Ferne, deine Weltsicht ist emotional",
        10: "du zeigst deine Fürsorge auch öffentlich, oft in helfenden oder nährenden Rollen",
        11: "deine emotionale Heimat findest du in Freundschaften und in Gemeinschaft",
        12: "deine Gefühlstiefe ist verborgen, du brauchst Rückzug und bist sehr empathisch",
    },
    "Merkur": {
        1: "du wirkst wach, kommunikativ und neugierig, das Reden liegt dir",
        2: "du denkst viel über Werte und Geld nach und verdienst gern über das Wort",
        3: "dein Denken ist besonders stark, Lernen, Schreiben und Sprechen sind dein Element",
        4: "deine Gedanken kreisen um Herkunft und Familie, du redest gern in vertrauter Runde",
        5: "du denkst kreativ und spielst mit Sprache, Worte sind für dich Kunst",
        6: "du denkst analytisch im Alltag und hast ein feines Auge fürs Detail",
        7: "Austausch ist deine Beziehungsbasis, du redest dich mit anderen zueinander",
        8: "dein Geist forscht gern in der Tiefe, dich ziehen Tabus und Psychologie an",
        9: "du denkst philosophisch und liebst Sprachen, Sinn und das große Ganze",
        10: "dein Denken zielt auf Beruf und Wirkung, Kommunikation ist dein Feld",
        11: "du tauschst Ideen in Gruppen aus und denkst in Netzwerken",
        12: "dein Denken ist leise und intuitiv, du führst viele innere Dialoge",
    },
    "Venus": {
        1: "du hast Charme und eine ganz natürliche Anziehungskraft",
        2: "du kannst tief genießen, liebst Schönes und hast klare eigene Werte",
        3: "du kommunizierst liebenswürdig und findest fast immer die schönen Worte",
        4: "du brauchst Harmonie und Schönheit in deinem Zuhause",
        5: "Romantik, Kunst und Flirt gehören ganz selbstverständlich zu deiner Lebensfreude",
        6: "du brauchst ein harmonisches Arbeitsklima und Freude im Alltag",
        7: "Partnerschaft ist dir ein hoher Wert, echte, verbindliche Beziehungen bedeuten dir viel",
        8: "du liebst tief und intensiv und fühlst dich zum Verborgenen hingezogen",
        9: "dich zieht das Fremde und die Ferne an, auch in der Liebe",
        10: "du bist im Beruf beliebt, oft in ästhetischen oder gestalterischen Feldern",
        11: "deine Liebe ist freundschaftlich, du magst harmonische Netzwerke",
        12: "deine Liebe ist zart und still, oft hingebungsvoll und im Verborgenen",
    },
    "Mars": {
        1: "du bist durchsetzungsstark, energiegeladen und manchmal ein wenig ungeduldig",
        2: "du kämpfst für deine Werte und dein Geld und packst am liebsten selbst an",
        3: "du hast eine scharfe Zunge, denkst schnell und diskutierst mit Leidenschaft",
        4: "in deiner Familie steckt viel Energie, manchmal auch Reibung und Konflikt",
        5: "du drückst dich leidenschaftlich aus, sportlich, mutig und kreativ",
        6: "du bist arbeitsam und tatkräftig, achte nur gut auf die Gefahr von Überlastung",
        7: "deine Beziehungen sind lebendig und dürfen auch mal Funken schlagen",
        8: "du hast eine starke Willenskraft und meisterst Krisen und Machtthemen",
        9: "du kämpfst für deine Überzeugungen und liebst das Abenteuer",
        10: "dein Ehrgeiz treibt deine Karriere, du gehst gern ganz vorne voran",
        11: "du bist aktiv in Gruppen und kämpfst mit Feuer für deine Ideale",
        12: "deine Kraft wirkt oft im Verborgenen, gestaute Wut ist dein Lernthema",
    },
    "Jupiter": {
        1: "du strahlst Optimismus und Großzügigkeit aus, fast wie ein Glückskind",
        2: "du hast ein feines Gespür für Fülle und für finanzielles Wachstum",
        3: "du lernst mit echter Freude und hast viele Interessen",
        4: "dein Zuhause ist großzügig und gastfreundlich, dort liegt dein Glück",
        5: "du erlebst Fülle in Kreativität, in der Liebe und mit Kindern",
        6: "du findest Sinn in deiner Arbeit und brauchst gute Bedingungen, um zu wachsen",
        7: "du wächst durch Partnerschaft, oft an der Seite großzügiger Menschen",
        8: "du gewinnst durch geteilte Ressourcen und durch tiefes inneres Wachstum",
        9: "Reisen, Weisheit und Lehren sind ein großes Geschenk in deinem Leben",
        10: "beruflicher Erfolg und öffentliches Ansehen fallen dir eher leicht zu",
        11: "förderliche Netzwerke und große Visionen tragen dich weit",
        12: "in dir wohnt eine Art innerer Schutzengel und ein tiefes spirituelles Wachstum",
    },
    "Saturn": {
        1: "du wirkst ernst und diszipliniert, dein Selbstvertrauen blüht erst spät richtig auf",
        2: "Sorgen um Sicherheit sind dein Lernfeld, du baust langsam, aber dauerhaft auf",
        3: "du denkst gründlich, und aus frühen Lernhürden wird mit der Zeit echte Expertise",
        4: "in deiner Herkunft lag früh viel auf deinen Schultern, du kommst innerlich eher spät an",
        5: "dein Selbstausdruck ist erst gehemmt, deine Kreativität reift zu etwas Ernstem",
        6: "du bist sehr pflichtbewusst und brauchst Disziplin für deine Gesundheit",
        7: "deine Bindungen sind ernst und dauerhaft, Beziehung ist für dich ein Reifeweg",
        8: "du lernst die Meisterschaft im Loslassen und im Umgang mit Kontrolle",
        9: "deine Sinnsuche ist skeptisch, dein Weltbild festigt sich durch Prüfungen",
        10: "deine Berufung reift durch Ausdauer, im Alter wächst deine natürliche Autorität",
        11: "du hast wenige, aber sehr loyale Freunde und trägst Verantwortung in Gruppen",
        12: "du löst verborgene Ängste und übst dich in einer stillen, spirituellen Disziplin",
    },
    "Uranus": {
        1: "du trittst unkonventionell auf und liebst deine Freiheit über alles",
        2: "deine Finanzen schwanken, und du gehst beim Verdienen gern eigene Wege",
        3: "du hast Geistesblitze und denkst sprunghaft, schnell und modern",
        4: "deine Herkunft war unruhig oder auf ihre Art unkonventionell",
        5: "deine Kreativität ist eigenwillig, und deine Lieben sind oft ungewöhnlich",
        6: "du brauchst Freiheit im Job und magst es, wenn nicht alles nach Plan läuft",
        7: "du liebst Freiheit in Beziehungen, Begegnungen kommen oft ganz plötzlich",
        8: "du erlebst plötzliche Wandlungen und gehst frei und offen mit Tabus um",
        9: "dein Weltbild ist rebellisch, und Erkenntnisse treffen dich blitzartig",
        10: "dein Karriereweg ist ungewöhnlich, Berufungen dürfen sich bei dir wandeln",
        11: "du bringst echten Reformgeist mit und hast ganz besondere Freundeskreise",
        12: "in dir reifen plötzliche innere Durchbrüche und eine verborgene Genialität",
    },
    "Neptun": {
        1: "du hast eine feine, schwer greifbare und sehr empathische Ausstrahlung",
        2: "beim Thema Geld ist manches unscharf, und deine Werte sind idealistisch",
        3: "du denkst poetisch und fantasievoll, pass nur auf die Zerstreuung auf",
        4: "dein Familienbild ist idealisiert, und dein Zuhause ist ein sehr sensibler Ort",
        5: "du schöpfst künstlerische Inspiration und neigst dazu, die Liebe zu verklären",
        6: "du bist feinfühlig im Alltag und fühlst dich zu helfenden Rollen hingezogen",
        7: "du idealisierst Partner leicht und sehnst dich nach der einen Seelenverbindung",
        8: "in dir liegt eine mystische Tiefe und eine feine, mediale Begabung",
        9: "deine Sinnsuche ist spirituell, dich ziehen Mystik und Ferne an",
        10: "deine Berufung ist künstlerisch, sozial oder spirituell gefärbt",
        11: "du träumst gemeinsam mit anderen von einer besseren, sanfteren Welt",
        12: "in dir wohnt eine tiefe Spiritualität und eine reiche, weite Traumwelt",
    },
    "Pluto": {
        1: "du hast eine intensive, fast magnetische Präsenz",
        2: "du wandelst deinen Selbstwert und findest Kraft über deine Ressourcen",
        3: "dein Denken ist durchdringend, und deine Worte haben echtes Gewicht",
        4: "in deiner Herkunft wirkten starke Kräfte, deine Familie hat viel Umbruch erlebt",
        5: "dein Selbstausdruck ist intensiv, und deine Lieben verwandeln dich",
        6: "du wandelst zwanghafte Alltagsmuster und regenerierst dich aus der Tiefe",
        7: "deine Beziehungen sind intensiv, Macht und Kontrolle sind ein echtes Thema",
        8: "du meisterst Krisen mit großer Tiefe und Erneuerungskraft",
        9: "dein Weltbild wandelt sich radikal, du suchst kompromisslos die Wahrheit",
        10: "deine öffentliche Rolle ist machtvoll, du steigst oft gerade durch Krisen auf",
        11: "du hast Einfluss in Gruppen und erlebst tief verwandelnde Freundschaften",
        12: "in dir wirken die tiefsten unbewussten Wandlungskräfte",
    },
}


def _pos_desc(key, sign, house, seen=None):
    if key == "Chiron":
        full = CHIRON_SIGN.get(sign, "")
        first = full.split(". ", 1)[0].strip()
        if first:
            return (first + ". Ausführlich liest du das im Reiter Deutung, im Kapitel über "
                    "deinen Chiron.")
        return ("Chiron zeigt, wo du verletzlich bist, und genau dort liegt deine besondere Kraft, "
                "andere zu heilen.")
    intro = PLANET_INTRO.get(key, "")
    ph = PLANET_HOUSE.get(key, {}).get(house)
    kurz = HOUSE_SHORT.get(house, "diesen Bereich")
    base = intro + " " + sign_voice(sign, seen, intro + " " + (ph or ""))

    def _frame(frames):
        """Rahmensatz durchtauschen. Ein gemeinsamer Zähler über alle Häuser, damit
        er von Karte zu Karte wechselt und nicht nur bei zwei Planeten im selben Haus."""
        if seen is None:
            return frames[0]
        i = seen.get("_haus", 0)
        seen["_haus"] = i + 1
        return frames[i % len(frames)]

    def _echo(label, *texte):
        """Taucht ein Begriff aus dem Hausnamen im Text daneben schon auf?"""
        rest = set()
        for t in texte:
            rest |= {w.lower() for w in re.findall(r"[A-Za-zÄÖÜäöüß]{4,}", t or "")}
        return bool(_schlagworte(label) & rest)

    if ph:
        if _echo(kurz, base, ph):
            frames = [
                f" Bei dir steht das im {house}. Haus. Ganz konkret zeigt es sich so: {ph}.",
                f" Sein Ort ist bei dir das {house}. Haus. Bei dir heißt das: {ph}.",
                f" Angesiedelt ist das bei dir im {house}. Haus. Ganz praktisch sieht das so "
                f"aus: {ph}.",
                f" In deinem Chart fällt das ins {house}. Haus. Und zwar so: {ph}.",
                f" Das Ganze wirkt bei dir im {house}. Haus. Konkret heißt das: {ph}.",
            ]
        else:
            frames = [
                f" Bei dir steht das im {house}. Haus, deinem Lebensfeld für {kurz}. Ganz konkret "
                f"zeigt es sich so: {ph}.",
                f" Sein Ort ist bei dir das {house}. Haus. Da geht es um {kurz}. Bei dir heißt "
                f"das: {ph}.",
                f" Angesiedelt ist das bei dir im {house}. Haus, wo es um {kurz} geht. Ganz "
                f"praktisch sieht das so aus: {ph}.",
                f" In deinem Chart fällt das ins {house}. Haus, dein Lebensfeld für {kurz}. Und "
                f"zwar so: {ph}.",
                f" Das Ganze wirkt bei dir im {house}. Haus, dem Lebensfeld für {kurz}. Konkret "
                f"heißt das: {ph}.",
            ]
        base += _frame(frames)
    elif house and key not in _ANGLES:
        if _echo(kurz, base):
            frames = [
                f" In deinem Leben spielt sich das vor allem im {house}. Haus ab.",
                f" Der Ort dafür ist bei dir das {house}. Haus.",
                f" Wirksam wird das bei dir vor allem im {house}. Haus.",
                f" In deinem Chart fällt das ins {house}. Haus.",
                f" Das Ganze wirkt bei dir im {house}. Haus.",
            ]
        else:
            frames = [
                f" In deinem Leben spielt sich das vor allem im {house}. Haus ab, deinem "
                f"Lebensfeld für {kurz}.",
                f" Der Ort dafür ist bei dir das {house}. Haus, dein Lebensfeld für {kurz}.",
                f" Wirksam wird das vor allem dort, wo es um {kurz} geht, in deinem {house}. Haus.",
                f" In deinem Chart fällt das ins {house}. Haus, dein Lebensfeld für {kurz}.",
                f" Das Ganze wirkt bei dir im {house}. Haus, dem Lebensfeld für {kurz}.",
            ]
        base += _frame(frames)
    return base.strip()


def profile_name(profile):
    return PROFILE_NAMES.get(profile, " / ".join(
        PROFILE_LINES.get(int(x), "") for x in profile.split("/")))


# ── Geschlecht: männlich (m), weiblich (f) oder geschlechtsneutral (n) ──
# Bei n (divers / keine Angabe) nutzen wir bewusst neutrale, gegenderte Formen.
TYPE_GENDER = {
    "Generator": {"m": "Generator", "f": "Generatorin"},
    "Manifestierender Generator": {"m": "Manifestierender Generator",
                                   "f": "Manifestierende Generatorin"},
    "Manifestor": {"m": "Manifestor", "f": "Manifestorin"},
    "Projektor": {"m": "Projektor", "f": "Projektorin"},
    "Reflektor": {"m": "Reflektor", "f": "Reflektorin"},
}
# Intuitions-Archetyp je Element. n ist die neutrale Adjektivform ohne Artikel.
INTU_ARCHETYPE = {
    "Wasser": {"m": "Der Tiefenfühlende", "f": "Die Tiefenfühlende", "n": "Tiefenfühlend"},
    "Feuer": {"m": "Der Impulsstarke", "f": "Die Impulsstarke", "n": "Impulsstark"},
    "Erde": {"m": "Der Spürsinnige", "f": "Die Spürsinnige", "n": "Spürsinnig"},
    "Luft": {"m": "Der Klarsehende", "f": "Die Klarsehende", "n": "Klarsehend"},
}


def norm_gender(g):
    """Frontend-Wert auf m / f / n normalisieren (n = neutral/gegendert)."""
    g = (g or "").strip().lower()
    if g in ("m", "mann", "männlich", "maennlich", "male", "herr"):
        return "m"
    if g in ("f", "w", "frau", "weiblich", "female", "dame"):
        return "f"
    return "n"  # divers, keine Angabe, unbekannt


def type_display(hd_type, gender):
    """Human-Design-Typ als Wort passend zum Geschlecht."""
    v = TYPE_GENDER.get(hd_type)
    if not v:
        return hd_type
    if gender == "f":
        return v["f"]
    return v["m"]  # m und n nutzen die im HD gebräuchliche, neutrale Grundform


def intu_archetype(element, gender):
    """Intuitions-Archetyp als Wort passend zum Geschlecht."""
    v = INTU_ARCHETYPE.get(element, {})
    return v.get(gender) or v.get("f") or ""


INTUITION = {
    "Wasser": {
        "archetype": "Die Tiefenfühlende",
        "tagline": "Gefühls-Intuition",
        "oneliner": "Du fühlst, was andere nicht aussprechen.",
        "text": ("Deine Intuition spricht durch das Gefühl. Dein Mond steht in {moon}, einem "
                 "Wasserzeichen, und das macht dich zu einem feinen Empfänger für Stimmungen, die "
                 "andere gar nicht bemerken. Du spürst, wie es einem Menschen wirklich geht, oft "
                 "schon, bevor ein Wort fällt. Dein Körper reagiert auf eine Situation, lange bevor "
                 "dein Kopf sie versteht, und genau dieses feine Bauchgefühl ist bei dir besonders "
                 "wach. Deine Gabe ist tiefe Empathie. Deine Aufgabe ist, dich liebevoll "
                 "abzugrenzen, damit du in den Gefühlen der anderen nicht untergehst."),
        "tools": [
            "Frage dich bei starken Gefühlen zuerst: Ist das gerade meins, oder habe ich es von "
            "jemandem aufgenommen?",
            "Wasser klärt dich. Eine Dusche, ein Bad oder ein Spaziergang am Wasser spült fremde "
            "Stimmungen wieder ab.",
            "Führ ein kleines Ahnungs-Tagebuch. Wenn du deine Eingebungen aufschreibst, siehst du "
            "mit der Zeit, wie oft du richtig lagst, und dein Vertrauen wächst.",
        ],
    },
    "Feuer": {
        "archetype": "Die Impulsstarke",
        "tagline": "Instinkt-Intuition",
        "oneliner": "Du weißt es schon im ersten Funken.",
        "text": ("Deine Intuition kommt als Impuls, blitzschnell und mitten aus dem Bauch. Dein "
                 "Mond steht in {moon}, einem Feuerzeichen, und das gibt dir einen Instinkt, der "
                 "sofort weiß, wohin es geht. Du erkennst eine Gelegenheit im ersten Moment und "
                 "bist schon in Bewegung, während andere noch überlegen. Dieses Wissen ist da, "
                 "bevor du es begründen kannst, wie ein Funke, der schneller ist als jeder Gedanke. "
                 "Deine Gabe sind Mut und Timing. Deine Aufgabe ist, einmal kurz durchzuatmen, "
                 "bevor der Funke dich schon losreißt."),
        "tools": [
            "Vertraue deinem allerersten Impuls, bevor der Zweifel kommt. Deine erste Antwort ist "
            "meistens die wahre.",
            "Bring deinen Körper in Bewegung. Beim Gehen, Tanzen oder Sport kommen deine besten "
            "Eingebungen wie von selbst.",
            "Setze deine Energie in eine kleine, sofortige Handlung um, statt sie zu zerdenken.",
        ],
    },
    "Erde": {
        "archetype": "Die Spürsinnige",
        "tagline": "Körper-Intuition",
        "oneliner": "Dein Körper weiß es zuerst.",
        "text": ("Deine Intuition wohnt im Körper. Dein Mond steht in {moon}, einem Erdzeichen, und "
                 "das erdet dein Gespür in etwas ganz Handfestes. Du fühlst im Bauch, in den "
                 "Schultern, im ganzen Körper, ob etwas stimmt. Dein Körper sendet dir feine "
                 "Signale und markiert eine Sache als richtig oder gefährlich, noch bevor der "
                 "Verstand nachzieht. Bei dir ist dieser Kompass besonders verlässlich. Deine Gabe "
                 "ist ein sicherer Instinkt für das Echte. Deine Aufgabe ist, wieder in den Körper "
                 "zu hören, wenn der Kopf zu laut wird."),
        "tools": [
            "Mach einen kurzen Body-Scan. Gehe in Gedanken durch deinen Körper und spüre, wo sich "
            "eine Entscheidung eng oder weit anfühlt.",
            "Gehe in die Natur, am liebsten barfuß. Der Boden unter dir bringt dich zurück zu deinem "
            "Bauchgefühl.",
            "Schlaf über wichtige Fragen. Am Morgen weiß dein Körper die Antwort oft schon.",
        ],
    },
    "Luft": {
        "archetype": "Die Klarsehende",
        "tagline": "Muster-Intuition",
        "oneliner": "Du erkennst das Muster im Nu.",
        "text": ("Deine Intuition zeigt sich als plötzliche Klarheit. Dein Mond steht in {moon}, "
                 "einem Luftzeichen, und das lässt dich Muster und Zusammenhänge erkennen, lange "
                 "bevor du sie erklären kannst. Du liest Menschen, Stimmungen und Ideen in "
                 "Sekunden, ein Blick, ein Tonfall, und du weißt Bescheid. Dein Gespür zieht viele "
                 "feine Signale auf einmal zu einem klaren Bild zusammen. Es ist wandelbar und "
                 "spiegelt oft deine Stimmung. Deine wichtigste Lektion ist, dir selbst zu "
                 "vertrauen, auch wenn sich dein Gespür von Tag zu Tag verändert."),
        "tools": [
            "Sprich deine Gedanken laut aus oder schreib sie auf. Im Formulieren wird deine Ahnung "
            "auf einmal klar.",
            "Vertraue dem ersten Bild, das auftaucht, wenn du an eine Person oder eine Situation "
            "denkst.",
            "Gönn deinem Kopf Stille. In der Ruhe zwischen den Gedanken taucht die Eingebung auf.",
        ],
    },
}


WATER_SIGNS = {"Krebs", "Skorpion", "Fische"}
WATER_HOUSES = {4, 8, 12}

DEPTH_SUMMARY = {
    "außergewöhnlich stark angelegt":
        "In deinem Chart ist die intuitive Ader außergewöhnlich stark angelegt. Gleich mehrere "
        "Kräfte spielen hier zusammen. Ob sich das für dich gerade laut anfühlt oder leise: Diese "
        "Anlage gehört zu deinen größten Talenten.",
    "stark angelegt":
        "In deinem Chart ist die intuitive Ader stark angelegt. Sie kann ein sehr verlässlicher "
        "Begleiter für dich werden, sobald du ihr Raum und Ruhe gibst. Und falls sie sich im Moment "
        "eher still anfühlt: Sie ist nicht weg, sie ist nur lange überhört worden.",
    "deutlich angelegt":
        "In deinem Chart ist eine deutliche intuitive Anlage zu sehen. Am klarsten meldet sie sich "
        "in ruhigen Momenten, wenn der Alltag einmal leiser wird. Ob du sie im Alltag schon "
        "wahrnimmst, ist eine zweite Frage, denn dieser Zugang lässt sich verlernen und genauso "
        "wieder aufwecken.",
    "fein und leise angelegt":
        "Deine intuitive Anlage ist eher fein und leise. Sie spricht in stillen Augenblicken, und "
        "je öfter du ihr zuhörst, desto deutlicher wird sie.",
}


def _aspect_name(a, b):
    d = abs(((a - b + 180) % 360) - 180)
    for ang, orb, name in [(0, 6, "Konjunktion"), (180, 6, "Opposition"),
                           (120, 5, "Trigon"), (90, 5, "Quadrat"), (60, 4, "Sextil")]:
        if abs(d - ang) <= orb:
            return name
    return None


def build_intuition(chart):
    nat = chart.get("natal", {})
    moon = nat.get("Mond")
    if not moon:
        return None
    moon_sign = moon["sign"]
    element = SIGN_ELEMENT.get(moon_sign, "Wasser")
    base = INTUITION[element]
    order = ["Feuer", "Erde", "Luft", "Wasser"]
    g = chart.get("gender", "n")

    result = {
        "key": element,
        "archetype": intu_archetype(element, g),
        "tagline": base["tagline"],
        "moon_sign": moon_sign,
        "text": base["text"].format(moon=moon_sign),
        "tools": base["tools"],
        "all": [{"key": e, "archetype": intu_archetype(e, g),
                 "tagline": INTUITION[e]["tagline"], "oneliner": INTUITION[e]["oneliner"]}
                for e in order],
        "note": "Der Intuitionstyp ist kein klassisches Human-Design- oder Astrologie-System, "
                "sondern ein eigenes Deutungsbild von Intuition mit Herz. Er entsteht aus deinem "
                "Mond, aus Neptun und Pluto und aus deinen Wasserhäusern 4, 8 und 12. Das sind die "
                "Stellen im Chart, die in der Astrologie traditionell mit Gefühl, Tiefe und "
                "Wahrnehmung verbunden sind. Verstehe ihn als ein Bild zur Selbstreflexion, das dich "
                "an deine eigene innere Stimme erinnert.",
        "depth": None,
    }

    # Tiefenschicht nur mit Geburtszeit (dann sind die Häuser verlässlich)
    if not chart.get("time_known"):
        return result

    mh = moon.get("house")
    nep, plu = nat.get("Neptun"), nat.get("Pluto")
    mn = _aspect_name(moon["lon"], nep["lon"]) if nep and "lon" in nep else None
    mp = _aspect_name(moon["lon"], plu["lon"]) if plu and "lon" in plu else None

    score = 0
    if moon_sign in WATER_SIGNS:
        score += 2
    if mh in WATER_HOUSES:
        score += 1
    if nep and (nep.get("house") in WATER_HOUSES or nep["sign"] in WATER_SIGNS):
        score += 1
    if plu and (plu.get("house") in WATER_HOUSES or plu["sign"] in WATER_SIGNS):
        score += 1
    for b in ["Sonne", "Merkur", "Venus", "Mars"]:
        p = nat.get(b)
        if p and p.get("house") in WATER_HOUSES:
            score += 1
    if mn in ("Konjunktion", "Opposition", "Trigon", "Quadrat"):
        score += 1
    if mp in ("Konjunktion", "Opposition", "Trigon", "Quadrat"):
        score += 1

    facets = []
    if mh:
        facets.append({"title": "Wo deine Intuition am wachsten ist",
            "text": f"Dein Mond steht in deinem {mh}. Lebensfeld. Hier geht es um "
                    f"{HOUSE_MEANING.get(mh, 'diesen Bereich')}. Genau in diesen Themen ist deine "
                    f"Intuition am wachsten, und deinem Gefühl darfst du hier besonders trauen."})
    if (nep and (nep.get("house") == 12 or nep["sign"] == "Fische")) or \
            mn in ("Konjunktion", "Opposition", "Trigon"):
        facets.append({"title": "Deine feinfühlige, fast mediale Ader",
            "text": "Neptun berührt deine Intuition und macht deine Antennen besonders fein. Du "
                    "nimmst Stimmungen und das Unausgesprochene oft so klar wahr, dass du gar nicht "
                    "sagen kannst, woher du es weißt. Diese Durchlässigkeit ist ein Geschenk. Erde "
                    "dich immer wieder, damit du in fremden Wellen nicht verschwimmst."})
    if (plu and (plu.get("house") == 8 or plu["sign"] == "Skorpion")) or \
            mp in ("Konjunktion", "Opposition", "Trigon"):
        facets.append({"title": "Dein Tiefenblick",
            "text": "Pluto gibt deiner Wahrnehmung Tiefe. Du spürst, was unter der Oberfläche "
                    "liegt, die wahren Beweggründe und das, was ein Mensch verbirgt. Andere fühlen "
                    "sich von dir gesehen bis auf den Grund. Gehe behutsam mit dieser starken Gabe "
                    "um."})
    occ = {}
    for b in ["Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn",
              "Neptun", "Pluto", "Chiron"]:
        p = nat.get(b)
        if p and p.get("house") in WATER_HOUSES:
            occ.setdefault(p["house"], True)
    if 4 in occ:
        facets.append({"title": "Deine familiäre Antenne",
            "text": "In deinem vierten Lebensfeld, bei Zuhause, Familie und Wurzeln, sammelt sich "
                    "viel Gespür. Du fühlst die Stimmung in deinem Zuhause, oft bevor ein Wort "
                    "fällt, und trägst ein feines Erbe an emotionaler Wahrnehmung in dir."})
    if 8 in occ:
        facets.append({"title": "Dein Gespür fürs Verborgene",
            "text": "In deinem achten Lebensfeld, bei Tiefe, Wandlung und echter Verbundenheit, "
                    "liegt eine besondere Sensibilität. Du spürst Umbrüche im Voraus und ahnst, was "
                    "Menschen im Innersten bewegt."})
    if 12 in occ:
        facets.append({"title": "Deine Traum- und Rückzugs-Wahrnehmung",
            "text": "In deinem zwölften Lebensfeld, bei Rückzug, Träumen und dem Verborgenen, "
                    "öffnet sich dir eine leisere Wirklichkeit. Deine Träume und deine stillen "
                    "Stunden für dich allein sind echte Quellen der Erkenntnis."})

    level = ("außergewöhnlich stark angelegt" if score >= 6 else
             "stark angelegt" if score >= 4 else
             "deutlich angelegt" if score >= 2 else "fein und leise angelegt")

    # Anlage und Zugang sind zweierlei. Wer wenig Wasser im Chart hat, kommt an das
    # eigene Fühlen oft schwerer heran, auch wenn die Intuition stark angelegt ist.
    # Ohne diesen Satz widerspricht sich der Bauplan an zwei Stellen.
    caveat = ""
    _w, _w_is_weakest = _water_share(chart)
    if _w <= 1 or (_w <= 2 and _w_is_weakest):
        _wie = ("kaum vertreten" if _w <= 1 else "von allen vier Elementen am schwächsten vertreten")
        caveat = (
            f"Eine Sache gehört ehrlich dazu: Wasser, das Element des Fühlens, ist in deinem Chart "
            f"{_wie}. Die Anlage ist also da, aber der Draht zu deinem eigenen Fühlen ist bei dir "
            f"nicht von allein gebahnt. Gut möglich, dass er als Kind offener war als heute. Er "
            f"lässt sich zurückholen: mit Stille, mit Zeit und damit, dass du deinen ersten "
            f"Eindruck ernst nimmst, bevor dein Kopf ihn überstimmt.")

    result["depth"] = {
        "score": min(score, 8), "max": 8, "level": level,
        "summary": DEPTH_SUMMARY[level], "caveat": caveat, "facets": facets,
    }
    return result


# ── Numerologie (deterministisch aus Geburtsdatum und Vorname, 0 € KI) ──
# Pythagoräische Buchstabenwerte; deutsche Umlaute werden vorher aufgelöst.
_NUM_LETTERS = {
    "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9,
    "j": 1, "k": 2, "l": 3, "m": 4, "n": 5, "o": 6, "p": 7, "q": 8, "r": 9,
    "s": 1, "t": 2, "u": 3, "v": 4, "w": 5, "x": 6, "y": 7, "z": 8,
}
_NUM_TRANS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
                            "á": "a", "à": "a", "â": "a", "é": "e", "è": "e",
                            "ê": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ç": "c"})


def _num_reduce(n, keep_master=True):
    """Quersumme, bis eine Ziffer bleibt. Meisterzahlen 11, 22, 33 bleiben stehen."""
    while n > 9 and not (keep_master and n in (11, 22, 33)):
        n = sum(int(d) for d in str(n))
    return n


LIFEPATH = {
    1: {"title": "Der Weg der Eigenständigkeit", "tagline": "Führung und Mut",
        "keyword": "Anfangen und führen",
        "text": "Deine Eins ist die Zahl des Anfangs. Du bist hier, um deinen eigenen Weg zu "
                "gehen, nicht den, den andere für dich vorgesehen haben. In dir steckt eine "
                "natürliche Führungskraft und der Mut, Dinge als Erste anzupacken. Vielleicht "
                "hast du früh gelernt, dich anzupassen, und tief gespürt, dass dich das klein "
                "macht. Deine Kraft wächst genau dann, wenn du zu deiner eigenen Richtung stehst, "
                "auch wenn du dafür ein Stück allein vorangehst. Du bist gebaut, um selbst zu "
                "entscheiden."},
    2: {"title": "Der Weg der Verbindung", "tagline": "Feingefühl und Nähe",
        "keyword": "Verbinden und spüren",
        "text": "Deine Zwei ist die Zahl der Verbindung. Du spürst feiner als die meisten, was "
                "zwischen Menschen mitschwingt, und hast die Gabe, Brücken zu bauen und "
                "auszugleichen. An der Seite anderer blühst du am meisten auf. Vielleicht stellst "
                "du dich dabei oft zu weit hinten an und vergisst dich selbst. Deine Aufgabe ist, "
                "deine Sanftheit als Stärke zu sehen und trotzdem für dich einzustehen. Echte "
                "Harmonie schließt dich immer mit ein."},
    3: {"title": "Der Weg des Ausdrucks", "tagline": "Freude und Kreativität",
        "keyword": "Ausdrücken und leuchten",
        "text": "Deine Drei ist die Zahl des Ausdrucks. In dir wohnt eine Leichtigkeit und eine "
                "schöpferische Freude, die andere ansteckt. Du bringst Farbe dorthin, wo es grau "
                "wird, mit Worten, mit Kreativität, mit deinem Lachen. Vielleicht hast du gelernt, "
                "dich kleiner zu machen, um bloß nicht zu viel zu sein. Aber deine Freude ist ein "
                "Geschenk, kein Zuviel. Wenn du dich zeigst, geht es dir am besten."},
    4: {"title": "Der Weg der Beständigkeit", "tagline": "Struktur und Halt",
        "keyword": "Bauen und halten",
        "text": "Deine Vier ist die Zahl des festen Bodens. Du baust mit Geduld etwas auf, das "
                "bleibt, und andere verlassen sich auf dein Wort. Struktur, Ordnung und "
                "Verlässlichkeit sind deine natürliche Sprache. Vielleicht bist du manchmal zu "
                "streng mit dir und lässt wenig Leichtigkeit zu. Erlaube dir, auch mal loszulassen. "
                "Dein Halt ist echt, du musst ihn dir nicht ständig hart erkämpfen."},
    5: {"title": "Der Weg der Freiheit", "tagline": "Wandel und Weite",
        "keyword": "Erleben und wandeln",
        "text": "Deine Fünf ist die Zahl der Freiheit. Du brauchst Bewegung, Abwechslung und Weite, "
                "um dich lebendig zu fühlen, und lernst am meisten, indem du das Leben selbst "
                "erfährst. Enge macht dich unruhig. Vielleicht hast du dich manchmal als zu "
                "sprunghaft erlebt oder so genannt bekommen. Aber dein Hunger nach Erfahrung ist "
                "kein Makel, er ist dein Motor. Gib dir die Freiheit, die du brauchst, und du "
                "findest von ganz allein zur Ruhe."},
    6: {"title": "Der Weg der Fürsorge", "tagline": "Liebe und Verantwortung",
        "keyword": "Sorgen und lieben",
        "text": "Deine Sechs ist die Zahl der Liebe und der Fürsorge. Du sorgst von Herzen für die "
                "Menschen um dich und hast ein feines Gespür für das, was ein Zuhause warm macht. "
                "Verantwortung trägst du gern. Vielleicht kümmerst du dich so sehr um andere, dass "
                "du dabei zuletzt kommst. Deine Lektion ist, dieselbe Fürsorge auch dir selbst zu "
                "schenken. Du darfst genährt werden, nicht immer nur nähren."},
    7: {"title": "Der Weg der Tiefe", "tagline": "Wahrheit und Weisheit",
        "keyword": "Ergründen und verstehen",
        "text": "Deine Sieben ist die Zahl der Tiefe. Du gibst dich nicht mit der Oberfläche "
                "zufrieden, du willst verstehen, was wirklich dahintersteckt. Stille, Rückzug und "
                "die großen Fragen gehören zu dir. Vielleicht fühlst du dich manchmal einsam oder "
                "anders als die anderen. Aber deine Tiefe ist eine Gabe, kein Abstand. Vertraue "
                "deiner inneren Weisheit, sie führt dich sicherer als jeder laute Rat von außen."},
    8: {"title": "Der Weg der Kraft", "tagline": "Fülle und Wirkung",
        "keyword": "Gestalten und tragen",
        "text": "Deine Acht ist die Zahl der Kraft und der Fülle. In dir steckt die Fähigkeit, im "
                "Außen zu wirken, Verantwortung zu tragen und etwas Großes auf die Beine zu "
                "stellen. Du denkst in Möglichkeiten, nicht in Grenzen. Vielleicht hast du ein "
                "zwiespältiges Verhältnis zu Erfolg und Geld, mal Sehnsucht, mal Scheu. Deine "
                "Aufgabe ist, deine Kraft anzunehmen, ohne dich über sie zu definieren. Du darfst "
                "wirken und trotzdem weich bleiben."},
    9: {"title": "Der Weg des Mitgefühls", "tagline": "Weite und Vollendung",
        "keyword": "Geben und loslassen",
        "text": "Deine Neun ist die Zahl des großen Herzens. Du fühlst über dich hinaus, mit den "
                "Menschen und mit der Welt, und trägst eine natürliche Weisheit und Großzügigkeit "
                "in dir. Oft gibst du, ohne zu rechnen. Vielleicht fällt dir das Loslassen schwer, "
                "das Festhalten an dem, was längst vorbei ist. Deine Lektion ist, zu vertrauen, "
                "dass im Loslassen Platz für Neues entsteht. Dein Mitgefühl ist dein Geschenk an "
                "diese Welt."},
    11: {"title": "Die Meisterzahl der Eingebung", "tagline": "Licht und Intuition",
         "keyword": "Erspüren und inspirieren",
         "text": "Deine Elf ist eine Meisterzahl, eine der seltensten und feinsten Schwingungen der "
                 "Numerologie. Sie trägt alles von der Zwei, aber in einer viel höheren, hellwachen "
                 "Form. Du bist wie ein Kanal für Eingebung und Inspiration und spürst Dinge, für "
                 "die andere keine Worte haben. Das kann sich groß anfühlen, manchmal fast zu viel. "
                 "Vielleicht schwankst du zwischen tiefer Klarheit und leisem Selbstzweifel. Wenn du "
                 "deiner inneren Stimme vertraust, wirst du für andere zu einem Licht."},
    22: {"title": "Die Meisterzahl der Verwirklichung", "tagline": "Vision und Aufbau",
         "keyword": "Träumen und bauen",
         "text": "Deine Zweiundzwanzig ist die Meisterzahl des Baumeisters, eine der kraftvollsten "
                 "überhaupt. Sie verbindet die große Vision der Elf mit dem festen Boden der Vier. "
                 "Du hast die seltene Gabe, große Träume nicht nur zu denken, sondern sie wirklich "
                 "in die Welt zu bringen. Vielleicht spürst du den Druck dieser Größe und traust "
                 "dich manchmal nicht so recht heran. Gehe in kleinen, festen Schritten. Was in dir "
                 "angelegt ist, darf echt werden."},
    33: {"title": "Die Meisterzahl der Liebe", "tagline": "Heilung und Hingabe",
         "keyword": "Heilen und dienen",
         "text": "Deine Dreiunddreißig ist die höchste und seltenste Meisterzahl, die Zahl des "
                 "liebenden Herzens. Sie trägt eine tiefe Berufung, für andere da zu sein und mit "
                 "reiner Wärme zu heilen. In dir wohnt ein großer Wunsch, die Welt ein Stück "
                 "sanfter zu machen. Diese Berufung darf dich nur nicht auslaugen. Deine Aufgabe "
                 "ist, dieselbe Liebe, die du so großzügig verschenkst, auch dir selbst zu "
                 "schenken."},
}

# Namenszahl (Ausdruckszahl): wie du deinen Lebensweg nach außen lebst und wirkst.
# Aus den Buchstaben deines Vornamens. Jeweils: was es heißt + was du damit anfängst.
NAMENUM = {
    1: "Deine Namenszahl 1 gibt deinem Auftreten etwas Führendes und Eigenständiges. Nach außen "
       "wirkst du selbstbewusst, klar und tatkräftig, wie jemand, der gern vorangeht. Lebe das, "
       "indem du Initiative ergreifst und zu deiner eigenen Richtung stehst, statt dich anzupassen. "
       "Achte nur darauf, andere mitzunehmen, statt sie zu überrollen.",
    2: "Deine Namenszahl 2 verleiht deinem Ausdruck etwas Sanftes und Verbindendes. Du wirkst "
       "nahbar, feinfühlig und ausgleichend, Menschen öffnen sich dir schnell. Deine Stärke ist es, "
       "zu vermitteln und Brücken zu bauen. Denke nur daran, dabei auch dich selbst zu zeigen und "
       "deine eigene Meinung einzubringen.",
    3: "Deine Namenszahl 3 bringt Leichtigkeit und Ausdruckskraft in dein Auftreten. Du wirkst "
       "lebendig, humorvoll und inspirierend und findest oft genau die richtigen Worte. Lebe das, "
       "indem du dich kreativ zeigst und dich mitteilst. Bleibe nur dran, auch wenn dich zwischendurch "
       "der Selbstzweifel packt.",
    4: "Deine Namenszahl 4 gibt dir eine geerdete, verlässliche Ausstrahlung. Andere erleben dich "
       "als jemanden, auf den man bauen kann, ruhig und beständig. Deinen Weg gehst du gründlich und "
       "Schritt für Schritt. Erlaube dir zwischendurch bewusst auch Leichtigkeit und Pausen.",
    5: "Deine Namenszahl 5 macht deinen Ausdruck lebendig und wandelbar. Du wirkst neugierig, offen "
       "und beweglich und bringst frischen Wind, wohin du kommst. Deinen Weg gehst du über Erfahrung "
       "und Abwechslung. Achte nur darauf, dich nicht zu verzetteln und dranzubleiben, wenn es zählt.",
    6: "Deine Namenszahl 6 umgibt dich mit Wärme und Fürsorge. Menschen fühlen sich in deiner Nähe "
       "schnell geborgen und aufgehoben. Deinen Weg gehst du verantwortungsvoll und mit einem feinen "
       "Blick fürs Miteinander. Vergiss dabei nicht, dieselbe Fürsorge auch dir selbst zu schenken.",
    7: "Deine Namenszahl 7 gibt dir eine tiefe, leicht geheimnisvolle Ausstrahlung. Du wirkst "
       "nachdenklich, beobachtend und nicht sofort zu durchschauen. Deinen Weg gehst du reflektiert "
       "und mit dem Wunsch, die Dinge wirklich zu verstehen. Öffne dich ruhig auch mal, statt dich "
       "zurückzuziehen.",
    8: "Deine Namenszahl 8 verleiht dir Präsenz und Kraft. Du wirkst zielstrebig, souverän und "
       "stark, wie jemand, der etwas bewegen kann. Deinen Weg gehst du mit Ehrgeiz und Weitblick. "
       "Zeige dabei ruhig auch deine weichen, verletzlichen Seiten, das macht dich nur stärker.",
    9: "Deine Namenszahl 9 umgibt dich mit einer warmen, großherzigen Ausstrahlung. Du wirkst "
       "mitfühlend, weise und offen für das große Ganze. Deinen Weg gehst du mit dem Wunsch, etwas "
       "beizutragen. Achte nur darauf, dich nicht in der Fürsorge für andere zu verlieren.",
    11: "Deine Namenszahl 11 ist eine Meisterzahl und gibt deinem Ausdruck etwas Hellwaches, fast "
        "Elektrisierendes. Du wirkst inspirierend und feinfühlig, oft spürst du mehr, als du in Worte "
        "fasst. Das ist ein Geschenk, kann aber auch viel sein. Erde dich bewusst, dann kann diese "
        "hohe Schwingung wirklich durch dich wirken.",
    22: "Deine Namenszahl 22 ist eine Meisterzahl und verbindet Vision mit Bodenhaftung. Nach außen "
        "wirkst du wie jemand, der Großes denken und es zugleich umsetzen kann. Das ist eine seltene "
        "Kraft. Gehe sie in ruhigen, festen Schritten an, statt dich unter deinen eigenen Anspruch zu "
        "setzen.",
    33: "Deine Namenszahl 33 ist die seltenste Meisterzahl und umgibt dich mit einer heilenden, "
        "liebevollen Ausstrahlung. Menschen spüren deine Wärme und dein echtes Interesse. Deine Gabe "
        "ist, andere durch dein Vorbild zu stärken. Denke nur daran, genug Kraft auch für dich selbst "
        "zu behalten.",
}

# Stärken und Aufgabe je Lebenszahl (aus der Numerologie-Recherche, für mehr Tiefe im Reiter).
LIFEPATH_MORE = {
    1: {"strengths": "Tatkraft, Mut, Pioniergeist, Führungsstärke und Originalität",
        "growth": "Führung mit echtem Zuhören zu verbinden und Nähe zuzulassen, statt alles allein zu stemmen"},
    2: {"strengths": "Empathie, Diplomatie, Feingefühl, Geduld und Teamgeist",
        "growth": "deine eigenen Bedürfnisse genauso ernst zu nehmen wie die der anderen, statt in der Harmonie zu verschwinden"},
    3: {"strengths": "Kreativität, Ausdruckskraft, Optimismus, Charme und Inspiration",
        "growth": "deine Selbstzweifel zu überwinden und deine Kreativität mutig und dranbleibend zu leben"},
    4: {"strengths": "Disziplin, Verlässlichkeit, Organisationstalent, Ausdauer und Bodenständigkeit",
        "growth": "Flexibilität und Leichtigkeit zuzulassen, ohne deinen inneren Halt zu verlieren"},
    5: {"strengths": "Vielseitigkeit, Anpassungsfähigkeit, Neugier und Mut zur Veränderung",
        "growth": "deine Freiheit mit Verantwortung und innerer Stabilität zu verbinden"},
    6: {"strengths": "Verantwortungsgefühl, Mitgefühl, Gerechtigkeitssinn und Sinn für Schönheit",
        "growth": "Fürsorge für andere und Fürsorge für dich selbst in eine gesunde Balance zu bringen"},
    7: {"strengths": "Tiefgang, ein klarer analytischer Geist, Intuition und spirituelles Gespür",
        "growth": "wieder Vertrauen zu fassen und deine Erkenntnisse zu teilen, statt dich zu isolieren"},
    8: {"strengths": "Durchsetzungskraft, strategisches Denken, Ausdauer und Ehrgeiz",
        "growth": "Kraft und Erfolg mit Fairness und innerer Ruhe zu verbinden und Verletzlichkeit zuzulassen"},
    9: {"strengths": "Mitgefühl, Weitblick, Großzügigkeit und Idealismus",
        "growth": "deinen Idealismus zu erden und auch für dich selbst zu sorgen, statt dich zu verausgaben"},
    11: {"strengths": "eine starke Intuition, visionäre Kraft, Inspiration und ein feines Gespür für Zusammenhänge",
         "growth": "dich zu erden, damit die hohe Schwingung dich trägt statt überflutet, und deinen Selbstzweifel zu besänftigen"},
    22: {"strengths": "ein großes Umsetzungsvermögen, Weitblick mit Bodenhaftung und echte Aufbaukraft",
         "growth": "in kleinen, festen Schritten zu gehen und dich nicht an deinem eigenen Anspruch zu verbrennen"},
    33: {"strengths": "heilende Wärme, tiefes Mitgefühl, eine Lehrgabe und humanitäre Kraft",
         "growth": "klare Grenzen zu setzen und dich selbst zu nähren, statt dich für andere aufzugeben"},
}

# "Gut zu wissen": echte, faszinierende Symbolik/Fakten zur Zahl (Know-how, keine Vermutung).
LIFEPATH_FACT = {
    1: "Die Eins ist der Ursprung aller Zahlen, das Symbol für Einheit und den allerersten Anfang. "
       "In fast allen Kulturen steht sie für das Eine, das Ganze, den ersten Funken.",
    2: "Die Zwei ist die Zahl der Polarität und des Gleichgewichts: Tag und Nacht, Yin und Yang, Ich "
       "und Du. Erst durch sie entsteht überhaupt Beziehung.",
    3: "Die Drei gilt seit der Antike als Zahl der Harmonie und Vollständigkeit: Anfang, Mitte, Ende; "
       "Körper, Geist, Seele; die Stabilität des Dreiecks. Nicht umsonst heißt es: Aller guten Dinge "
       "sind drei.",
    4: "Die Vier ordnet die Welt: vier Himmelsrichtungen, vier Elemente, vier Jahreszeiten. Sie ist "
       "das Symbol für Stabilität und für alles Feste, Greifbare.",
    5: "Die Fünf ist die Zahl des Menschen (fünf Finger, fünf Sinne) und der Bewegung. Im Pentagramm "
       "gilt sie seit jeher als Zeichen für Lebendigkeit.",
    6: "Die Sechs galt schon bei den alten Griechen als vollkommene Zahl, weil ihre Teiler 1, 2 und 3 "
       "zusammen wieder 6 ergeben. Sie steht für Harmonie und Ebenmaß, wie in der sechseckigen "
       "Bienenwabe.",
    7: "Die Sieben gilt in vielen Kulturen als heilig: sieben Wochentage, sieben Chakren, sieben "
       "Farben des Regenbogens, sieben Weltwunder. Sie ist die Zahl der Suche und des Geheimnisses.",
    8: "Legt man die Acht auf die Seite, wird sie zum Zeichen der Unendlichkeit. Sie steht für "
       "Kreislauf und Fülle, für den Ausgleich von materieller und geistiger Welt, und gilt in Asien "
       "als große Glückszahl.",
    9: "Die Neun ist die letzte einstellige Zahl, das Symbol für Vollendung und Abschluss. Und sie "
       "hat einen verblüffenden Trick: Multiplizierst du sie mit irgendeiner Zahl, ergibt die "
       "Quersumme des Ergebnisses immer wieder 9.",
    11: "Die Elf ist die erste Meisterzahl, ein Tor aus zwei Einsen, das für einen direkten Draht zur "
        "Intuition steht. Man kennt sie als Zahl der Eingebung und des Erwachens.",
    22: "Die Zweiundzwanzig verbindet die Vision der Elf mit dem festen Boden der Vier. Man nennt sie "
        "den Baumeister, weil sie große Ideen in echte, greifbare Form bringen kann.",
    33: "Die Dreiunddreißig ist die seltenste Meisterzahl, die Zahl des Lehrers. Sie trägt Mitgefühl "
        "und Hingabe und taucht in vielen spirituellen Traditionen als Zahl der Meisterschaft auf.",
}

_NUM_WORD = {1: "eins", 2: "zwei", 3: "drei", 4: "vier", 5: "fünf", 6: "sechs",
             7: "sieben", 8: "acht", 9: "neun", 11: "elf", 22: "zweiundzwanzig",
             33: "dreiunddreißig"}
# Kurzlabel fürs Zahlen-Raster (sauberer Nominativ, kein Genitiv-Rest)
LIFEPATH_SHORT = {1: "Eigenständigkeit", 2: "Verbindung", 3: "Ausdruck", 4: "Beständigkeit",
                  5: "Freiheit", 6: "Fürsorge", 7: "Tiefe", 8: "Kraft", 9: "Mitgefühl"}

# Persönliches Jahr: das Motto des aktuellen Kalenderjahres (wandert jährlich weiter, 1 bis 9).
PERSONAL_YEAR = {
    1: {"theme": "Neuanfang", "text": "Ein Jahr des Neuanfangs. Ein frischer Zyklus beginnt, und "
        "was du jetzt anstößt, trägt weit. Sei mutig, gehe den ersten Schritt und setze die Samen "
        "für die nächsten neun Jahre."},
    2: {"theme": "Geduld und Nähe", "text": "Ein Jahr der Geduld und der Beziehungen. Vieles reift "
        "leise im Hintergrund, auch wenn nach außen wenig passiert. Pflege deine Verbindungen, "
        "höre hin und dräng nichts. Zusammenarbeit trägt dich jetzt weiter als der Alleingang."},
    3: {"theme": "Ausdruck und Freude", "text": "Ein Jahr des Ausdrucks und der Lebensfreude. Zeige "
        "dich, sei kreativ und lass wieder Leichtigkeit herein. Dein Herz will nach außen, also "
        "gönn dir Begegnungen, Farbe und alles, was dich zum Leuchten bringt."},
    4: {"theme": "Aufbau", "text": "Ein Jahr des Aufbaus. Jetzt zählen Fleiß, Struktur und ein "
        "langer Atem. Was du dieses Jahr solide baust, trägt dich über Jahre. Kümmere dich um die "
        "Fundamente, auch wenn es unspektakulär wirkt."},
    5: {"theme": "Veränderung", "text": "Ein Jahr der Veränderung und der Freiheit. Rechne mit "
        "Bewegung, neuen Chancen und der einen oder anderen Überraschung. Bleibe flexibel und offen, "
        "klammere dich nicht ans Alte. Dieses Jahr will, dass du das Leben spürst."},
    6: {"theme": "Verantwortung und Liebe", "text": "Ein Jahr der Verantwortung und der Liebe. "
        "Familie, Zuhause und die Menschen, die dir wichtig sind, rücken in den Mittelpunkt. Du "
        "gibst viel in diesem Jahr, also vergiss dabei nicht, auch für dich selbst zu sorgen."},
    7: {"theme": "Einkehr", "text": "Ein Jahr der Einkehr. Ziehe dich bewusst ein Stück zurück, "
        "reflektiere und gehe in die Tiefe. Nicht im lauten Außen, sondern in der Stille liegt "
        "dieses Jahr dein Wachstum. Vertraue deiner inneren Stimme mehr als je zuvor."},
    8: {"theme": "Ernte und Kraft", "text": "Ein Jahr der Ernte und der Kraft. Jetzt darfst du im "
        "Außen wirken und einfahren, was du in den Jahren davor gesät hast. Traue dich, groß zu "
        "denken und Verantwortung zu übernehmen. Deine Arbeit zahlt sich aus."},
    9: {"theme": "Loslassen", "text": "Ein Jahr des Loslassens und des Abschließens. Ein ganzer "
        "Zyklus geht zu Ende. Räum auf, verabschiede, was seine Zeit hatte, und mach innerlich "
        "Platz. Alles, was du jetzt gehen lässt, schafft Raum für den Neuanfang im nächsten Jahr."},
}


def _name_number(name):
    s = (name or "").strip().lower().translate(_NUM_TRANS)
    vals = [_NUM_LETTERS[c] for c in s if c in _NUM_LETTERS]
    if not vals:
        return None
    return _num_reduce(sum(vals))


def build_numerology(chart):
    """Lebenszahl aus dem Geburtsdatum und persönliches Jahr. Rein arithmetisch."""
    bd = chart.get("birth_date")
    if not bd:
        return None
    y, m, d = bd["year"], bd["month"], bd["day"]
    # Kanonische Methode: ALLE Ziffern des Geburtsdatums einzeln addieren, dann
    # Schritt für Schritt quersummieren. Meisterzahlen 11/22/33 stoppen die Reduktion.
    digits = [int(c) for c in f"{d:02d}{m:02d}{y}"]
    raw = sum(digits)
    chain = [raw]
    n = raw
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(c) for c in str(n))
        chain.append(n)
    lp = chain[-1]
    info = LIFEPATH.get(lp) or LIFEPATH[_num_reduce(lp, keep_master=False)]
    more = LIFEPATH_MORE.get(lp) or LIFEPATH_MORE.get(_num_reduce(lp, keep_master=False), {})
    calc = (f"{d:02d}.{m:02d}.{y}  →  " + "+".join(str(x) for x in digits) + f" = {raw}"
            + "".join("  →  " + str(c) for c in chain[1:]))

    # Persönliches Jahr: Geburtstag + Geburtsmonat + aktuelles Kalenderjahr (1 bis 9)
    cy = date.today().year
    py = _num_reduce(_num_reduce(d, keep_master=False) + _num_reduce(m, keep_master=False)
                     + _num_reduce(sum(int(x) for x in str(cy)), keep_master=False),
                     keep_master=False)
    py_info = PERSONAL_YEAR.get(py, {})
    personal_year = {"year": cy, "number": py,
                     "theme": py_info.get("theme", ""), "text": py_info.get("text", "")}

    return {
        "lifepath": lp,
        "is_master": lp in (11, 22, 33),
        "title": info["title"],
        "tagline": info["tagline"],
        "keyword": info["keyword"],
        "text": info["text"],
        "strengths": more.get("strengths", ""),
        "growth": more.get("growth", ""),
        "fact": LIFEPATH_FACT.get(lp) or LIFEPATH_FACT.get(_num_reduce(lp, keep_master=False), ""),
        "calc": calc,
        "personal_year": personal_year,
        "all": [{"number": k, "short": LIFEPATH_SHORT[k], "keyword": LIFEPATH[k]["keyword"]}
                for k in range(1, 10)],
        "note": "Die Numerologie ist ein eigenes, altes Deutungssystem und kein Teil von Human "
                "Design oder Astrologie. Deine Lebenszahl entsteht aus deinem Geburtsdatum, dein "
                "persönliches Jahr aus Tag, Monat und dem laufenden Jahr. Verstehe beides als ein "
                "weiteres Bild zur Selbstreflexion, das dich an deine eigenen Themen erinnert.",
    }


def teaser(chart):
    """Der kostenlose Funke: ausführlich genug zum Neugierigmachen, ohne das volle Bild."""
    hd = chart["hd"]
    t = TYPE_INFO.get(hd["type"], {})
    sun = chart["natal"]["Sonne"]
    moon = chart["natal"]["Mond"]
    defined = hd.get("defined_centers", [])
    g = chart.get("gender", "n")
    _intu = build_intuition(chart)
    asc = chart.get("ascendant")

    # Konkreter Wiedererkennungs-Funke aus Sonne, Mond und Aszendent
    resonance = []
    if asc:
        resonance.append(("So wirkst du nach außen", SIGN_CORE.get(asc["sign"], "")))
    resonance.append(("Das brauchst du im Innersten", SIGN_CORE.get(moon["sign"], "")))
    resonance.append(("Darum geht es in deinem Kern", SIGN_CORE.get(sun["sign"], "")))
    resonance_hook = (f"Und immer wenn du dich verbiegst, um dazuzugehören, meldet sich "
                      f"{t.get('not_self', 'ein leises Unbehagen')} in dir. Genau an dieser Stelle "
                      "beginnt dein eigentlicher Weg zu dir selbst.")

    return {
        "type": type_display(hd["type"], g),
        "type_short": t.get("short", ""),
        "resonance": resonance,
        "resonance_hook": resonance_hook,
        "intuition_tag": _intu["tagline"] if _intu else "",
        "intuition_type": _intu["archetype"] if _intu else "",
        "sun_sym": sun.get("sym", ""),
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
            "Dein vollständiges Geburtshoroskop mit allen Planeten, exakt auf die Bogenminute",
            "Dein Aszendent, Deszendent, MC und IC, also wie du wirkst, was du anziehst und wohin dein Weg zeigt",
            "Jeder Planet in Zeichen und Haus, konkret gedeutet für dein Leben",
            "Deine Elemente-Balance und dein persönlicher Lebensschwerpunkt",
            "Dein Human-Design-Typ, deine innere Autorität und dein Profil im Klartext",
            "Deine definierten und offenen Zentren, wo du Kraft schöpfst und wo du dich verlierst",
            "Dein Entscheidungsweg, deine größte Stärke und deine größte Herausforderung, und wie du sie meisterst",
            "Deine Lebensaufgabe aus deiner Mondknoten-Achse und dein Chiron, deine Wunde und Heilkraft",
            "Dein Intuitionstyp, über welchen Kanal deine innere Führung zu dir spricht",
            "Deine Lebenszahl und dein persönliches Jahr aus der Numerologie, dein roter Faden in einer Zahl",
            "Konkrete Werkzeuge und Handlungsempfehlungen, ganz auf dich zugeschnitten",
        ],
    }


SIGN_CORE = {
    "Widder": "Mut, Initiative und der Drang, voranzugehen",
    "Stier": "Ruhe, Genuss und der Wunsch nach echter Sicherheit",
    "Zwillinge": "Neugier, Worte und eine wache geistige Beweglichkeit",
    "Krebs": "Gefühl, Fürsorge und das Bedürfnis nach Geborgenheit",
    "Löwe": "Herz, Ausdruck und der Wunsch, mit Wärme zu strahlen",
    "Jungfrau": "Klarheit, Hingabe und ein feiner Blick fürs Detail",
    "Waage": "Harmonie, Schönheit und das echte Miteinander",
    "Skorpion": "Tiefe, Leidenschaft und der Mut zur Wandlung",
    "Schütze": "Weite, Sinn und die Sehnsucht nach Freiheit",
    "Steinbock": "Struktur, Ausdauer und eine stille Verantwortung",
    "Wassermann": "Freiheit, eigene Ideen und der Blick nach vorn",
    "Fische": "Mitgefühl, Fantasie und eine tiefe Durchlässigkeit",
}
ELEMENT_STRONG = {
    "Feuer": "Begeisterung, Tatkraft und der Mut, Dinge einfach anzufangen",
    "Erde": "Bodenständigkeit, Ausdauer und ein sicheres Gespür fürs Praktische",
    "Luft": "Denken, Austausch und die Gabe, den Überblick zu behalten",
    "Wasser": "Fühlen, Tiefe und ein feines Gespür für Zwischentöne",
}
ELEMENT_WEAK = {
    "Feuer": "der spontane Antrieb fällt dir manchmal schwer. Du holst ihn dir am besten über "
             "Bewegung und den Mut zum ersten Schritt, auch wenn er klein ist",
    "Erde": "das Praktische und Beständige kostet dich mehr Kraft. Kleine, feste Routinen erden "
            "dich und geben dir Halt im Alltag",
    "Luft": "das sachliche Draufschauen aus Distanz fällt dir schwerer. Reden und Schreiben helfen "
            "dir, deine Gedanken zu ordnen",
    "Wasser": "an dein eigenes Fühlen heranzukommen ist nicht immer leicht. Nimm dir bewusst Zeit "
              "für Stille, für Nähe und für alles, was dein Herz wirklich berührt",
}
_ELEMENT_ADJ = {"Feuer": "lebendig und tatkräftig", "Erde": "geerdet und verlässlich",
                "Luft": "wach und verbindend", "Wasser": "tief und feinfühlig"}
_ASPECTS = [(0, 7, "Konjunktion"), (60, 5, "Sextil"), (90, 6, "Quadrat"),
            (120, 7, "Trigon"), (180, 7, "Opposition"), (150, 3, "Quinkunx")]
# "ein Konjunktion" war falsch: Konjunktion und Opposition sind feminin.
_ASPECT_ARTIKEL = {
    "Konjunktion": "eine", "Opposition": "eine",
    "Sextil": "ein", "Quadrat": "ein", "Trigon": "ein", "Quinkunx": "ein",
}
_ASPECT_QUAL = {
    "Konjunktion": "Diese beiden Kräfte verschmelzen in dir zu einer einzigen, sie sind fast untrennbar.",
    "Sextil": "Hier liegt ein leichtes Talent bereit, das du aktiv nutzen darfst.",
    "Trigon": "Das ist eine angeborene Begabung, die dir fast mühelos zufällt.",
    "Quadrat": "Das ist eine echte innere Reibung, und genau an ihr wächst du am meisten.",
    "Opposition": "Zwei Pole in dir, die nach Ausgleich suchen, oft spielst du sie über deine Beziehungen aus.",
    "Quinkunx": "Zwei fremde Kräfte, die ständig feine Justierung brauchen, bis sie zusammenfinden.",
}
# Zweite Fassung, damit bei zwei gleichen Aspekten nicht zweimal derselbe Satz steht.
_ASPECT_QUAL2 = {
    "Konjunktion": "Diese beiden Kräfte sitzen bei dir aufeinander und wirken fast wie eine.",
    "Sextil": "Eine Begabung, die bereitliegt und darauf wartet, dass du sie in die Hand nimmst.",
    "Trigon": "Das fällt dir so leicht, dass du es kaum für eine Leistung hältst.",
    "Quadrat": "Hier reibt es sich in dir, und genau diese Reibung bringt dich weiter.",
    "Opposition": "Zwei Enden in dir, die um Ausgleich ringen, oft sichtbar in deinen Beziehungen.",
    "Quinkunx": "Zwei Kräfte, die nicht recht zueinanderpassen und trotzdem miteinander "
                "auskommen müssen.",
}
_PLANETS10 = ["Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn",
              "Uranus", "Neptun", "Pluto"]


def _kern_synthese(se, me, ae):
    if se == me == ae:
        return (f"Und jetzt kommt das Besondere. Diese drei Kräfte ziehen bei dir alle an einem "
                f"Strang, alle im Element {se}. Das macht dich unverkennbar {_ELEMENT_ADJ.get(se, '')}. "
                f"Menschen spüren diese Klarheit sofort, und du wirkst wie aus einem Guss.")
    if se == me:
        return (f"Innen ziehen dein Wesen und dein Gefühl an einem Strang, beide im Element {se}. "
                f"Nach außen aber zeigst du eine andere Farbe. So bist du dir innerlich sicherer, als "
                f"du nach außen wirkst, und überraschst andere mit einer Seite, die sie nicht "
                f"erwartet hätten.")
    return (f"In dir wohnen mehrere Stimmen. {se} in deinem Kern, {me} in deinem Gefühl, {ae} in "
            f"deinem Auftreten. Das kann sich manchmal widersprüchlich anfühlen, so als wärst du "
            f"mehrere Menschen zugleich. In Wahrheit ist genau das dein Reichtum. Du kannst vieles "
            f"in dir verbinden, was bei anderen getrennt bleibt.")


def _kern_section(sun, moon, asc):
    se = SIGN_ELEMENT.get(sun["sign"], "")
    me = SIGN_ELEMENT.get(moon["sign"], "")
    ae = SIGN_ELEMENT.get(asc["sign"], "")
    body = (
        "Bevor wir in die Einzelteile gehen, hier das Bild, das sich aus deinen drei wichtigsten "
        "Punkten ergibt. Sonne, Mond und Aszendent sind das Herzstück von allem.\n\n"
        f"In deinem tiefsten Wesen bist du {sun['sign']}. In dir wirkt {SIGN_CORE.get(sun['sign'], '')}. "
        "Das ist die Kraft, die dich morgens trägt und die zeigt, wer du im Grunde bist.\n\n"
        f"Dein Gefühl, dein innerer Hafen, ist {moon['sign']}. Hier lebt {SIGN_CORE.get(moon['sign'], '')}. "
        "So fühlst du wirklich, und das brauchst du, um dich sicher und geborgen zu fühlen. Diese "
        "Seite zeigst du oft nur den Menschen, denen du vertraust.\n\n"
        f"Nach außen aber zeigst du dich als {asc['sign']}. Der erste Eindruck, den du hinterlässt, "
        f"trägt {SIGN_CORE.get(asc['sign'], '')}. Vielleicht ist das gar nicht das Erste, was du "
        "selbst an dir spürst, und trotzdem ist es das, was andere zuerst sehen.\n\n"
        + _kern_synthese(se, me, ae))
    return {
        "title": "Dein innerster Kern",
        "subtitle": "Sonne, Mond und Aszendent, das Herzstück deines Charts",
        "headline": f"{sun['sign']}-Sonne, {moon['sign']}-Mond, {asc['sign']}-Aszendent",
        "body": body,
        "takeaway": "Diese drei sind kein Widerspruch. Sie sind die drei Stimmen, aus denen dein "
                    "ganz eigener Klang entsteht.",
        "facts": [("Sonne", f"{sun['sym']} {sun['sign']} {sun['text']}"),
                  ("Mond", f"{moon['sym']} {moon['sign']} {moon['text']}"),
                  ("Aszendent", f"{asc['sym']} {asc['sign']} {asc['text']}")],
    }


def _element_counts(nat, asc, mc):
    """Zehn Planeten plus AC und MC nach Elementen sortiert."""
    counts = {"Feuer": 0, "Erde": 0, "Luft": 0, "Wasser": 0}
    for k in _PLANETS10:
        p = nat.get(k)
        if p:
            el = SIGN_ELEMENT.get(p["sign"])
            if el:
                counts[el] += 1
    for pt in (asc, mc):
        if pt:
            el = SIGN_ELEMENT.get(pt["sign"])
            if el:
                counts[el] += 1
    return counts


def _water_share(chart):
    """Wasseranteil und ob Wasser das schwächste Element ist.

    Grundlage für den ehrlichen Hinweis beim Intuitionstyp: Die Anlage kann stark
    sein, während der Zugang zum eigenen Fühlen trotzdem verschüttet ist.
    """
    counts = _element_counts(chart.get("natal", {}), chart.get("ascendant"), chart.get("mc"))
    w = counts["Wasser"]
    return w, w == min(counts.values())


def _element_section(nat, asc, mc):
    counts = _element_counts(nat, asc, mc)
    dom = max(counts, key=counts.get)
    low = min(counts, key=counts.get)
    lack = ("Das Element " + low + " fehlt in deinem Chart fast ganz. Das heißt: " + ELEMENT_WEAK[low]
            if counts[low] == 0 else
            "Am wenigsten ausgeprägt ist bei dir das Element " + low + ". Das heißt: " + ELEMENT_WEAK[low])
    body = (
        "Für dieses Bild werden alle deine zehn Planeten sowie dein Aszendent und dein MC nach den "
        "vier Elementen sortiert. So entsteht eine Gesamtverteilung, nicht das Bild eines einzelnen "
        "Punktes. Dein Deszendent taucht hier bewusst nicht auf, denn er liegt immer genau gegenüber "
        "deinem Aszendenten und würde dieselbe Achse nur ein zweites Mal zählen.\n\n"
        f"Am stärksten ist bei dir das Element {dom}. In dir wirkt vor allem {ELEMENT_STRONG[dom]}. "
        "Das ist deine natürliche Sprache, die Art, wie du am liebsten durchs Leben gehst und dich "
        "am lebendigsten fühlst.\n\n"
        + lack + ".\n\n"
        "So eine Verteilung ist kein Mangel. Sie zeigt nur, wo deine Gaben von ganz allein fließen "
        "und wo du dir bewusst ein wenig dazuholen darfst. Oft ziehen wir genau die Menschen an, "
        "die unser schwächstes Element stark leben. Achte einmal darauf, wen du dir ins Leben "
        "holst.")
    return {
        "title": "Deine Elemente-Balance",
        "subtitle": "Feuer, Erde, Luft und Wasser in deinem Chart",
        "headline": f"Deine Stärke liegt im Element {dom}",
        "body": body,
        "facts": [("Feuer", str(counts["Feuer"])), ("Erde", str(counts["Erde"])),
                  ("Luft", str(counts["Luft"])), ("Wasser", str(counts["Wasser"]))],
    }


def _stellium_section(nat):
    groups = {}
    for k in _PLANETS10:
        p = nat.get(k)
        if p:
            groups.setdefault(p["sign"], []).append(k)
    stelliums = [(s, ps) for s, ps in groups.items() if len(ps) >= 3]
    if not stelliums:
        return None
    s, ps = max(stelliums, key=lambda x: len(x[1]))
    liste = ", ".join(ps)
    body = (
        f"Etwas Seltenes fällt in deinem Chart sofort auf. In {s} stehen gleich mehrere deiner "
        f"Planeten dicht beieinander: {liste}. Man nennt so eine Häufung ein Stellium.\n\n"
        f"Das ist ein echter Lebensschwerpunkt. Ein großer Teil deiner Energie dreht sich um die "
        f"Themen von {s}: {SIGN_CORE.get(s, '')}. Ob du willst oder nicht, dieses Thema zieht sich "
        f"wie ein roter Faden durch dein ganzes Leben.\n\n"
        f"Hier liegt eine deiner größten Gaben. Und zugleich das Feld, in dem du am meisten lernst "
        f"und über dich hinauswächst. Menschen mit einem Stellium wirken auf diesem einen Gebiet "
        f"oft, als wären sie damit geboren. Wahrscheinlich kennst du das von dir.")
    return {
        "title": "Ein Lebensschwerpunkt",
        "subtitle": f"Dein {s}-Stellium, {len(ps)} Planeten in einem Zeichen",
        "headline": f"Geballte {s}-Kraft",
        "body": body,
        "facts": [(f"Stellium in {s}", liste)],
    }


def _aspects_section(nat):
    found = []
    for i in range(len(_PLANETS10)):
        for j in range(i + 1, len(_PLANETS10)):
            a, b = nat.get(_PLANETS10[i]), nat.get(_PLANETS10[j])
            if not (a and b and "lon" in a and "lon" in b):
                continue
            d = abs(((a["lon"] - b["lon"] + 180) % 360) - 180)
            for ang, orb, nm in _ASPECTS:
                if abs(d - ang) <= orb:
                    found.append((abs(d - ang), _PLANETS10[i], _PLANETS10[j], nm))
                    break
    if not found:
        return None
    found.sort(key=lambda x: x[0])
    # Die Themen sind selbst Wortgruppen mit "und" ("Gefühlswelt und innerer Hafen").
    # Deshalb braucht jede Fassung einen klaren Trenner und den Nominativ, sonst
    # entstehen und-Ketten oder falsche Fälle ("mit innerer Hafen").
    schluss = [
        "Zwei Themen sind bei dir eng miteinander verwoben: {a} auf der einen Seite, {b} auf "
        "der anderen.",
        "Zwei Felder gehören bei dir zusammen: einmal {a}, einmal {b}.",
        "Das eine Thema heißt {a}, das andere {b}. Bei dir laufen die beiden zusammen.",
        "Bei dir berühren sich zwei Themen: einerseits {a}, andererseits {b}.",
    ]
    genau = [", fast auf den Punkt genau.", ", und das fast gradgenau.",
             ", beinahe exakt.", ", ziemlich genau sogar."]
    lines = []
    gesehen = {}
    for i, (o, a, b, nm) in enumerate(found[:4]):
        art = _ASPECT_ARTIKEL.get(nm, "ein")
        wie = gesehen.get(nm, 0)
        gesehen[nm] = wie + 1
        qual = _ASPECT_QUAL[nm] if wie == 0 else _ASPECT_QUAL2.get(nm, _ASPECT_QUAL[nm])
        lines.append(
            f"Zwischen {a} und {b} liegt {art} {nm}{genau[i % len(genau)]} {qual} "
            + schluss[i % len(schluss)].format(a=meaning_phrase(a), b=meaning_phrase(b)))
    body = (
        "Deine Planeten stehen nicht für sich allein. Sie stehen in bestimmten Winkeln zueinander "
        "und führen so etwas wie Gespräche miteinander. Diese Aspekte gehören zu den "
        "persönlichsten Zügen deines ganzen Charts, kein anderer Mensch hat sie genau so.\n\n"
        + "\n\n".join(lines) +
        "\n\nManche dieser Verbindungen fühlen sich leicht an, andere fordern dich heraus. Beide "
        "gehören zu dir. Die leichten sind deine Geschenke. Die fordernden sind die Stellen, an "
        "denen du am meisten über dich hinauswächst.")
    return {
        "title": "Deine inneren Gespräche",
        "subtitle": "Die stärksten Aspekte in deinem Chart",
        "headline": "Wo sich deine Kräfte berühren",
        "body": body,
        "facts": [],
    }



def _intuition_deutung_section(it):
    body = (
        f"Auch dein Intuitionstyp gehört mitten in deinen Bauplan. Über deinen Mond in "
        f"{it['moon_sign']} spricht deine innere Führung als {it['tagline']} zu dir, immer auf "
        f"deine ganz eigene Art.\n\n"
        f"Wie sich das genau anfühlt und welche Werkzeuge zu dir passen, findest du ausführlich im "
        f"eigenen Reiter „Intuitionstyp“. Fürs große Ganze zählt hier vor allem eins: Diese leise "
        f"Stimme ist kein nettes Extra. Sie ist ein zweiter Kompass neben deiner inneren Autorität. "
        f"Wenn du ihr wieder traust, führt sie dich in vielen Momenten zuverlässiger als jeder "
        f"Verstand.")
    dp = it.get("depth")
    facts = [("Intuitionstyp", it["archetype"]), ("Mond", it["moon_sign"])]
    if dp:
        facts.append(("Ausprägung", dp["level"]))
    return {
        "title": "Dein Intuitionstyp",
        "subtitle": f"{it['archetype']}, {it['tagline']}",
        "headline": it["archetype"],
        "body": body,
        "facts": facts,
    }


def full_analysis(chart):
    """Die vollständige, liebevoll aufbereitete Analyse (nach der E-Mail)."""
    hd = chart["hd"]
    t = TYPE_INFO.get(hd["type"], {})
    name = chart.get("name") or "du"
    asc = chart.get("ascendant")
    g = chart.get("gender", "n")
    type_word = type_display(hd["type"], g)
    hd["type_display"] = type_word

    sections = []
    _sun = chart["natal"].get("Sonne")
    _moon = chart["natal"].get("Mond")
    if _sun and _moon and asc:
        sections.append(_kern_section(_sun, _moon, asc))
    sections.append({
        "title": "Dein Human-Design-Typ",
        "headline": type_word,
        "body": ("Bevor du irgendwas an dir ändern willst, darfst du erst mal verstehen, wie du gebaut "
                 "bist. Dein Typ ist die Grundmelodie deiner Energie. Er zeigt dir, wie du am "
                 "leichtesten durchs Leben gehst und wo du dich immer wieder verausgabst.\n\n"
                 + t.get("short", "") + "\n\nDu kennst bestimmt Menschen, denen vieles mühelos "
                 "gelingt. Und du fragst dich, warum es bei dir an manchen Stellen so viel "
                 "schwerer geht. Meistens ist der Grund ganz einfach. Du hast versucht, nach einer "
                 "Melodie zu leben, die gar nicht deine ist.\n\nWenn du deiner eigenen Art vertraust, "
                 "ändert sich etwas Leises, aber Tiefes. Das Leben fühlt sich weniger nach Widerstand "
                 "an. Es fängt an, dich zu tragen."),
        "takeaway": ("Das Wichtigste zuerst: Deine Strategie ist " + strat_phrase(t.get("strategy", ""))
                     + ". Vertraue ihr, dann fühlt sich das Leben weniger nach Kampf an."),
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
        "body": ("Deine innere Autorität ist vielleicht das Wichtigste über dich. Sie beantwortet eine "
                 "Frage, an der viele hängenbleiben. Wie treffe ich eine Entscheidung, die wirklich zu "
                 "mir passt?\n\n" + AUTHORITY_INFO.get(hd["authority"], "") + "\n\nErinnerst du dich an "
                 "eine Entscheidung, die auf dem Papier richtig war und sich trotzdem falsch angefühlt "
                 "hat? Dieses leise Ziehen im Bauch war keine Feigheit. Das war deine echte Führung. "
                 "Sie hat versucht, mit dir zu reden.\n\nDein Kopf ist ein guter Berater. Aber er "
                 "sollte nicht am Ende entscheiden. Wenn du dieser tieferen Stimme wieder traust, "
                 "hörst du auf, gegen dich selbst zu leben."),
        "takeaway": ("Merke dir das: Entscheide über deine " + auth_phrase(hd["authority"]) + ", nicht "
                     "über den Kopf. Dann lebst du nicht mehr gegen dich selbst."),
        "facts": [],
    })
    sections.append({
        "title": "Dein Profil",
        "headline": f"{hd['profile']}, {profile_name(hd['profile'])}",
        "body": ("Dein Profil beschreibt die Rolle, in der sich dein Weg entfaltet. Stelle es dir wie "
                 "ein Kostüm vor, das deine Seele für dieses Leben gewählt hat. Die erste Zahl lebst "
                 "du bewusst. Sie ist dir vertraut. Die zweite wirkt eher aus dem Verborgenen. Andere "
                 "sehen sie oft früher in dir als du selbst.\n\n" + PROFILE_DESC.get(hd["profile"], "")
                 + "\n\nVielleicht erkennst du dich in beiden Seiten wieder. Und du hast dich manchmal "
                 "gefragt, warum du so widersprüchlich sein kannst. Das ist kein Widerspruch. Das ist "
                 "dein Design. Wenn du beide Seiten in dir sein lässt, wirst du ganz."),
        "takeaway": ("Am Ende gilt: Du darfst beide Seiten deines Profils sein. Erst zusammen ergeben "
                     "sie dich ganz."),
        "facts": [("Definition", hd["definition"]),
                  ("Definierte Zentren", ", ".join(hd["defined_centers"]) or "keine")],
    })

    defined = hd.get("defined_centers", [])
    open_c = hd.get("open_centers", [])
    sections.append({
        "title": "Deine Zentren",
        "headline": f"{len(defined)} definiert, {len(open_c)} offen",
        "body": ("Stelle dir deine Zentren wie neun Räume in dir vor. Manche sind fest eingerichtet und "
                 "immer gleich. Andere stehen offen und füllen sich mit dem, was gerade um dich herum "
                 "ist.\n\nDeine definierten Zentren sind deine feste, verlässliche Energie. Hier bist "
                 "du dir treu. Hier kannst du dich auf dich verlassen. Andere spüren diese Ruhe an "
                 "dir.\n\nDeine offenen Zentren sind deine Lernräume. Hier nimmst du andere fein auf. "
                 "Hier bist du beweglich. Und genau hier entsteht der Druck, dich zu verbiegen, um "
                 "dazuzugehören. Vielleicht kennst du das Gefühl, in bestimmter Gesellschaft plötzlich "
                 "ein anderer Mensch zu sein. Das passiert genau in diesen offenen Räumen.\n\nWenn du "
                 "verstehst, welche Räume bei dir offen sind, ist das oft ein echter Befreiungsmoment. "
                 "Du merkst: Vieles, was du für dein Problem gehalten hast, war nie deins. Du hast es "
                 "nur aufgenommen."),
        "takeaway": ("Kurz gesagt: Deine definierten Zentren sind dein fester Halt, deine offenen "
                     "deine Lernräume. Vieles, was du für dein Problem hieltest, hast du nur "
                     "aufgenommen."),
        "facts": [("Definiert", ", ".join(defined) or "keine"),
                  ("Offen", ", ".join(open_c) or "keine")],
    })

    # ---- Kombi-Sektionen aus Human Design und Geburtshoroskop ----
    _natk = chart["natal"]
    sun_sign = _natk["Sonne"]["sign"] if _natk.get("Sonne") else ""
    strat = t.get("strategy", "")
    auth = hd["authority"]
    sig = t.get("signature", "")
    nots = t.get("not_self", "")
    dcs = hd["defined_centers"]
    ocs = hd["open_centers"]

    sections.append({
        "title": "Dein Entscheidungsweg",
        "subtitle": "Wie du Entscheidungen triffst, die halten",
        "headline": f"{strat}, danach auf deine {auth_phrase(auth)} hören",
        "body": ("Zwei Dinge zusammen ergeben deinen sichersten Weg zu jeder Entscheidung.\n\n"
                 f"Der erste Schritt ist deine Strategie: {strat_phrase(strat)}. So kommst du überhaupt "
                 "erst mit dem Richtigen in Berührung.\n\n"
                 f"Der zweite Schritt ist deine innere Autorität, deine {auth_phrase(auth)}. Sie sagt dir, "
                 "ob ein Ja auch wirklich deins ist.\n\n"
                 "Erinnerst du dich, wie oft du schnell aus dem Kopf entschieden und dich danach "
                 "gefragt hast, warum sich alles falsch anfühlt? In dieser Reihenfolge kann dir das "
                 "nicht mehr passieren. Erst in Berührung kommen, dann von innen prüfen, und du "
                 "triffst Entscheidungen, die du nicht mehr bereust."),
        "takeaway": f"Dein roter Faden: {strat}. Und dann ehrlich auf deine {auth_phrase(auth)} hören.",
        "facts": [("Strategie", strat), ("Autorität", auth)],
    })

    staerken_ext = ((" Und dein Geburtshoroskop legt noch etwas dazu: "
                     + SIGN_STRENGTH.get(sun_sign, "") + ".")
                    if sun_sign and SIGN_STRENGTH.get(sun_sign) else "")
    staerken_basis = ((" " + aufzaehlung(dcs) + (" sind bei dir definiert." if len(dcs) > 1
                       else " ist bei dir definiert.")
                       + " Hier kannst du dich immer auf dich verlassen, egal was um dich herum "
                       "passiert.") if dcs else " Deine Kraft liegt gerade darin, offen und "
                      "beweglich zu bleiben und andere fein zu spüren.")
    sections.append({
        "title": "Deine größten Stärken",
        "subtitle": "Kräfte, die schon lange in dir stecken",
        "headline": "Das kannst du, auch wenn du es für selbstverständlich hältst",
        "body": ("Oft sind die eigenen Stärken genau die Dinge, die einem so leicht fallen, dass man "
                 "sie gar nicht für besonders hält. Dabei sind das deine Geschenke.\n\n"
                 "Aus deinem Human Design: Deine Signatur im Flow ist " + amp_phrase(sig) + ". Immer wenn "
                 "du die in dir spürst, bist du genau richtig unterwegs." + staerken_ext + "\n\n"
                 "Deine feste Basis:" + staerken_basis),
        "takeaway": ("Vergiss das nie: Deine größten Gaben fühlen sich für dich selbstverständlich an. "
                     "Genau deshalb übersiehst du sie. Fang an, sie bewusst zu leben."),
        "facts": [("Sonne", sun_sign), ("Signatur", sig)],
    })

    heraus_open = ((" Dazu kommen deine offenen Zentren: " + aufzaehlung(ocs) + ". Die hast du oben schon "
                    "kennengelernt. Genau dort nimmst du fremden Druck am leichtesten für deinen "
                    "eigenen und erschöpfst dich, ohne zu wissen, warum.") if ocs else "")
    sections.append({
        "title": "Deine größte Herausforderung",
        "subtitle": "Und wie du sie meisterst",
        "headline": "Deine wunde Stelle, ehrlich benannt",
        "body": ("Jeder Mensch hat eine Stelle, an der es immer wieder schwer wird. Sie zu kennen, "
                 "nimmt ihr schon die halbe Macht.\n\n"
                 "Dein deutlichstes Warnsignal heißt " + amp_phrase(nots) + ". Immer wenn du das in dir spürst, "
                 "lebst du gerade nicht deine eigene Natur. Du lebst die Erwartungen anderer."
                 + heraus_open + "\n\n"
                 "Und wie du sie meisterst: Frage dich immer wieder ehrlich, ob ein Gefühl gerade "
                 "wirklich deins ist oder nur aufgenommen. Gehe raus aus Räumen und Gesprächen, die "
                 "dich leer machen. Und lass die Entscheidung von innen kommen, so wie du es bei "
                 "deiner Autorität schon gelesen hast. So findest du jedes Mal zu dir zurück."),
        "takeaway": "Dein Frühwarnsystem: Sobald sich " + amp_phrase(nots) + " meldet, halte "
                    "inne und komm zu deiner eigenen Natur zurück.",
        "facts": [("Nicht-Selbst-Thema", nots)],
    })

    nat = chart["natal"]
    intuition = build_intuition(chart)
    if asc:
        sections.append(_element_section(nat, asc, chart.get("mc")))
        _stell = _stellium_section(nat)
        if _stell:
            sections.append(_stell)
        _asp = _aspects_section(nat)
        if _asp:
            sections.append(_asp)
    if intuition:
        sections.append(_intuition_deutung_section(intuition))

    nk = nat.get("Nordknoten")
    sk = nat.get("Südknoten")
    axis = NODE_AXIS.get(nk["sign"], {}) if nk else {}
    if nk and axis:
        f = [("Nordknoten", f"{nk['sym']} {nk['sign']} {nk['text']}")]
        if nk.get("house"):
            f.append(("Haus", f"H{nk['house']}"))
        sections.append({
            "title": "Dein Higher Self",
            "subtitle": f"Nordknoten in {nk['sign']}, wohin du wächst",
            "headline": f"Dein Wachstum zeigt Richtung {nk['sign']}",
            "body": ("Dein Higher Self ist niemand, der du erst noch werden musst. Es ist die Version "
                     "von dir, die längst in dir steckt. Sie wartet nur darauf, gelebt zu werden.\n\n"
                     + axis.get("higher", "") + "\n\nVielleicht spürst du ab und zu eine leise "
                     "Sehnsucht in diese Richtung. Ein Ziehen zu einem Leben, das sich freier "
                     "anfühlt, echter, mehr nach dir. Meistens schiebst du es weg. Zu groß, zu "
                     "unvernünftig, vielleicht später.\n\nAber dieses Ziehen geht nie ganz weg, oder? "
                     "Das ist kein Zufall. Es ist der Teil in dir, der genau weiß, wozu du hier bist. "
                     "Jedes Mal, wenn du ihm folgst, auch nur einen kleinen Schritt, kommst du ein "
                     "Stück mehr nach Hause. Zu dir."),
            "takeaway": (f"Denke immer daran: Dein Wachstum zeigt Richtung {nk['sign']}. Jeder kleine "
                         "Schritt dorthin bringt dich mehr zu dir."),
            "facts": f,
        })
    if sk and axis:
        sections.append({
            "title": "Dein Lower Self",
            "subtitle": f"Südknoten in {sk['sign']}, dein vertrautes Muster",
            "headline": f"Deine Komfortzone liegt im Zeichen {sk['sign']}",
            "body": ("Dein Lower Self ist kein Feind. Es ist der Teil von dir, der sich am sichersten "
                     "anfühlt. Du kennst ihn schon lange, oft seit deiner Kindheit.\n\n"
                     + axis.get("lower", "") + "\n\nKennst du diese Momente, in denen du unter Druck "
                     "automatisch in ein altes Muster zurückfällst? Obwohl ein Teil von dir es besser "
                     "weiß? Manchmal liegst du abends wach und denkst: Warum mache ich das immer "
                     "wieder? Genau das ist gemeint.\n\nHör mir kurz zu. Du bist nicht kaputt. Du hast "
                     "als Kind einen Weg gefunden, dich sicher zu fühlen. Damals hat er dich "
                     "beschützt. Heute hält er dich klein. Das ist kein Versagen. Das ist ein alter "
                     "Schutz, der seine Zeit hatte.\n\nDu musst dich dafür nicht schämen. Du musst es "
                     "nur sehen. Ein Muster, das du klar erkennst, verliert seine heimliche Macht "
                     "über dich."),
            "takeaway": ("Sei sanft mit dir: Dein altes Muster ist kein Feind, sondern ein alter "
                         "Schutz. Erkenne ihn, dann verliert er seine heimliche Macht."),
            "facts": [("Südknoten", f"{sk['sym']} {sk['sign']} {sk['text']}")],
        })
    if nk and sk and axis:
        _lifebody = (
            f"Jetzt wird es ernst. Hier geht es nicht mehr um einzelne Bausteine, sondern um den "
            f"einen roten Faden, der sich durch dein ganzes Leben zieht. Deine beiden Seiten hast du "
            f"gerade kennengelernt: das vertraute {sk['sign']}-Muster, in das du unter Druck "
            f"zurückfällst, und dein {nk['sign']}-Wachstum, das eigentlich schon in dir wartet.\n\n"
            f"Und genau da liegt die Falle. Weil sich das Alte so sicher anfühlt, kehrst du immer "
            f"wieder dorthin zurück, auch wenn du längst spürst, dass es dich nicht mehr wachsen "
            f"lässt. Es hält dich klein und nennt es Schutz.\n\n"
            f"Jetzt kommt der Teil, den du nicht überspringen darfst, das Wie: Du wächst da nicht "
            f"rein, indem du darüber nachdenkst. Du wächst rein, indem du im echten Leben immer wieder "
            f"anders handelst als sonst. Als {hd['type']} gelingt dir das über den Entscheidungsweg, "
            f"den du weiter oben schon entdeckt hast. Erst dein eigener Impuls, dann die ruhige "
            f"Prüfung von innen. Und eben nicht der alte Reflex. Jedes Mal, wenn du "
            f"dich in einem dieser Momente für den ungewohnten, den {nk['sign']}-Weg entscheidest, "
            f"erfüllst du ein Stück deiner Lebensaufgabe. Es sind keine großen Gesten. Es sind die "
            f"kleinen, unbequemen Entscheidungen, in denen du dich für dich entscheidest.\n\n"
            f"Und ja, das wird sich manchmal falsch anfühlen. Fremd, riskant, fast wie Verrat am alten "
            f"Ich. Genau daran erkennst du, dass du auf dem richtigen Weg bist. Wachstum fühlt sich "
            f"nie sicher an. Es fühlt sich echt an.")
        sections.append({
            "title": "Deine Lebensaufgabe",
            "subtitle": f"Deine Mondknoten-Achse: {sk['sign']} zu {nk['sign']}",
            "headline": f"Von {sk['sign']} nach {nk['sign']}",
            "body": _lifebody,
            "takeaway": axis.get("task", ""),
            "tip": ("So gehst du deine Lebensaufgabe an", axis.get("task_tip", "")),
            "facts": [("Kommst du her von", f"{sk['sign']} {sk['text']}"),
                      ("Wächst du hin zu", f"{nk['sign']} {nk['text']}")],
        })

    chi = chart["natal"].get("Chiron")
    if chi:
        facts = [("Stellung", f"{chi['sym']} {chi['sign']} {chi['text']}")]
        if chi.get("house"):
            facts.append(("Haus", f"H{chi['house']}"))
        sections.append({
            "title": "Dein Chiron, Wunde und Heilung",
            "headline": f"Chiron in {chi['sign']} {chi['text']}",
            "body": (CHIRON_SIGN.get(chi["sign"], "Chiron zeigt die Stelle, an der du verletzlich "
                     "bist, und genau dort liegt deine besondere Kraft, andere zu heilen.")
                     + "\n\nDiese Wunde ist alt. Wahrscheinlich älter, als du denkst. Vielleicht warst "
                     "du noch ein Kind, als sie entstanden ist. Du hast früh gelernt, sie zu "
                     "verstecken. Also hast du gelächelt, funktioniert, dich zusammengerissen. Und "
                     "tief in dir blieb dieser eine wunde Punkt, den kaum jemand je gesehen hat.\n\n"
                     "Vielleicht spürst du ihn genau in diesem Moment, während du das hier liest. "
                     "Dieses Ziehen in der Brust. Das ist in Ordnung. Es heißt, dass diese Stelle "
                     "endlich gesehen wird. Von dir.\n\nUnd jetzt der Satz, den du dir vielleicht dein "
                     "ganzes Leben gewünscht hast: An dir ist nichts kaputt und war es nie. Diese "
                     "Wunde macht dich nicht schwächer. Sie macht dich weich. Weil du diesen Schmerz so gut kennst, "
                     "spürst du ihn bei anderen sofort. Du bist der Mensch, der einem anderen sagen "
                     "kann: Du bist genug. Und der es auch so meint. Du heilst andere durch genau "
                     "die Stelle, an der du selbst verletzt wurdest."),
            "takeaway": ("Wenn du nur einen Satz behältst: An dir ist nichts kaputt. Deine Wunde und "
                         "deine Gabe sind dieselbe Stelle."),
            "tip": ("So arbeitest du mit dieser Wunde", CHIRON_HEAL_TIP.get(chi["sign"], "")),
            "facts": facts,
        })

    if axis.get("tools"):
        tool_lines = "\n\n".join("• " + x for x in axis["tools"])
        sections.append({
            "title": "Deine Tools und Impulse",
            "subtitle": "Wie du gut mit dir und deiner Umwelt umgehst",
            "headline": "Kleine Schritte, große Wirkung",
            "body": ("Ein paar konkrete Impulse, wie du dein Higher Self stärkst und dein altes Muster "
                     "früh erkennst:\n\n" + tool_lines + "\n\nUnd im Umgang mit anderen bleibt dein "
                     "Kompass derselbe, den du bei deinem Entscheidungsweg entdeckt hast: erst spüren, "
                     "dann handeln. So bleibst du bei dir, auch wenn es um dich herum laut wird."),
            "facts": [],
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

    closing = (f"{name}, wenn du nur einen Satz aus all dem mitnimmst, dann diesen: Mit dir war nie "
               f"etwas falsch. Du hast dich nur lange an einen Ort angepasst, der nicht für dich "
               f"gebaut war. Kein Wunder, dass du müde bist. Du darfst deiner eigenen Art wieder "
               f"vertrauen. Lebe deine Strategie, {strat_phrase(t.get('strategy',''))}, und höre auf deine "
               f"{auth_phrase(hd['authority'])}. Immer wenn sich etwas von innen richtig anfühlt, gehe da "
               f"hin. Auch wenn dein Weg kurviger ist als der von anderen. Er ist deiner. Und er war "
               f"die ganze Zeit schon in dir. 🤍")

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

    _sign_seen = {}

    def _pos(key, label, p, house):
        return {
            "key": key, "label": label, "sym": p.get("sym_body", key) if key not in _ANGLES else key,
            "signSymbol": p["sym"], "sign": p["sign"], "deg": p["text"],
            "element": SIGN_ELEMENT.get(p["sign"], ""), "house": house,
            "house_pl": p.get("house_pl", house),
            "house_meaning": HOUSE_MEANING.get(house, "") if house else "",
            "meaning": PLANET_MEANING.get(key, ""),
            "desc": _pos_desc(key, p["sign"], house, _sign_seen),
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
    hd_centers = []
    for c in ["Kopf", "Ajna", "Kehle", "G", "Herz", "Milz", "Sakral",
              "Solarplexus", "Wurzel"]:
        info = CENTER_INFO.get(c, {})
        is_def = c in _defset
        hd_centers.append({
            "name": c,
            "defined": is_def,
            "meaning": CENTER_MEANING.get(c, ""),
            "desc": CENTER_DEEP.get(c, {}).get("def" if is_def else "open", ""),
            "theme": info.get("theme", ""),
            "detail": info.get("defined", "") if is_def else info.get("open", ""),
            "tip": info.get("tip", ""),
            "gift": info.get("gift", ""),
            "shadow": info.get("shadow", ""),
            "says": info.get("says_def", "") if is_def else info.get("says_open", ""),
            "use_def": CENTER_USE_DEF.get(c, ""),
        })

    houses = [{"nr": i, "title": HOUSE_TITLE[i], "meaning": HOUSE_MEANING.get(i, "")}
              for i in range(1, 13)]

    return {
        "name": name,
        "hd": hd,
        "sections": sections,
        "natal_rows": natal_rows,
        "positions": positions,
        "houses": houses,
        "hd_centers": hd_centers,
        "intuition": intuition,
        "numerology": build_numerology(chart),
        "ascendant": asc,
        "geo": geo,
        "closing": closing,
        "note": "Symbolische Deutung zur Selbstreflexion. Kein Ersatz für Beratung, keine Diagnose. "
                "Alle Positionen exakt berechnet (tropischer Tierkreis). Häuser in Ganzzeichen und "
                "Placidus angegeben; die ausführliche Deutung folgt den Ganzzeichen-Häusern.",
    }
