---
name: carousel-generator
description: >-
  Schreibt komplette, save-starke Instagram-Karussells und rendert die Slides
  als saubere PNGs (1080×1350). Nutze diesen Skill, wenn jemand ein Karussell,
  einen Karussell-Post, Instagram-Slides, einen Slide-Post oder einen
  Save-Post zu einem Thema möchte ("Mach mir ein Karussell über …",
  "Instagram-Karussell", "carousel post", "slides for instagram"). Liefert
  2 Text-Varianten mit Slides + Design-Hinweisen und exportiert danach
  slide_1.png … slide_N.png über Chrome headless (lokal, kein Internet).
---

# Carousel Generator

Dieser Skill macht zwei Dinge:

1. **Schreiben** — komplette Instagram-Karussells als Text (Hook, Slides, CTA),
   in **zwei** Varianten, mit kurzen Design-Hinweisen.
2. **Rendern** — die gewählte Variante in die HTML-Vorlage füllen und als
   PNGs exportieren (1080×1350) über Chrome/Chromium headless.

Immer zuerst schreiben, dann (auf Wunsch) rendern.

---

## 1. Brand-Konfiguration

> Diese Werte steuern Stimme, Wortwahl und Inhalte. Sie sind für die Marke
> **„Intuition mit Herz" (Denise)** ausgefüllt. Beim Einsatz für eine andere
> Marke einfach überschreiben.

- **Nische:** Astrologie, Human Design & Natalchart als Werkzeug zur
  Selbstreflexion — „dein kosmischer Bauplan".
- **Zielgruppe:** feinfühlige, spirituell interessierte Menschen (vorwiegend
  Frauen 25–45), die sich selbst besser verstehen, entscheiden und
  entfalten wollen — sanft, aber ernsthaft, kein Eso-Kitsch.
- **Tonalität:** warm, klar, ermutigend. Du-Ansprache. Herz + Substanz.
  Poetisch dosiert, nie schwurbelig. Kurze Sätze, echte Bilder.
