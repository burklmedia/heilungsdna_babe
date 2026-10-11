"""
Vercel Serverless Function: POST /api/hoeren  {"d": "<Bauplan-Parameter>"}  (seit 11.10.2026)

Liest den Kosmischen Bauplan in rund zwei Minuten vor: Der Sprechtext entsteht aus den Texten,
die schon im Bericht stehen (Sonne, Mond, Aszendent, Human Design, Lebenszahl, Intuitionstyp,
Schlusssatz), gesprochen von Lea (ElevenLabs, eleven_v4). Antwort ist eine MP3.

Kosten bleiben gedeckelt: je Geraet (Hash der IP) hoechstens 3 Aufnahmen am Tag, insgesamt
hoechstens HOEREN_TAGESLIMIT (Standard 150). Das Handy speichert die fertige Aufnahme selbst.
Umgebungsvariable: ELEVENLABS_API_KEY (in Vercel, nie im Repo).
Im Log stehen nie Namen, Geburtsdaten oder der Schluessel.
"""
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone
import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import kv_incr_ttl
except Exception:  # noqa
    def kv_incr_ttl(k, ttl):
        return None

LEA = "M39iqBUcu1jyiwM5PfSy"
MODELL = "eleven_v4"
PRO_GERAET = 3
_D = re.compile(r"^[A-Za-z0-9_-]{20,1200}$")
IM = ["im Widder", "im Stier", "in den Zwillingen", "im Krebs", "im Löwen", "in der Jungfrau", "in der Waage",
      "im Skorpion", "im Schützen", "im Steinbock", "im Wassermann", "in den Fischen"]
ZEICHEN = ["Widder", "Stier", "Zwillinge", "Krebs", "Löwe", "Jungfrau", "Waage", "Skorpion", "Schütze",
           "Steinbock", "Wassermann", "Fische"]
ZAHLWORT = {1: "Eins", 2: "Zwei", 3: "Drei", 4: "Vier", 5: "Fünf", 6: "Sechs", 7: "Sieben", 8: "Acht", 9: "Neun",
            11: "Elf", 22: "Zweiundzwanzig", 33: "Dreiunddreißig"}
ZIFFER = {"1": "eins", "2": "zwei", "3": "drei", "4": "vier", "5": "fünf", "6": "sechs"}


def _decode(d):
    d = d.replace("-", "+").replace("_", "/")
    d += "=" * (-len(d) % 4)
    return json.loads(base64.b64decode(d).decode("utf-8"))


def _klein(titel):
    """„Der Weg der Tiefe“ mitten im Satz: Artikel am Anfang klein."""
    t = str(titel or "").strip()
    return re.sub(r"^(Der|Die|Das) ", lambda m: m.group(1).lower() + " ", t)


def _saetze(text, ab=0, anzahl=1):
    s = [x.strip() for x in re.findall(r"[^.!?]+[.!?]+", str(text or ""))]
    s = [x for x in s[ab:] if not re.match(r"(Vielleicht|Manchmal|Stell dir vor)\b", x)]
    return " ".join(s[:anzahl])


def sprechtext(full, name=""):
    by = {p.get("key"): p for p in (full.get("positions") or [])}
    teile = []
    teile.append(("Hallo " + name + ". " if name else "") +
                 "Hier ist dein Kosmischer Bauplan, vorgelesen in rund zwei Minuten. Mach es dir bequem.")
    for key, satz in (("Sonne", "Deine Sonne steht {im}."), ("Mond", "Dein Mond steht {im}."), ("AC", "Dein Aszendent steht {im}.")):
        p = by.get(key)
        if not p or p.get("sign") not in ZEICHEN:
            continue
        teile.append(satz.format(im=IM[ZEICHEN.index(p["sign"])]) + " " + _saetze(p.get("desc"), 1, 2 if key == "Sonne" else 1))
    hd = full.get("hd") or {}
    if hd.get("type_display") or hd.get("type"):
        profil = " ".join(ZIFFER.get(z, z) for z in str(hd.get("profile") or "").split("/") if z)
        satz = "In deinem Human Design bist du " + (hd.get("type_display") or hd.get("type")) + (", mit dem Profil " + profil if profil else "") + "."
        if hd.get("authority"):
            a = str(hd["authority"])
            satz += " Deine Entscheidungen kommen über deine " + a[:1].lower() + a[1:] + "."
        teile.append(satz)
    num = full.get("numerology") or {}
    if num.get("lifepath"):
        n = int(num["lifepath"])
        teile.append("Deine Lebenszahl ist die " + ZAHLWORT.get(n, str(n)) + ", " + _klein(num.get("title")) + ". " + _saetze(num.get("text"), 1, 2))
    it = full.get("intuition") or {}
    if it.get("archetype"):
        teile.append("Dein Intuitionstyp ist " + _klein(it["archetype"]) + (", " + it["tagline"] if it.get("tagline") else "") + ".")
    schluss = re.sub(r"[^\w\s.,:;!?äöüÄÖÜß'„“\"()-]", "", str(full.get("closing") or "")).strip()
    if schluss:
        teile.append(schluss)
    teile.append("Alles Weitere findest du in deinem Bauplan. Lies dort weiter, wo es dich gerade hinzieht.")
    text = "\n\n".join(t.strip() for t in teile if t.strip())
    return re.sub(r"[ \t]+", " ", text)


