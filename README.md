# Intuition mit Herz — Kosmischer Bauplan 🤍

Eine kostenlose Web-Analyse: Menschen geben **Name, Geburtsdatum, Geburtsort
und (optional) Geburtszeit** ein und bekommen ihr **Human Design + Natalchart**
– exakt berechnet und liebevoll erklärt. Im Gegenzug für die vollständige
Analyse hinterlassen sie ihre E-Mail (Lead-Magnet).

## Warum das zu 100 % korrekt ist

Das Kernproblem war: Eine KI kann Natalchart und Human Design **nicht**
zuverlässig ausrechnen. Deshalb trennen wir sauber:

| Aufgabe | Wer | Kosten |
|---|---|---|
| Planeten, Aszendent, Häuser exakt berechnen | **Swiss Ephemeris** (Code) | 0 € |
| Human-Design (Typ, Autorität, Profil, Tore, Kanäle) | deterministischer Code | 0 € |
| Der schöne, persönliche Text | Textbausteine (später optional Claude) | ~0 € |

Die Engine wurde gegen reale, handkorrigierte Charts (Denise & Tobias)
validiert – **alle Planeten, beide Aszendenten, beide MCs und das komplette
Human Design stimmen auf die Bogenminute.**

## Architektur (laufende Kosten ≈ 0 €)

```
public/index.html         Frontend: Formular, magischer Moment, Ergebnis
  └─ Städte-Autocomplete   Open-Meteo (kostenlos, kein Key) → lat/lon + Zeitzone
api/analyze.py             Serverless: berechnet Chart, liefert Teaser + Voll-Analyse
  ├─ _engine.py            Swiss-Ephemeris-Rechenkern (Moshier, keine Datendateien)
  ├─ _interpret.py         Textbausteine für Gratis-Häppchen und Voll-Analyse
  └─ _geo.py               Offline-Städte-Fallback (geonamescache + timezonefinder)
api/subscribe.py           Serverless: nimmt E-Mail entgegen (Newsletter-Anbindung)
```

## Der Funnel

1. Vier Felder eingeben → **„Meinen Himmel lesen"**
2. Magischer Moment: die Sternenkarte formt sich (Animation)
3. **Kleiner Gratis-Funke**: Typ + ein Fingerzeig – nur ein Häppchen
4. **E-Mail-Feld**: „Möchtest du deine komplette Analyse? …"
5. Vollständige Analyse (Human Design + Natalchart + Deutung)

## Deployment auf Vercel

1. Dieses Repo mit einem Vercel-Konto verbinden (vercel.com → *Add New Project*
   → Repository importieren).
2. **Framework Preset:** „Other". Kein Build-Command nötig, `public/` ist die
   statische Wurzel, `api/*.py` werden automatisch zu Python-Funktionen.
3. **Deploy** klicken. Fertig – die Seite läuft.

Python-Abhängigkeiten stehen in `requirements.txt` und werden von Vercel
automatisch installiert.

## E-Mail-Adressen wirklich sammeln (optional)

Standardmäßig nimmt `api/subscribe.py` die Adresse an und antwortet ok – noch
ohne Anbindung. So verbindest du **Brevo** (kostenloser Tarif):

1. Konto auf [brevo.com](https://www.brevo.com), API-Key erzeugen.
2. In Vercel unter *Settings → Environment Variables*:
   - `BREVO_API_KEY` = dein Key
   - `BREVO_LIST_ID` = z. B. `2` (optional, ID deiner Kontaktliste)
3. Redeploy. Ab jetzt landen alle Adressen automatisch in Brevo.

MailerLite/Mailchimp lassen sich analog anbinden (eine Funktion, ein API-Call).

## Nächste Ausbaustufen (Ideen)

- **Voll-Analyse per Claude** noch persönlicher texten (Zahlen bleiben exakt).
- **E-Mail-Versand** der Analyse als schönes PDF/HTML.
- **Beziehungsanalyse (Synastrie)** – die zwei-Personen-Tiefe wie im
  ursprünglichen Denise×Tobias-Artefakt, als Premium (19–29 €).
- **Bezahlung** via Stripe Payment Link, wenn die Nachfrage da ist.

## Lokal testen

```bash
pip install -r requirements.txt
# kleiner Dev-Server siehe Projekt-Notizen; auf Vercel läuft es ohne Zusatz.
```

---

*Symbolische Deutung zur Selbstreflexion – kein Ersatz für Beratung, keine
Diagnose. Alle Positionen exakt berechnet (tropischer Tierkreis,
Ganzzeichen-Häuser).*
