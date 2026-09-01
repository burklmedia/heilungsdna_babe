# Intuition mit Herz, Kosmischer Bauplan 🤍

Eine kostenlose Web-Analyse: Menschen geben **Name, Geschlecht, Geburtsdatum,
Geburtszeit und Geburtsort** ein und bekommen ihren **kosmischen Bauplan**
(Human Design, Natalchart, Intuitionstyp und Numerologie), exakt berechnet und
liebevoll erklärt. Sie lesen ihn direkt auf der Seite und können ihn als
gebrandetes **PDF** herunterladen. Im Gegenzug hinterlassen sie ihre E-Mail
(Lead-Magnet).

## Warum das zu 100 % korrekt ist

Eine KI kann Natalchart und Human Design **nicht** zuverlässig ausrechnen.
Deshalb trennen wir sauber:

| Aufgabe | Wer | Kosten |
|---|---|---|
| Planeten, Aszendent, Häuser exakt berechnen | **Swiss Ephemeris** (Code) | 0 € |
| Human Design (Typ, Autorität, Profil, Tore, Kanäle) | deterministischer Code | 0 € |
| Numerologie (Lebenszahl, Persönliches Jahr) | deterministischer Code | 0 € |
| Der schöne, persönliche Text | Textbausteine im Code | ~0 € |

Die Engine wurde gegen reale, handkorrigierte Charts (Denise und Tobias)
validiert. Alle Planeten, beide Aszendenten, beide MCs und das komplette
Human Design stimmen auf die Bogenminute. Häuser werden in **Ganzzeichen**
und **Placidus** ausgegeben.

Nichts wird vorgespeichert: Jede Analyse und jedes PDF entsteht frisch aus den
eingegebenen Geburtsdaten.

## Architektur (laufende Kosten ≈ 0 €)

```
public/
  index.html            Frontend: Formular, magischer Moment, Teaser, Vollanalyse
  impressum.html        Rechtsseiten
  datenschutz.html
  feedback.html         gebrandete Feedback-Seite (Formular -> POST /api/feedback)
  fonts/                lokal gehostete Schriften (Cormorant, Mulish) -> kein Google
  greatvibes*.woff2     Wortmarken-Schrift
  favicon.svg, ...      Favicon + Apple-Touch-Icon
  og-image.jpg          Social-Vorschaubild (Open Graph)
  denise.jpg            Foto Denise

api/
  analyze.py            berechnet Chart, liefert Teaser + Vollanalyse (JSON)
    ├─ _engine.py       Swiss-Ephemeris-Rechenkern (Moshier, Chiron via seas_18.se1)
    ├─ _interpret.py    Textbausteine für Teaser und Vollanalyse
    └─ _geo.py          Offline-Städte-Fallback (geonamescache + timezonefinder)
  pdf.py                rendert den kompletten Bauplan als PDF (fpdf2), Design
                        wie die Website-Reiter: Medaillon-Deckblatt aus Chart +
                        Bodygraph, Inhaltsverzeichnis, Uebersicht, Kapitel, Abschluss
  subscribe.py          traegt E-Mail in MailerLite ein, setzt den PDF-Link
  track.py              cookiefreies Zaehlen der Funnel-Schritte
  stats.py              passwortgeschuetzte Statistik-Seite
  feedback.py           Feedback zum Bauplan: speichert Antworten in der KV und
                        setzt in MailerLite feedback_given=yes (Zuordnung ueber Token)
  _store.py             Mini-Redis-Helfer (Upstash/Vercel KV), Statistik + Feedback
  _assets/fonts/        Schriften fuers PDF (Cormorant, Mulish, Great Vibes,
                        AstroSymbols fuer die Tierkreis- und Planetenzeichen)

dev.py                  lokaler Server, bedient Frontend + API wie Vercel
vercel.json             Routing + Python-Builds (includeFiles: api/**)
requirements.txt        pyswisseph, timezonefinder, geonamescache, tzdata, fpdf2
```

### Endpunkte

