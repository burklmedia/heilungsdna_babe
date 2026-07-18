# Session-Notizen — Stand & nächste Schritte

_Zuletzt aktualisiert: 2026-07-18_

## Was in dieser Session gebaut wurde (Step 1)

Die Startseite ist von einer statischen Info-Seite zu einer **Conversion-Landingpage mit
echtem Funnel** ausgebaut worden.

**Funnel (`public/index.html`):**
1. **Landing** — Hero mit 4 Geburtsfeldern (Name · Geburtsdatum · Geburtszeit optional ·
   Geburtsort mit Städte-Autocomplete) + Marketing-Sektionen (Pain, „Was ist drin", Über dich, Footer).
2. **Magischer Moment** — das Sternenrad-Ritual, jetzt **länger** (~7,2 s, 6 Status-Phasen).
   Stellschrauben im JS: `MIN_RITUAL` (Dauer) und das `STATUS`-Array (Texte).
3. **Ausführlicher Teaser** — großer Typ-Name + Beschreibung, 3 Fakten-Kacheln
   (Strategie/Profil/Sonne), hervorgehobener Autoritäts-Block, 🔒-Vorschau auf die Vollanalyse.
4. **E-Mail-Gate** — Vorname + E-Mail → Vollanalyse (normales Formular, kein externer Embed).
5. **Vollanalyse** — Human-Design-Panel, Natalchart-Tabelle, Deutungs-Sektionen, Abschluss.

**Backend (`api/_interpret.py`):**
- `teaser()` liefert jetzt viel mehr Inhalt (Typ-Beschreibung, Strategie, Autoritäts-Erklärung,
  Profil-Bedeutung `PROFILE_DESC`, Sonne/Mond, `locked_preview`). Deterministisch, 0 € KI-Kosten.

**Design:** Mitternachtshimmel (dunkel), Gold-Akzent + Blush, Serif-Display (Cormorant
Garamond via Google Fonts CDN) + Sans (Jost). Voll responsiv, `prefers-reduced-motion` beachtet.

## Lokal starten
```bash
pip install -r requirements.txt   # bzw. nur: pip install pyswisseph
python3 dev.py                     # → http://localhost:8000
```
Hinweis: `timezonefinder==8.2.5` baut auf Python 3.9 nicht; für den Normalweg
(Städte-Autocomplete via Open-Meteo) nicht nötig.

## Offene Punkte für den Vollausbau (nächste Runde)
- [ ] Echtes **Autor:innen-Foto** und finale Bio im „Über dich"-Block (aktuell Platzhalter).
- [ ] **Impressum / Datenschutz** als echte Seiten (`/impressum`, `/datenschutz`).
- [ ] **E-Mail-Anbindung** (Brevo o. ä.) in `api/subscribe.py` scharf schalten + echter Analyse-Versand.
- [ ] **Vollanalyse-Texte** vertiefen (optional per Claude persönlicher texten, Zahlen bleiben exakt).
- [ ] Teaser-/Marketing-**Copy** final abstimmen (Zielgruppe, Tonalität).
- [ ] Feinschliff **magischer Moment** (Dauer/Texte nach Geschmack).
- [ ] Cross-Browser-/Mobile-Test auf echten Geräten.
