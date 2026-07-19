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
        "getan, was von dir erwartet wurde, und dich dabei selbst verloren. Frag dich bei jeder "
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

# Mondknoten-Achse (nach Nordknoten-Zeichen):
#   higher = Higher Self (Nordknoten, wohin du wächst)
#   lower  = Lower Self (Südknoten, dein vertrautes Rückfall-Muster)
#   task   = Lebensaufgabe in einem Satz
#   tools  = konkrete Impulse für den Alltag
NODE_AXIS = {
    "Widder": {
        "higher": "Du bist hier, um für dich selbst einzustehen. Um deine eigenen Impulse ernst zu nehmen und den Schritt nach vorn zu wagen, auch wenn ihn dir niemand abnimmt. Es geht darum, endlich du zu sein, laut und lebendig, statt immer die nette, angepasste Version.",
        "lower": "Dein vertrautes Muster ist Anpassung. Du willst gefallen, glättest jeden Konflikt und schaust zuerst, was die anderen brauchen. Wahrscheinlich hast du früh gelernt, dass du geliebt wirst, wenn du pflegeleicht bist. Das fühlt sich sicher an. Aber am Ende bist du für alle da, nur nicht für dich.",
        "task": "Deine Lebensaufgabe: dich selbst an die erste Stelle setzen, ohne schlechtes Gewissen.",
        "tools": ["Frag dich bei Entscheidungen zuerst: Was will eigentlich ich?", "Übe kleine, klare Ansagen im Alltag, statt dich anzupassen und später innerlich zu grollen.", "Mach den ersten Schritt bewusst allein. Mut wächst im Tun."],
    },
    "Stier": {
        "higher": "Du wächst über Ruhe, Beständigkeit und Selbstwert. Du darfst deinem eigenen Tempo vertrauen, das Einfache genießen und Dinge bauen, die bleiben. Weniger Drama, mehr Boden unter den Füßen.",
        "lower": "Dein vertrautes Muster sucht Intensität, Krise und Kontrolle. Du hinterfragst alles bis auf den Grund und misstraust der Ruhe, als wäre sie nur die Stille vor dem Sturm. Diese Daueranspannung kennst du gut. Sie hat dich einmal beschützt. Heute erschöpft sie dich nur noch.",
        "task": "Deine Lebensaufgabe: spüren, dass Sicherheit und Genuss erlaubt sind und nicht erkämpft werden müssen.",
        "tools": ["Bau dir feste kleine Routinen, die dir guttun.", "Wenn du ins Grübeln kippst, komm zurück in den Körper: Natur, Essen, Berührung.", "Vertrau darauf, dass etwas auch dann bleibt, wenn du es nicht kontrollierst."],
    },
    "Zwillinge": {
        "higher": "Du wächst über Neugier und Nähe im Alltag. Du bist hier, um Fragen zu stellen, wirklich zuzuhören und in den vielen kleinen Verbindungen präsent zu sein. Das Leben findet im Kleinen statt, direkt vor dir.",
        "lower": "Dein vertrautes Muster will recht haben und die große Wahrheit verkünden. Du weißt schon Bescheid, belehrst und überspringst das Detail. Vielleicht fühlst du dich sicherer, wenn du der bist, der die Antwort hat. Aber genau das entfernt dich vom echten Gegenüber.",
        "task": "Deine Lebensaufgabe: mehr fragen als dozieren und im Nahen ankommen.",
        "tools": ["Stell echte Fragen und hör zu Ende zu, bevor du deine Meinung sagst.", "Sammle konkrete Fakten statt fertiger Überzeugungen.", "Pflege die kleinen Kontakte in deinem Alltag, dort liegt gerade dein Wachstum."],
    },
    "Krebs": {
        "higher": "Du wächst über Gefühl und Nähe. Du darfst dich selbst nähren, verletzlich sein und dich anlehnen. Du musst nicht die Starke sein, die alles allein trägt.",
        "lower": "Dein vertrautes Muster greift zu Kontrolle, Pflicht und Härte gegen dich selbst. Du trägst alles allein und organisierst deine Gefühle weg, weil du gelernt hast, dass Schwäche gefährlich ist. Diese Rüstung ist schwer. Und einsam.",
        "task": "Deine Lebensaufgabe: dich lehnen und fühlen dürfen, ohne die Kontrolle zu verlieren.",
        "tools": ["Frag dich öfter: Wie geht es mir gerade? statt: Was muss ich noch leisten?", "Lass Nähe zu und bitte um Hilfe, auch wenn es ungewohnt ist.", "Gönn dir Fürsorge, ohne sie dir erst zu verdienen."],
    },
    "Löwe": {
        "higher": "Du wächst über Sichtbarkeit und Herz. Du bist hier, um aus dir heraus zu schaffen, Freude auszudrücken und deine eigene Bühne einzunehmen. Dein Strahlen darf gesehen werden.",
        "lower": "Dein vertrautes Muster versteckt dich in der Gruppe. Du bleibst cool, distanziert und willst bloß nicht auffallen. Vielleicht ist es dir sicherer, einer von vielen zu sein, als dich einzeln zu zeigen und vielleicht abgelehnt zu werden. Aber im Verstecken verkümmert dein Herz.",
        "task": "Deine Lebensaufgabe: dich zeigen und dein Herz sprechen lassen, auch wenn es sich exponiert anfühlt.",
        "tools": ["Erlaub dir, im Mittelpunkt zu stehen, statt dich hinter dem Wir zu verstecken.", "Schaff etwas, das wirklich von dir kommt, und zeig es.", "Sag öfter ich statt man, vor allem bei deinen Wünschen."],
    },
    "Jungfrau": {
        "higher": "Du wächst über Struktur und geerdete Fürsorge. Du darfst im Alltag ankommen, dir mit klaren, kleinen Schritten helfen und im Konkreten wirken. Ordnung im Außen bringt Ruhe in dein Innen.",
        "lower": "Dein vertrautes Muster verliert sich, flüchtet oder lässt sich treiben. Grenzen verschwimmen, und du rutschst schnell in das Gefühl, dass das Leben einfach mit dir passiert. Der Rückzug ins Diffuse fühlt sich weich an. Aber er hält dich davon ab, dein Leben wirklich anzupacken.",
        "task": "Deine Lebensaufgabe: im Alltag ankommen und dir mit klaren Schritten selbst helfen.",
        "tools": ["Bring Ordnung in eine kleine Ecke deines Lebens, das erdet dich sofort.", "Setz klare Grenzen, statt in allem zu verschwimmen.", "Kümmere dich konkret um deinen Körper und deinen Alltag, Schritt für Schritt."],
    },
    "Waage": {
        "higher": "Du wächst über Beziehung und Ausgleich. Du bist hier, um andere einzubeziehen, fair zu sein und gemeinsam zu gehen, statt alles allein zu stemmen. Verbindung macht dich nicht schwächer, sie macht dich reicher.",
        "lower": "Dein vertrautes Muster zieht alles im Alleingang durch. Du bist ungeduldig, gehst zu schnell vor und übergehst die anderen. Wahrscheinlich hast du gelernt, dass du dich auf niemanden verlassen kannst, außer auf dich. Das macht dich stark, aber auch sehr einsam.",
        "task": "Deine Lebensaufgabe: den anderen wirklich mitdenken und gemeinsam statt gegeneinander handeln.",
        "tools": ["Hol dir vor Entscheidungen bewusst die Sicht des anderen ein.", "Übe Geduld, wenn dich der Impuls packt, sofort allein loszurennen.", "Such Kompromisse aktiv, statt sie als Niederlage zu sehen."],
    },
    "Skorpion": {
        "higher": "Du wächst über Tiefe und echte Verbindung. Du darfst dich einlassen, teilen, die Kontrolle loslassen und dich verwandeln. Erst wenn du dich wirklich zeigst, wird Nähe echt.",
        "lower": "Dein vertrautes Muster hält fest. An Besitz, an Gewohntem, an dem, was sicher ist. Veränderung fühlt sich teuer und bedrohlich an, also bleibst du lieber beim Bekannten, auch wenn es dich längst nicht mehr nährt. Diese Bequemlichkeit ist ein weiches Gefängnis.",
        "task": "Deine Lebensaufgabe: dich einlassen und loslassen, auch wenn es unbequem wird.",
        "tools": ["Lass bewusst etwas los, an dem du aus Gewohnheit festhältst.", "Wag echte Tiefe, statt an der Oberfläche sicher zu bleiben.", "Frag dich: Halte ich das, weil es stimmt, oder nur, weil es vertraut ist?"],
    },
    "Schütze": {
        "higher": "Du wächst über Sinn, Weite und Vertrauen. Du bist hier, um für deine eigene Wahrheit einzustehen und das große Bild zu sehen. Nicht jede Kleinigkeit muss belegt sein, manches darfst du einfach glauben.",
        "lower": "Dein vertrautes Muster verzettelt sich. Du sammelst alle Meinungen, bleibst an der Oberfläche und legst dich bloß nicht fest. Solange du dich nicht entscheidest, kann nichts schiefgehen, denkst du. Aber diese ständige Unverbindlichkeit lässt dich nie irgendwo ankommen.",
        "task": "Deine Lebensaufgabe: dich auf deine eigene Wahrheit festlegen und ihr folgen.",
        "tools": ["Triff eine Entscheidung und bleib eine Weile dran, statt neu zu sammeln.", "Frag nach dem Warum hinter den Fakten, nicht nur nach mehr Fakten.", "Vertrau deiner inneren Richtung, auch ohne alle Informationen."],
    },
    "Steinbock": {
        "higher": "Du wächst über Verantwortung und Struktur. Du darfst erwachsen werden, dir sichtbare Ziele setzen und für dich sorgen wie ein guter, verlässlicher Erwachsener. Du darfst dein Leben in die Hand nehmen.",
        "lower": "Dein vertrautes Muster macht dich klein und abhängig. Du verkriechst dich im Vertrauten und wartest leise, dass jemand kommt und es für dich löst. Vielleicht fühlt sich Verantwortung wie eine zu große Last an. Aber im Warten bleibst du in einer Rolle, die dir längst zu eng ist.",
        "task": "Deine Lebensaufgabe: selbst die Erwachsene in deinem Leben sein und deine Ziele ernst nehmen.",
        "tools": ["Setz dir ein konkretes Ziel und geh es in kleinen, festen Schritten an.", "Übernimm Verantwortung für deine Lage, statt zu warten.", "Tröste dich selbst und mach dann den nächsten Schritt."],
    },
    "Wassermann": {
        "higher": "Du wächst über Gemeinschaft und Freiheit. Du bist hier, um mit genau deinem Anderssein zu etwas Größerem beizutragen. Du gehörst dazu, ohne dich verbiegen zu müssen.",
        "lower": "Dein vertrautes Muster braucht Anerkennung und den Mittelpunkt. Es geht schnell um dich, um dein Bild, um die Frage, wie du dastehst. Wahrscheinlich hast du gelernt, dass du nur zählst, wenn du besonders bist. Aber dieser Hunger nach Applaus macht nie wirklich satt.",
        "task": "Deine Lebensaufgabe: Teil von etwas Größerem sein, ohne ständig gesehen werden zu müssen.",
        "tools": ["Trag zu einer Sache bei, ohne auf Applaus zu warten.", "Freu dich am Erfolg anderer, statt ihn mit deinem zu vergleichen.", "Steh zu deinem Anderssein, es ist dein Beitrag, nicht dein Makel."],
    },
    "Fische": {
        "higher": "Du wächst über Vertrauen und Mitgefühl. Du darfst loslassen, weich werden und dich mit etwas Größerem verbinden. Du musst nicht alles im Griff haben, um sicher zu sein.",
        "lower": "Dein vertrautes Muster perfektioniert und kontrolliert. Du verlierst dich in Kritik, Sorge und Analyse, weil dir das ein Gefühl von Kontrolle gibt. Solange du an allem arbeitest, kann dich nichts überraschen, glaubst du. Aber dieses ständige Anspannen raubt dir die Leichtigkeit.",
        "task": "Deine Lebensaufgabe: vertrauen und loslassen, statt alles kontrollieren zu wollen.",
        "tools": ["Lass bewusst etwas unperfekt und schau, dass die Welt trotzdem trägt.", "Nimm dir Momente der Stille, in denen du nichts optimieren musst.", "Sei so sanft mit dir, wie du es mit einem lieben Menschen wärst."],
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
             "stiften. Deine Aufgabe ist, dabei nie dich selbst zu vergessen, denn echte Harmonie "
             "schließt dich mit ein.",
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
        9: "du bist im Kern eine Sinnsucherin, eine Reisende und eine Lehrerin",
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
        7: "Partnerschaft ist dir ein hoher Wert, du bist ein echter Beziehungsmensch",
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
        10: "dein Ehrgeiz treibt deine Karriere, du gehst gern als Erste voran",
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
        4: "in deiner Herkunft lag viel Verantwortung, du kommst innerlich eher spät an",
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
        11: "du bist eine Reformerin mit ganz besonderen Freundeskreisen",
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
        4: "in deiner Herkunft wirkten tiefe Kräfte, deine Familie durchläuft Wandlung",
        5: "dein Selbstausdruck ist intensiv, und deine Lieben verwandeln dich",
        6: "du wandelst zwanghafte Alltagsmuster und regenerierst dich aus der Tiefe",
        7: "deine Beziehungen sind intensiv, Macht und Kontrolle sind ein echtes Thema",
        8: "du bist eine Krisenmeisterin mit großer Tiefe und Erneuerungskraft",
        9: "dein Weltbild wandelt sich radikal, du suchst kompromisslos die Wahrheit",
        10: "deine öffentliche Rolle ist machtvoll, du steigst oft gerade durch Krisen auf",
        11: "du hast Einfluss in Gruppen und erlebst tief verwandelnde Freundschaften",
        12: "in dir wirken die tiefsten unbewussten Wandlungskräfte",
    },
}