def _ueber_grenze(ip):
    h = hashlib.sha256(("imh-hoeren|" + (ip or "")).encode("utf-8")).hexdigest()[:20]
    tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    n = kv_incr_ttl("imh:rl:hoeren:" + tag + ":" + h, 2 * 86400)
    if isinstance(n, int) and n > PRO_GERAET:
        return "geraet"
    g = kv_incr_ttl("imh:hoeren:" + tag, 3 * 86400)
    limit = int(os.environ.get("HOEREN_TAGESLIMIT", "150") or 150)
    if isinstance(g, int) and g > limit:
        return "tag"
    return None


def tts(text):
    key = (os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    if not key:
        return None, "nicht_konfiguriert"
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/text-to-speech/" + LEA + "?output_format=mp3_44100_64",
        data=json.dumps({"text": text, "model_id": MODELL, "language_code": "de"}).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=55) as r:
            return r.read(), None
    except urllib.error.HTTPError as e:
        print("[hoeren] ElevenLabs lehnt ab", e.code)
        return None, "http_%d" % e.code
    except Exception as e:  # noqa
        print("[hoeren] ElevenLabs nicht erreichbar", type(e).__name__)
        return None, "netz"


def handle(body, ip=""):
    """Rueckgabe (code, content_type, bytes)."""
    d = body.get("d") if isinstance(body.get("d"), str) else ""
    if not _D.match(d.strip()):
        return 400, "application/json", json.dumps({"ok": False, "error": "bad_request"}).encode()
    try:
        birth = _decode(d.strip())
        from analyze import build_result
        full = (build_result(birth) or {}).get("full") or {}
    except Exception as e:  # noqa
        print("[hoeren] Bauplan nicht berechenbar", type(e).__name__)
        return 400, "application/json", json.dumps({"ok": False, "error": "bad_data"}).encode()
    grenze = _ueber_grenze(ip)
    if grenze:
        msg = ("Für heute hast du deinen Bauplan schon oft angehört. Morgen geht es wieder." if grenze == "geraet"
               else "Heute wurde der Bauplan schon sehr oft angehört. Bitte versuch es morgen noch einmal.")
        return 429, "application/json", json.dumps({"ok": False, "error": "limit", "message": msg}, ensure_ascii=False).encode("utf-8")
    audio, fehler = tts(sprechtext(full, str(birth.get("name") or "").strip()[:40]))
    if not audio:
        return 503, "application/json", json.dumps({"ok": False, "error": fehler or "tts",
                                                    "message": "Das Vorlesen klappt gerade nicht. Bitte versuch es später noch einmal."},
                                                   ensure_ascii=False).encode("utf-8")
    return 200, "audio/mpeg", audio


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = min(int(self.headers.get("content-length", 0)), 4096)
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                body = {}
            ip = (self.headers.get("x-forwarded-for") or "").split(",")[0].strip()
            code, art, daten = handle(body, ip)
        except Exception as e:  # noqa
            print("[hoeren] Fehler", type(e).__name__)
            code, art, daten = 500, "application/json", b'{"ok": false}'
        self.send_response(code)
        self.send_header("Content-Type", art)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(daten)))
        self.end_headers()
        self.wfile.write(daten)
