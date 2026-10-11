"""
Prüft nach jedem Deploy, ob die Live-Seite noch funktioniert (seit 11.10.2026, Regel von Tobias).

    python3 tools/nach_deploy_pruefen.py            # live, bauplan.intuitionmitherz.de
    python3 tools/nach_deploy_pruefen.py http://localhost:8000

Löst nichts aus, das zählt, kostet oder jemanden anmeldet:
  - /api/subscribe nur per GET (Diagnose, startet die Funktion samt Paketen)
  - /api/analyze mit einem fiktiven Beispiel (Marie), nur Berechnung
  - /api/bericht und /api/hoeren nur mit ungültigen Eingaben (erwartet 400, nicht 500)
  - Seiten und wichtige Dateien per HEAD/GET
Alle Anfragen tragen das Cookie imh_intern=1, damit nichts in die Statistik fällt.
Exit-Code 1, wenn etwas nicht stimmt.
"""
import json
import sys
import urllib.error
import urllib.request

BASIS = (sys.argv[1] if len(sys.argv) > 1 else "https://bauplan.intuitionmitherz.de").rstrip("/")
KOPF = {"Cookie": "imh_intern=1", "User-Agent": "Mozilla/5.0 (Bauplan-Selbsttest)"}
BEISPIEL = {"name": "Marie", "gender": "weiblich", "date": "1994-06-14", "time": "08:42", "place": "Köln",
            "lat": 50.94, "lon": 6.96, "tz": "Europe/Berlin"}
FEHLER = []


def abruf(pfad, methode="GET", daten=None, timeout=60):
    body = json.dumps(daten).encode("utf-8") if daten is not None else None
    kopf = dict(KOPF)
    if body is not None:
        kopf["Content-Type"] = "application/json"
    req = urllib.request.Request(BASIS + pfad, data=body, headers=kopf, method=methode)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers
    except Exception as e:  # noqa
        return 0, str(type(e).__name__).encode(), {}


def pruefe(name, ok, info=""):
    print(("  ok    " if ok else "  FEHLER ") + name + (("  (" + info + ")") if info else ""))
    if not ok:
        FEHLER.append(name)


def main():
    print("Prüfe " + BASIS)
    for pfad in ("/", "/impressum", "/datenschutz", "/feedback?t=x", "/geschenk", "/robots.txt", "/llms.txt",
                 "/design.css", "/erlebnis.js", "/himmel.js", "/bilder/film/so-entsteht-hoch.webp", "/bilder/wrapped-klang.mp3"):
        code, _, _ = abruf(pfad, "HEAD" if pfad.startswith("/bilder") else "GET")
        pruefe("Seite " + pfad, code == 200, str(code))

    code, body, _ = abruf("/api/subscribe")
    try:
        diag = json.loads(body)
    except Exception:  # noqa
        diag = {}
    pruefe("Anmeldung startet (GET /api/subscribe)", code == 200, str(code))
    pruefe("ActiveCampaign-Formular verbunden", bool(diag.get("ac_form_connected")))
    pruefe("ActiveCampaign-API verbunden", bool(diag.get("ac_api_configured")))
    pruefe("Telegram eingerichtet", bool(diag.get("telegram_configured")))

    code, body, _ = abruf("/api/analyze", "POST", BEISPIEL)
    try:
        res = json.loads(body)
    except Exception:  # noqa
        res = {}
    full = res.get("full") or {}
    pruefe("Berechnung (POST /api/analyze)", code == 200 and bool(res.get("ok")), str(code))
    pruefe("Bericht vollständig (Positionen, Human Design, Kapitel)",
           bool(full.get("positions")) and bool(full.get("hd")) and len(full.get("sections") or []) >= 10)

    code, _, _ = abruf("/api/bericht", "POST", {"aktion": "unbekannt"})
    pruefe("Warteliste und Frage starten (POST /api/bericht)", code == 400, str(code))
    code, _, _ = abruf("/api/hoeren", "POST", {"d": "x"})
    pruefe("Vorlesen startet (POST /api/hoeren)", code == 400, str(code))
    code, _, _ = abruf("/api/feedback", "POST", {})
    pruefe("Feedback startet (POST /api/feedback)", code in (400, 404), str(code))

    print()
    if FEHLER:
        print("NICHT IN ORDNUNG: " + ", ".join(FEHLER))
        sys.exit(1)
    print("Alles in Ordnung.")


if __name__ == "__main__":
    main()