def _pos_desc(key, sign, house):
    if key == "Chiron":
        return CHIRON_SIGN.get(sign, "Chiron zeigt, wo du verletzlich bist, und genau dort liegt "
                               "deine besondere Kraft, andere zu heilen.")
    base = PLANET_INTRO.get(key, "") + " " + SIGN_EMOTION.get(sign, "")
    ph = PLANET_HOUSE.get(key, {}).get(house)
    if ph:
        base += (f" Weil das bei dir im {house}. Haus steht, dem Lebensfeld für "
                 f"{HOUSE_MEANING.get(house, 'diesen Bereich')}, zeigt es sich ganz konkret so: {ph}.")
    elif house and key not in _ANGLES:
        base += (f" In deinem Leben spielt sich das vor allem im {house}. Haus ab, deinem "
                 f"Lebensfeld für {HOUSE_MEANING.get(house, 'diesen Bereich')}.")
    return base.strip()


def profile_name(profile):
    return PROFILE_NAMES.get(profile, " / ".join(
        PROFILE_LINES.get(int(x), "") for x in profile.split("/")))


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
            "Frag dich bei starken Gefühlen zuerst: Ist das gerade meins, oder habe ich es von "
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
            "Vertrau deinem allerersten Impuls, bevor der Zweifel kommt. Deine erste Antwort ist "
            "meistens die wahre.",
            "Bring deinen Körper in Bewegung. Beim Gehen, Tanzen oder Sport kommen deine besten "
            "Eingebungen wie von selbst.",
            "Setz deine Energie in eine kleine, sofortige Handlung um, statt sie zu zerdenken.",
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
            "Mach einen kurzen Body-Scan. Geh in Gedanken durch deinen Körper und spür, wo sich "
            "eine Entscheidung eng oder weit anfühlt.",
            "Geh in die Natur, am liebsten barfuß. Der Boden unter dir bringt dich zurück zu deinem "
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
            "Vertrau dem ersten Bild, das auftaucht, wenn du an eine Person oder eine Situation "
            "denkst.",
            "Gönn deinem Kopf Stille. In der Ruhe zwischen den Gedanken taucht die Eingebung auf.",
        ],
    },
}