- **Content-Säulen:**
  1. Human Design (Typ, Autorität, Profil, Strategie) alltagsnah erklärt.
  2. Astrologie/Natalchart (Sonne, Mond, Aszendent, Häuser) zum Verstehen
     statt Vorhersagen.
  3. Selbstreflexion & Selbstannahme („darfst du sein, wie du gemacht bist").
  4. Entscheidungen aus der eigenen Autorität statt aus Angst.
- **Wortbank (gern verwenden):** kosmischer Bauplan, dein Design, Autorität,
  Strategie, sanft, klar, erlaubt, Energie, Muster, Wahrheit, Himmel lesen,
  auf die Bogenminute genau.
- **Tabus (nie tun):** keine Heils-/Heilungsversprechen, keine Diagnosen,
  keine Vorhersagen als Fakt, keine Angstmache, kein Fatalismus
  („dein Schicksal steht fest"), keine hohlen Buzzwords. Immer der Rahmen:
  *symbolische Deutung zur Selbstreflexion, kein Ersatz für Beratung.*
- **Handle / Brandmark:** „Intuition mit Herz" · @deniseeichberg (im
  Bild-Template als Kürzel gesetzt).

---

## 2. Ein Karussell schreiben

Wenn der Nutzer ein Thema nennt, liefere **zwei Varianten (A und B)**. Jede
Variante hat **7–9 Slides** nach diesem Bauplan:

- **Slide 1 – Hook.** Ein einziger Gedanke, der stoppt. Spannung oder
  Erkenntnis, keine Erklärung. Max. ~7 Wörter Headline + optional 1 Zeile.
- **Slides 2 … N-2 – Substanz.** Ein Punkt pro Slide. Konkret, anwendbar,
  in „Du"-Sprache. Je Slide eine fette Kernaussage + 1–2 stützende Zeilen.
- **Slide N-1 – Wende/Kern.** Die eigentliche Einsicht, der Aha-Moment,
  der den Save auslöst.
- **Slide N – CTA.** Eine klare Handlung: speichern, kommentieren, oder
  „Lies deinen Himmel" (Link in Bio). Sanft, nicht marktschreierisch.

Regeln:
- Ein Gedanke pro Slide. Lieber weniger Wörter, mehr Raum.
- Aktive, warme Sprache. Keine Floskeln, keine Fremdwörter-Show.
- Halte dich an Wortbank & Tabus oben.
- Save-Wert: gib etwas mit, das man behalten will (Merksatz, Mini-Framework,
  Reihenfolge, Frage zur Selbstreflexion).

**Ausgabeformat** je Variante:

```
### Variante A — „<Kurzer Titel>"
Slide 1 (Hook): <Headline> / <Unterzeile optional>
Slide 2: <Kernaussage> — <stützende Zeile>
…
Slide N (CTA): <Handlungsaufforderung>

Design-Hinweise: <Farbstimmung, 1 Bild-Idee, welche Slides fett/ruhig>
Caption-Idee (1 Satz): <optional>
```

Danach fragen: **„Soll ich Variante A oder B als PNGs rendern?"**

---

## 3. Slides rendern (PNG-Export)

1. Öffne `assets/karussell-template.html` und trage die Slides der gewählten
   Variante ein. Struktur der Vorlage: ein `<section class="slide">` pro Slide,
   mit `data-slide="1"`, `data-slide="2"`, … fortlaufend nummeriert.
   - Nutze `.kicker` (kleine Zeile oben), `.headline` (große Aussage),
     `.body` (Fließtext), `.cta` (Handlung). Nicht alle Elemente müssen auf
     jeder Slide vorkommen.
   - Marke/Look wird über `:root` und `.brandmark` oben in der HTML gesteuert.
2. Speichere die gefüllte Datei als `karussell.html` **neben** der Vorlage
   (im selben `assets/`-Ordner), damit relative Schriften/Styles greifen.
3. Rendere:
   ```bash
   bash assets/render.sh assets/karussell.html
   ```
   Das erzeugt `slide_1.png … slide_N.png` (je 1080×1350) im selben Ordner.
   Die Anzahl der Slides wird automatisch aus `data-slide=…` erkannt.

**Voraussetzung:** Google Chrome oder Chromium muss installiert sein
(headless, lokal, kein Internet). Reine Vorschau ohne Export: `karussell.html`
einfach im Browser öffnen.

---

## Beispiel (voll ausgefüllt) — Thema „Warum du dich manchmal ausgelaugt fühlst"

### Variante A — „Deine Energie hat Regeln"
- **Slide 1 (Hook):** „Du bist nicht faul. Du folgst dem falschen Takt."
- **Slide 2:** *Nicht jede Energie ist zum Dauerlauf gemacht.* — Dein Design
  sagt dir, wie du sie einsetzt, ohne auszubrennen.
- **Slide 3:** *Manche sind zum Anschieben gebaut, andere zum Reagieren.* —
  Zwingst du dich in den falschen Modus, kostet alles doppelt Kraft.
- **Slide 4:** *Erschöpfung ist oft nur ein Signal.* — Nicht „mehr
  durchhalten", sondern „anders ansetzen".
- **Slide 5 (Kern):** *Deine Autorität kennt die Antwort vor deinem Kopf.* —
  Bauch, Herz oder Timing — je nach deinem Bauplan.
- **Slide 6 (CTA):** „Willst du wissen, wie deine Energie tickt? Lies deinen
  Himmel — Link in Bio. 🤍 Speicher dir das für den nächsten müden Tag."

Design-Hinweise: tiefes Violett als Grund, goldener Akzent auf den fetten
Kernaussagen; Slide 1 & 5 ruhig und groß, Mittel-Slides mit `.kicker`.
Caption-Idee: „Ausgelaugt heißt selten faul — meistens nur: falscher Takt."

### Variante B — „3 Fragen, bevor du weiter powerst"
- **Slide 1 (Hook):** „Bevor du dich zwingst: 3 ehrliche Fragen."
- **Slide 2:** *Frage 1: Ist das meine Energie — oder die von allen um mich?*
- **Slide 3:** *Frage 2: Habe ich reagiert, oder nur funktioniert?*
- **Slide 4:** *Frage 3: Sagt mein Körper ja, oder nur mein Kalender?*
- **Slide 5 (Kern):** *Dein Design ist kein Limit. Es ist eine
  Gebrauchsanweisung.*
- **Slide 6 (CTA):** „Speicher dir die 3 Fragen. Und wenn du deinen Bauplan
  lesen willst: Link in Bio."

Design-Hinweise: nummerierte `.kicker` (Frage 1/2/3), viel Ruhe, Gold nur auf
Slide 5. Caption-Idee: „Drei Fragen, die dir ehrlicher antworten als dein
Terminkalender."
