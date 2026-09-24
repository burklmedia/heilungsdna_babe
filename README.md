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
  index.html            Frontend: Formular, magischer Moment, Teaser; Vollanalyse
                        nur unter /mein-bauplan (Link aus der E-Mail)
  impressum.html        Rechtsseiten
  datenschutz.html
  feedback.html         gebrandete Feedback-Seite (Formular -> POST /api/feedback)
  bestaetigt.html       Seite nach dem Klick in der Bestaetigungsmail (/bestaetigt)
  fonts/                lokal gehostete Schriften (Cormorant, Mulish) -> kein Google
  greatvibes*.woff2     Wortmarken-Schrift
  favicon.svg, ...      Favicon + Apple-Touch-Icon
  og-image.jpg          Social-Vorschaubild (Open Graph)
  denise.jpg            Foto Denise
  robots.txt            Suchmaschinen-Regeln (verweist auf die Sitemap)
  sitemap.xml           Sitemap (Startseite)

api/
  analyze.py            berechnet Chart, liefert Teaser + Vollanalyse (JSON)
    ├─ _engine.py       Swiss-Ephemeris-Rechenkern (Moshier, Chiron via seas_18.se1)
    ├─ _interpret.py    Textbausteine für Teaser und Vollanalyse
    └─ _geo.py          Offline-Städte-Fallback (geonamescache + timezonefinder)
  pdf.py                rendert den kompletten Bauplan als PDF (fpdf2), Design
                        wie die Website-Reiter: Medaillon-Deckblatt aus Chart +
                        Bodygraph, Inhaltsverzeichnis, Uebersicht, Kapitel, Abschluss
  subscribe.py          reicht Vorname, E-Mail, Bauplan-Link und Feedback-Token an
                        das ActiveCampaign-Formular weiter (Double-Opt-in)
  track.py              cookiefreies Zaehlen der Funnel-Schritte
  stats.py              passwortgeschuetzte Statistik-Seite
  feedback.py           Feedback zum Bauplan: speichert Antworten in der KV und
                        setzt in ActiveCampaign "Feedback gegeben" (Zuordnung ueber Token)
  topic.py              Themenauswahl: setzt in ActiveCampaign "Bauplan-Thema"
  _ac.py                ActiveCampaign-REST nur fuer bestehende Kontakte (Felder
                        setzen, nie anlegen), Feld-IDs, Uebergang fuer MailerLite
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
| `GET /mein-bauplan?d=…` | persönliche Bauplan-Seite (Link aus der E-Mail), komplette Auswertung + PDF-Button |
| `POST /api/subscribe` | Anmeldung über das ActiveCampaign-Formular, mit Bauplan-Link (`%BAUPLAN_PDF%`) und Feedback-Token |
| `GET /api/subscribe` | Diagnose: Formular verbunden, API-Key da (nur ja/nein) |
| `GET /bestaetigt` | Seite nach dem Klick in der Bestätigungsmail |
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
4. **E-Mail-Feld**: für den kompletten Bauplan. Geht an das
   ActiveCampaign-Formular (Double-Opt-in). Danach öffnet sich ein
   Hinweisfenster „Deine komplette Auswertung kommt per E-Mail". Auf der
   Startseite wird vom Ergebnis nichts gezeigt.
5. **Bestätigung**: ActiveCampaign schickt die Bestätigungsmail. Der Klick
   darin führt auf `/bestaetigt`, erst jetzt ist der Kontakt aktiv.
