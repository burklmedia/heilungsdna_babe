# 🌙 Intuition mit Herz — Schnellstart für Denise

Diese Datei ist deine kurze, entspannte Anleitung. Kein Technik-Kauderwelsch. 🤍

---

## Was ist das hier?

Eine Website, auf der Menschen ihren **Namen, Geburtsdatum, Geburtsort** und
(optional) die **Geburtszeit** eingeben. Dann passiert ein kleiner magischer
Moment — und sie bekommen ihr **Human Design + Geburtshoroskop**, exakt
berechnet und mit Herz erklärt. Für die *komplette* Analyse hinterlassen sie
ihre E-Mail. So wächst deine Liste. 💌

Das Wichtigste: **Alles wird richtig gerechnet.** Nicht von einer KI geraten,
sondern von echter Astronomie-Software (Swiss Ephemeris). Getestet gegen dein
eigenes Chart und das von Tobias — alles stimmt auf die Bogenminute.

---

## 🖥️ Auf deinem Rechner ansehen (lokal)

Öffne ein **Terminal** und tippe der Reihe nach:

```bash
# 1. Projekt holen (nur beim ersten Mal)
git clone -b claude/astrology-analysis-tool-4c2brg https://github.com/burklmedia/heilungsdna_babe.git
cd heilungsdna_babe

# 2. Zutaten installieren (nur beim ersten Mal)
pip install -r requirements.txt

# 3. Starten
python3 dev.py
```

Dann erscheint im Terminal:

```
✦  Intuition mit Herz — lokaler Dev-Server läuft
→  Öffne im Browser:  http://localhost:8000
```

👉 Diese Adresse **http://localhost:8000** im Browser öffnen — fertig, du siehst
die ganze Seite live.

**Beenden:** im Terminal `Strg` + `C` drücken.

> 💡 Windows? Dann statt `python3` einfach `python` schreiben.
> Kein Python installiert? Test mit `python3 --version`. Wenn nichts kommt,
> sag mir Bescheid — ich zeig dir die 2-Minuten-Installation.

---

## 🌍 Ins Internet stellen (Vercel)

1. Auf [vercel.com](https://vercel.com) einloggen → **Add New Project**
2. Repo `heilungsdna_babe` importieren, Branch
   `claude/astrology-analysis-tool-4c2brg` wählen
3. **Framework: „Other"** einstellen, sonst nichts ändern
4. **Deploy** klicken → du bekommst eine öffentliche Web-Adresse

Kosten: praktisch **0 €**.

---

## 💌 E-Mail-Adressen wirklich sammeln

Standardmäßig nimmt die Seite die Adresse an, speichert sie aber noch nirgends.
Um sie automatisch zu sammeln, verbinden wir einen Newsletter-Dienst (z. B.
**Brevo**, kostenloser Tarif). Das richte ich dir gern ein — es sind nur zwei
Angaben in Vercel. Sag einfach Bescheid.

---

## ✨ Was als Nächstes kommen könnte

- Die Texte noch persönlicher schreiben lassen (mit Claude)
- Die **Beziehungsanalyse** (zwei Menschen, wie dein Denise×Tobias-Artefakt)
  als kostenpflichtiges Premium
- Die Analyse als schönes **PDF per E-Mail** verschicken

Du führst, ich baue. 💫