WATER_SIGNS = {"Krebs", "Skorpion", "Fische"}
WATER_HOUSES = {4, 8, 12}

DEPTH_SUMMARY = {
    "außergewöhnlich stark": "Bei dir ist die intuitive Ader außergewöhnlich stark angelegt. "
        "Gleich mehrere Kräfte deines Charts spielen hier zusammen. Dein Gespür gehört zu deinen "
        "größten Talenten, also vertrau ihm.",
    "stark ausgeprägt": "Bei dir ist die intuitive Ader stark ausgeprägt. Dein Gespür ist ein "
        "verlässlicher Begleiter, sobald du ihm Raum und Ruhe gibst.",
    "deutlich spürbar": "Deine intuitive Ader ist deutlich spürbar. Am klarsten meldet sie sich in "
        "ruhigen Momenten, wenn der Alltag einmal leiser wird.",
    "fein und leise": "Deine Intuition ist eher fein und leise. Sie spricht in stillen "
        "Augenblicken, und je öfter du ihr zuhörst, desto deutlicher wird sie.",
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

    result = {
        "key": element,
        "archetype": base["archetype"],
        "tagline": base["tagline"],
        "moon_sign": moon_sign,
        "text": base["text"].format(moon=moon_sign),
        "tools": base["tools"],
        "all": [{"key": e, "archetype": INTUITION[e]["archetype"],
                 "tagline": INTUITION[e]["tagline"], "oneliner": INTUITION[e]["oneliner"]}
                for e in order],
        "note": "Dein Intuitionstyp entsteht aus deinem Mond, aus Neptun und Pluto und aus deinen "
                "Wasserhäusern (4, 8 und 12), dort, wo sich Wissenschaft und Astrologie begegnen. "
                "Verstehe ihn als ein Bild zur Selbstreflexion, das dich an deine eigene innere "
                "Stimme erinnert.",
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
            "text": f"Dein Mond steht in deinem {mh}. Lebensfeld. Hier, wo es um "
                    f"{HOUSE_MEANING.get(mh, 'diesen Bereich')} geht, ist deine Intuition am "
                    f"wachsten, und deinem Gefühl kannst du in diesen Themen besonders trauen."})
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
                    "sich von dir gesehen bis auf den Grund. Geh behutsam mit dieser starken Gabe "
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

    level = ("außergewöhnlich stark" if score >= 6 else
             "stark ausgeprägt" if score >= 4 else
             "deutlich spürbar" if score >= 2 else "fein und leise")
    result["depth"] = {
        "score": min(score, 8), "max": 8, "level": level,
        "summary": DEPTH_SUMMARY[level], "facets": facets,
    }
    return result


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
_ASPECT_QUAL = {
    "Konjunktion": "Diese beiden Kräfte verschmelzen in dir zu einer einzigen, sie sind fast untrennbar.",
    "Sextil": "Hier liegt ein leichtes Talent bereit, das du aktiv nutzen darfst.",
    "Trigon": "Das ist eine angeborene Begabung, die dir fast mühelos zufällt.",
    "Quadrat": "Das ist eine echte innere Reibung, und genau an ihr wächst du am meisten.",
    "Opposition": "Zwei Pole in dir, die nach Ausgleich suchen, oft spielst du sie über deine Beziehungen aus.",
    "Quinkunx": "Zwei fremde Kräfte, die ständig feine Justierung brauchen, bis sie zusammenfinden.",
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


def _element_section(nat, asc, mc):
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
    dom = max(counts, key=counts.get)
    low = min(counts, key=counts.get)
    lack = ("Das Element " + low + " fehlt in deinem Chart fast ganz. Das heißt: " + ELEMENT_WEAK[low]
            if counts[low] == 0 else
            "Am wenigsten ausgeprägt ist bei dir das Element " + low + ". Das heißt: " + ELEMENT_WEAK[low])
    body = (
        "Wenn man deine Planeten nach den vier Elementen ordnet, wird ein Muster sichtbar, das viel "
        "über dich erzählt.\n\n"
        f"Am stärksten ist bei dir das Element {dom}. In dir wirkt vor allem {ELEMENT_STRONG[dom]}. "
        "Das ist deine natürliche Sprache, die Art, wie du am liebsten durchs Leben gehst und dich "
        "am lebendigsten fühlst.\n\n"
        + lack + ".\n\n"
        "So eine Verteilung ist kein Mangel. Sie zeigt nur, wo deine Gaben von ganz allein fließen "
        "und wo du dir bewusst ein wenig dazuholen darfst. Oft ziehen wir genau die Menschen an, "
        "die unser schwächstes Element stark leben. Vielleicht kennst du das.")
    return {
        "title": "Deine Elemente-Balance",
        "subtitle": "Feuer, Erde, Luft und Wasser in deinem Chart",
        "headline": f"Deine Stärke liegt im {dom}",
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
        f"und über dich hinauswächst. Menschen mit einem Stellium wirken auf diesem einen Gebiet oft "
        f"wie Expertinnen von Geburt an. Wahrscheinlich kennst du dieses Gefühl an dir.")
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
    lines = []
    for o, a, b, nm in found[:4]:
        lines.append(
            f"Zwischen {a} und {b} liegt ein {nm}, fast auf den Punkt genau. {_ASPECT_QUAL[nm]} "
            f"Dein Thema {PLANET_MEANING.get(a, '').lower()} und dein Thema "
            f"{PLANET_MEANING.get(b, '').lower()} sind bei dir eng miteinander verwoben.")
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


def full_analysis(chart):
    """Die vollständige, liebevoll aufbereitete Analyse (nach der E-Mail)."""
    hd = chart["hd"]
    t = TYPE_INFO.get(hd["type"], {})
    name = chart.get("name") or "du"
    asc = chart.get("ascendant")

    sections = []
    _sun = chart["natal"].get("Sonne")
    _moon = chart["natal"].get("Mond")
    if _sun and _moon and asc:
        sections.append(_kern_section(_sun, _moon, asc))
    sections.append({
        "title": "Dein Human-Design-Typ",
        "headline": hd["type"],
        "body": ("Bevor du irgendwas an dir ändern willst, darfst du erst mal verstehen, wie du gebaut "
                 "bist. Dein Typ ist die Grundmelodie deiner Energie. Er zeigt dir, wie du am "
                 "leichtesten durchs Leben gehst und wo du dich immer wieder verausgabst.\n\n"
                 + t.get("short", "") + "\n\nVielleicht kennst du das. Du siehst Menschen, denen "
                 "vieles leicht fällt. Und du fragst dich, warum es bei dir an manchen Stellen so viel "
                 "schwerer geht. Meistens ist der Grund ganz einfach. Du hast versucht, nach einer "
                 "Melodie zu leben, die gar nicht deine ist.\n\nWenn du deiner eigenen Art vertraust, "
                 "ändert sich etwas Leises, aber Tiefes. Das Leben fühlt sich weniger nach Widerstand "
                 "an. Es fängt an, dich zu tragen."),
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
        "facts": [],
    })
    sections.append({
        "title": "Dein Profil",
        "headline": f"{hd['profile']}, {profile_name(hd['profile'])}",
        "body": ("Dein Profil beschreibt die Rolle, in der sich dein Weg entfaltet. Stell es dir wie "
                 "ein Kostüm vor, das deine Seele für dieses Leben gewählt hat. Die erste Zahl lebst "
                 "du bewusst. Sie ist dir vertraut. Die zweite wirkt eher aus dem Verborgenen. Andere "
                 "sehen sie oft früher in dir als du selbst.\n\n" + PROFILE_DESC.get(hd["profile"], "")
                 + "\n\nVielleicht erkennst du dich in beiden Seiten wieder. Und du hast dich manchmal "
                 "gefragt, warum du so widersprüchlich sein kannst. Das ist kein Widerspruch. Das ist "
                 "dein Design. Wenn du beide Seiten in dir sein lässt, wirst du ganz."),
        "facts": [("Definition", hd["definition"]),
                  ("Definierte Zentren", ", ".join(hd["defined_centers"]) or "keine")],
    })

    defined = hd.get("defined_centers", [])
    open_c = hd.get("open_centers", [])
    sections.append({
        "title": "Deine Zentren",
        "headline": f"{len(defined)} definiert, {len(open_c)} offen",
        "body": ("Stell dir deine Zentren wie neun Räume in dir vor. Manche sind fest eingerichtet und "
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
        "facts": [("Definiert", ", ".join(defined) or "keine"),
                  ("Offen", ", ".join(open_c) or "keine")],
    })

    nat = chart["natal"]
    if asc:
        sections.append(_element_section(nat, asc, chart.get("mc")))
        _stell = _stellium_section(nat)
        if _stell:
            sections.append(_stell)
        _asp = _aspects_section(nat)
        if _asp:
            sections.append(_asp)

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
            "takeaway": axis.get("task", ""),
            "facts": f,
        })
    if sk and axis:
        sections.append({
            "title": "Dein Lower Self",
            "subtitle": f"Südknoten in {sk['sign']}, dein vertrautes Muster",
            "headline": f"Deine Komfortzone liegt im {sk['sign']}",
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
            "facts": [("Südknoten", f"{sk['sym']} {sk['sign']} {sk['text']}")],
        })
    if nk and sk and axis:
        sections.append({
            "title": "Deine Lebensaufgabe",
            "subtitle": f"Deine Mondknoten-Achse: {sk['sign']} zu {nk['sign']}",
            "headline": f"Von {sk['sign']} nach {nk['sign']}",
            "body": (f"Deine Mondknoten-Achse ist der rote Faden deines Lebens. Sie zeigt, woher du "
                     f"kommst und wohin du wächst. Das {sk['sign']}-Muster ist dir vertraut und leicht. "
                     f"Dort fühlst du dich sicher. Dein Wachstum liegt auf der anderen Seite, im "
                     f"{nk['sign']}. Du kommst dorthin in kleinen Schritten. Immer dann, wenn du das "
                     f"alte Muster bewusst hinter dir lässt und den neuen Weg wählst."),
            "takeaway": axis.get("task", ""),
            "facts": [],
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
                     "ganzes Leben gewünscht hast: Mit dir war nie etwas falsch. Diese Wunde macht "
                     "dich nicht kaputt. Sie macht dich weich. Weil du diesen Schmerz so gut kennst, "
                     "spürst du ihn bei anderen sofort. Du bist der Mensch, der einem anderen sagen "
                     "kann: Du bist genug. Und der es auch so meint. Deine Wunde und deine Gabe sind "
                     "dieselbe Stelle. Du heilst genau durch sie."),
            "facts": facts,
        })

    if axis.get("tools"):
        tool_lines = "\n\n".join("• " + x for x in axis["tools"])
        sections.append({
            "title": "Deine Tools und Impulse",
            "subtitle": "Wie du gut mit dir und deiner Umwelt umgehst",
            "headline": "Kleine Schritte, große Wirkung",
            "body": ("Ein paar konkrete Impulse, wie du dein Higher Self stärkst und dein altes Muster "
                     "früh erkennst:\n\n" + tool_lines + "\n\nUnd im Umgang mit anderen: Lebe deine "
                     "Strategie, " + t.get("strategy", "").lower() + ", und triff wichtige "
                     "Entscheidungen über deine " + hd["authority"].lower() + ". So bleibst du bei "
                     "dir, auch wenn es um dich herum laut wird."),
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
               f"vertrauen. Lebe deine Strategie, {t.get('strategy','').lower()}, und hör auf deine "
               f"{hd['authority'].lower()}. Immer wenn sich etwas von innen richtig anfühlt, geh da "
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

    houses = [{"nr": i, "title": HOUSE_TITLE[i], "meaning": HOUSE_MEANING.get(i, "")}
              for i in range(1, 13)]

    intuition = build_intuition(chart)

    return {
        "name": name,
        "hd": hd,
        "sections": sections,
        "natal_rows": natal_rows,
        "positions": positions,
        "houses": houses,
        "hd_centers": hd_centers,
        "intuition": intuition,
        "ascendant": asc,
        "geo": geo,
        "closing": closing,
        "note": "Symbolische Deutung zur Selbstreflexion. Kein Ersatz für Beratung, keine Diagnose. "
                "Alle Positionen exakt berechnet (tropischer Tierkreis, Ganzzeichen-Häuser).",
    }