6. **Mail mit Link**: Die Automation schickt Mail 1 mit dem Button zur
   persönlichen Bauplan-Seite `/mein-bauplan?d=…` (komplette Auswertung mit
   Reitern, dazu **„Als PDF speichern"**).

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
| `AC_API_URL` / `AC_API_KEY` | ActiveCampaign-API (Einstellungen → Entwickler), nur für Feedback und Themenwahl. Die Anmeldung selbst braucht keinen Schlüssel |
| `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` | Speicher für Statistik, Feedback-Token und Feedback (alternativ `KV_REST_API_URL` / `KV_REST_API_TOKEN` von Vercel KV) |
| `STATS_PASSWORD` | Passwort für `/api/stats` |
| `MAILERLITE_API_KEY` | nur noch im Übergang: Feedback und Themenwahl von Altkontakten, die noch in MailerLite stehen. Danach löschen |

Nach dem Setzen jeweils **einmal neu deployen**, für Production **und** Preview.

## E-Mail-Versand (ActiveCampaign)

Aufgebaut wie beim MUSTER-Quiz von tobixsoulgrowth, im selben Konto
`burkl-media.activehosted.com`.

**Anmeldung über das Formular.** `api/subscribe.py` schickt Vorname, E-Mail,
Bauplan-Link und Feedback-Token an das AC-Formular „Kosmischer Bauplan"
(Formular 5, `proc.php`, Werte `u`, `f`, `or` aus dem Einbettungscode in
`FORM`). Der
Umweg über das Formular ist nötig: Nur dort hängt der Double-Opt-in, und an
unbestätigte Kontakte verschickt ActiveCampaign gar nichts. Ohne ausgefüllte
`FORM`-Werte nimmt die Funktion keine Anmeldung an (503), statt Adressen still
zu verlieren. `GET /api/subscribe` zeigt, ob alles verbunden ist.

**Liste und Felder.** Liste 6 „Kosmischer Bauplan · Intuition mit Herz",
Felder (nur dieser Liste zugeordnet):

| ID | Feld | Platzhalter | gesetzt von |
|---|---|---|---|
| 4 | Bauplan-Link (Textbereich) | `%BAUPLAN_PDF%` | Formular beim Absenden |
| 5 | Feedback-Token | `%FEEDBACK_TOKEN%` | Formular beim Absenden |
| 6 | Feedback gegeben | `%FEEDBACK_GIVEN%` | `api/feedback.py` über die API, Wert `yes` |
| 7 | Bauplan-Thema | `%BETA_TOPIC%` | `api/topic.py` über die API |

Im Formular heißen sie `field[4]` und `field[5]`. Ändern sich die IDs, weil
ein Feld neu angelegt wird, müssen `api/_ac.py` und der Einbettungscode
zusammenpassen.

**Ablauf.** Absenden → Kontakt „unbestätigt", AC verschickt die
Bestätigungsmail aus dem Formular → Klick → Weiterleitung auf `/bestaetigt`,
Kontakt aktiv → Automation mit Auslöser „Abonniert eine Liste" schickt die
Reihe. In den Mails führt der Button zu
`https://bauplan.intuitionmitherz.de/mein-bauplan?d=%BAUPLAN_PDF%`, die
Links zu Feedback und Themenwahl tragen `?t=%FEEDBACK_TOKEN%`.

**Mails.** Die ActiveCampaign-Fassungen liegen in `emails/activecampaign/`,
jede mit Kopfkommentar zu Betreff, Vorschau und Einsetzen. Text und Look sind
1:1 aus den MailerLite-Dateien in `emails/`, geändert sind nur die Platzhalter
(`%FIRSTNAME%`, `%BAUPLAN_PDF%`, `%FEEDBACK_TOKEN%`, `%UNSUBSCRIBELINK%`) und
die Fußzeile mit Anschrift, Impressum, Datenschutz und Abmeldelink. Die
Anschrift kommt über `%SENDER-INFO-SINGLELINE%` aus Einstellungen → Adressen:
Denises Adresse, der Bauplan-Liste zugeordnet (AC erlaubt beliebig viele
Adressen, eine davon ist Standard, dort steht Burkl Media für MUSTER). Nur wenn
`%SENDER-INFO-SINGLELINE%` und `%UNSUBSCRIBELINK%` in der Mail stehen, lässt
AC seinen eigenen Fuß mit „Abbestellen“ weg; löschen lässt er sich nicht. Die
Bestätigungsmail steht in `emails/activecampaign/double-opt-in.html`. Sie
gehört als HTML-Block ins Formular, nicht in die Automation.

**Automation „Kosmischer Bauplan · Starter".** 1:1 aus der MailerLite-Automation
„Denise Starter E-Mail". In AC heißen die Bausteine Warten, Wenn/Sonst und
Gehe zu:

```
Auslöser: Abonniert Liste 6 (feuert erst nach dem Klick in der
          Bestätigungsmail), läuft mehrfach
Tag 0   Mail 1  Dein Bauplan ist fertig                   mail-1.html
        1 Tag warten
Tag 1   Mail 2  Drei Stellen für den Anfang               mail-2.html
        2 Tage warten
Tag 3   Wenn/Sonst: Bauplan-Link in Mail 1 ODER in Mail 2 geklickt
        ├ Ja:   Mail 3a  Eine Frage (Antwort per Mail)    mail-frage.html
        │       2 Tage warten   ◄─────────────────────┐
Tag 5   │       Mail 4  Feedback                      │   mail-3.html
        │       3 Tage warten                         │
Tag 8   │       Wenn/Sonst: „Feedback gegeben" ist yes│
        │       ├ Ja:   4 Tage warten   ◄──────────┐  │
Tag 12  │       │       Mail 6  Themenwahl         │  │   mail-thema.html
        │       │       Ende                       │  │
        │       └ Nein: Mail 5  Feedback-Erinnerung│  │   mail-feedback-erinnerung.html
        │               Gehe zu ───────────────────┘  │
        └ Nein: Mail 3b  Rückhol-Mail                 │   mail-rueckhol.html
                Gehe zu ──────────────────────────────┘
```

Look aller Mails: dunkles Violett, goldene Wortmarke, gold gerahmte Karte,
Gold-Button, Signatur. Vorlage: `emails/_TEMPLATE.html`. Bilder
(`email-wordmark.png`, `email-signature-gold.png`) liegen in `public/`.

**Übergang.** Wer sich vor der Umstellung angemeldet hat, steht noch in
MailerLite und bekommt die dort begonnene Reihe weiter. Solange
`MAILERLITE_API_KEY` gesetzt ist, landen Feedback und Themenwahl dieser
Altkontakte in MailerLite, aber nur bei Adressen, die MailerLite schon kennt.

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
nicht umkehrbar): `api/subscribe.py` erzeugt ihn bei der Anmeldung, legt das
Mapping `imh:fbtok:<token> = E-Mail` in der KV ab und schickt den Token im
Feld „Feedback-Token" an ActiveCampaign. Der Mail-Link lautet dann
`https://bauplan.intuitionmitherz.de/feedback?t=%FEEDBACK_TOKEN%`.