| Route | Zweck |
|---|---|
| `POST /api/analyze` | Geburtsdaten rein, Teaser + Vollanalyse als JSON raus |
| `GET /api/pdf?d=…` | kompletter Bauplan als PDF (Daten base64url im Parameter `d`) |
| `POST /api/subscribe` | E-Mail zu MailerLite, speichert PDF-Link im Feld `bauplan_pdf` |
| `POST /api/track` | anonymer Funnel-Zaehler (visit, himmel, teaser, email, bauplan, scroll, pdf) |
| `GET /api/stats?pw=…` | Statistik-Seite (Funnel + 14-Tage-Verlauf) |
| `POST /api/feedback` | Feedback zum Bauplan (Token `t`), speichert in der KV, setzt `feedback_given=yes` |
| `GET /api/feedback?pw=…` | geschuetzte Ansicht aller Rueckmeldungen (Passwort `STATS_PASSWORD`) |

## Der Funnel

1. Formular ausfüllen (Name, Geschlecht, Geburtsdatum, Geburtszeit, Geburtsort)
   und **„Meinen Himmel lesen"**. Ortssuche über Open-Meteo (lat/lon + Zeitzone).
2. **Magischer Moment**: die Sternenkarte formt sich (Animation).
3. **Teaser**: persönliche, dynamische Begrüßung mit echtem Astro-Fakt, dazu eine
   versiegelte Vorschau des fertigen Bauplans (Chart + Bodygraph).
4. **E-Mail-Feld**: für den kompletten Bauplan. Trägt in MailerLite ein
   (Double-Opt-in).
5. **Vollanalyse** auf der Seite, plus Button **„Als PDF speichern"**.

## Deployment auf Vercel

1. Repo mit Vercel verbinden (vercel.com, *Add New Project*, Repository importieren).
2. Kein Build-Command nötig. `vercel.json` definiert die Python-Builds und Routen;
   `public/` ist statisch, `api/*.py` werden zu Python-Funktionen.
3. **Deploy**. Python-Abhängigkeiten aus `requirements.txt` installiert Vercel
   automatisch.

> Hinweis: Läuft das Projekt auf einem Branch (nicht `main`), ist es ein
> **Preview**-Deployment. Umgebungsvariablen müssen dann auch für **Preview**
> freigegeben sein, sonst kommen sie nicht bei den Funktionen an.

## Umgebungsvariablen