Beim Absenden löst `api/feedback.py` den Token zur E-Mail auf, legt genau einen
Datensatz in der KV-Liste `imh:feedback` ab (die sieben Antworten, kein Verkauf,
kein Testimonial) und setzt in ActiveCampaign „Feedback gegeben" auf `yes`,
nur beim bestehenden Kontakt (`api/_ac.py` sucht per E-Mail und legt nie an).
Daran erkennt die Automation, ob die Feedback-Erinnerung noch nötig ist.
Doppel-Absenden ist verhindert (Browser-Merker plus serverseitige
`SET NX`-Sperre `imh:fbdone:<token>`). Die Rückmeldungen liest man geschützt über
`/api/feedback?pw=…` (gleiches Passwort wie die Statistik). ActiveCampaign
bekommt bewusst nur Token und Ja/Nein, keine Freitexte.

## Datenschutz

- **Schriften lokal gehostet**, keine Google Fonts (keine IP-Übertragung an
  Google).
- **Tracking cookiefrei** und ohne personenbezogene Daten.
- **Impressum** und **Datenschutzerklärung** liegen unter `public/`.
- Ortssuche über Open-Meteo (EU, keine Cookies) ist in der
  Datenschutzerklärung genannt.

## Nächste Ausbaustufen

- **Domain:** Produktiv-Adresse ist `bauplan.intuitionmitherz.de` (Subdomain bei
  Hostinger, CNAME auf Vercel). robots.txt, sitemap.xml, Canonical und die
  Social-/E-Mail-URLs zeigen bereits darauf. Einmalig nötig: DNS-CNAME bei
  Hostinger + Domain im Vercel-Projekt hinzufügen.
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

Lokal geht beim E-Mail-Schritt nichts an ActiveCampaign, die Anmeldung wird
nur angenommen. Wer den echten Weg samt Bestätigungsmail testen will:
`BAUPLAN_AC_LIVE=1 python3 dev.py` (legt einen echten Kontakt an).

Tests ohne Netzwerk:

```bash
python3 tests/test_activecampaign.py
python3 tests/test_freebie_integrity.py
python3 tests/test_handoff.py
```

Der lokale Server bedient Frontend und API wie Vercel. Beenden mit `Strg+C`.
Für das PDF wird `fpdf2` gebraucht (steht in `requirements.txt`). Für die
Statistik lokal Upstash-Variablen und `STATS_PASSWORD` setzen, sonst zeigt die
Seite nur den Hinweis, dass noch kein Speicher verbunden ist.

---

*Symbolische Deutung zur Selbstreflexion, kein Ersatz für Beratung, keine
Diagnose. Alle Positionen exakt berechnet (tropischer Tierkreis, Häuser in
Ganzzeichen und Placidus).*