| Variable | Wofür |
|---|---|
| `MAILERLITE_API_KEY` | E-Mail-Anbindung (MailerLite) |
| `MAILERLITE_GROUP_ID` | Zielgruppe in MailerLite (z. B. „Denise Analyse") |
| `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` | Speicher für die Statistik (alternativ `KV_REST_API_URL` / `KV_REST_API_TOKEN` von Vercel KV) |
| `STATS_PASSWORD` | Passwort für `/api/stats` |
| `BREVO_API_KEY` / `BREVO_LIST_ID` | optionaler Fallback statt MailerLite |

Nach dem Setzen jeweils **einmal neu deployen**.

## E-Mail-Sammlung (MailerLite, aktiv)

`api/subscribe.py` legt jede Adresse in MailerLite an (Double-Opt-in) und
speichert im Feld `bauplan_pdf` den persönlichen PDF-Parameter. In der
Willkommensmail baut man einen Button mit der Verlinkung
`https://<domain>/api/pdf?d={$bauplan_pdf}`, so bekommt jede Person ihren
eigenen Bauplan als PDF. Ohne konfigurierten Key nimmt die Funktion die
Adresse an und antwortet ok (Brevo ist als Fallback vorhanden).

Die Willkommens- und Automations-Mails liegen als fertige HTML-Dateien in
`emails/`. Alle Mails nutzen denselben, an die Website angeglichenen Look
(dunkles Violett, goldene Wortmarke, gold gerahmte Karte, Gold-Button,
Signatur). Vorlage: `emails/_TEMPLATE.html`; Referenz: `emails/mail-1.html`
(Tag 0) und `emails/mail-2.html` (Tag 1). Bilder (`email-wordmark.png`,
`email-signature-gold.png`) liegen in `public/`. Merge-Tags: `{$name}`,
`{$bauplan_pdf}`, `{$unsubscribe}`. Zum Einsetzen in MailerLite den HTML-Code
in einen Custom-HTML-Block kopieren.

## Eigenes Tracking (cookiefrei)

`api/track.py` zählt anonym die Funnel-Schritte: keine Cookies, keine Namen,
keine E-Mails, keine IP. Pro Browser-Sitzung wird jedes Ereignis einmal
gezählt. `api/stats.py` zeigt daraus einen Funnel mit Raten plus einen
14-Tage-Verlauf, geschützt über `STATS_PASSWORD`. Der Speicher ist ein
kostenloser Upstash-Redis (bzw. Vercel KV) über die REST-Schnittstelle; ohne
Speicher läuft die Seite normal weiter, es werden nur keine Zahlen gezählt.

## Feedback zum Bauplan

Nach der Feedback-Mail kommt die Person auf die eigene, gebrandete Seite
`public/feedback.html` (`/feedback`), nicht auf ein externes Formular. Die
Zuordnung läuft über einen **opaken Zufalls-Token** (kein E-Mail-Bestandteil,
nicht umkehrbar): `api/subscribe.py` erzeugt ihn beim Opt-in, legt das Mapping
`imh:fbtok:<token> = E-Mail` in der KV ab und speichert den Token im MailerLite-
Feld `feedback_token`. Der Mail-Link lautet dann
`https://<domain>/feedback?t={$feedback_token}`.

Beim Absenden löst `api/feedback.py` den Token zur E-Mail auf, legt genau einen
Datensatz in der KV-Liste `imh:feedback` ab (die sieben Antworten, kein Verkauf,
kein Testimonial) und setzt in MailerLite `feedback_given=yes` (Upsert per
E-Mail). Doppel-Absenden ist verhindert (Browser-Merker plus serverseitige
`SET NX`-Sperre `imh:fbdone:<token>`). Die Rückmeldungen liest man geschützt über
`/api/feedback?pw=…` (gleiches Passwort wie die Statistik). MailerLite bekommt
bewusst nur die zwei Zustände `feedback_token` und `feedback_given`, keine
Freitexte. Nötige MailerLite-Custom-Fields: `feedback_token` und `feedback_given`
(beide Typ Text).

## Datenschutz

- **Schriften lokal gehostet**, keine Google Fonts (keine IP-Übertragung an
  Google).
- **Tracking cookiefrei** und ohne personenbezogene Daten.
- **Impressum** und **Datenschutzerklärung** liegen unter `public/`.
- Ortssuche über Open-Meteo (EU, keine Cookies) ist in der
  Datenschutzerklärung genannt.

## Nächste Ausbaustufen

- **robots.txt, sitemap.xml, Canonical** und die Social-URLs auf die echte
  Domain umstellen (aktuell Preview-Adresse).
- **Vollanalyse-Text per Claude** noch persönlicher (Zahlen bleiben exakt).
- **Beziehungsanalyse (Synastrie)**, zwei Personen, wie im ursprünglichen
  Denise×Tobias-Artefakt, als Premium.
- **Bezahlung** via Stripe Payment Link, wenn die Nachfrage da ist.
- **Reset-Knopf** für die Statistik (Testzahlen vor Launch auf null).

## Lokal starten

```bash
# 1. Projekt holen (einmalig)
git clone -b claude/astrology-analysis-tool-4c2brg https://github.com/burklmedia/heilungsdna_babe.git
cd heilungsdna_babe

# 2. Abhängigkeiten installieren
pip install -r requirements.txt         # oder: pip3 install -r requirements.txt

# 3. Server starten
python3 dev.py                          # Windows: python dev.py
```

Dann im Browser öffnen: **http://localhost:8000**

Der lokale Server bedient Frontend und API wie Vercel. Beenden mit `Strg+C`.
Für das PDF wird `fpdf2` gebraucht (steht in `requirements.txt`). Für die
Statistik lokal Upstash-Variablen und `STATS_PASSWORD` setzen, sonst zeigt die
Seite nur den Hinweis, dass noch kein Speicher verbunden ist.

---

*Symbolische Deutung zur Selbstreflexion, kein Ersatz für Beratung, keine
Diagnose. Alle Positionen exakt berechnet (tropischer Tierkreis, Häuser in
Ganzzeichen und Placidus).*
