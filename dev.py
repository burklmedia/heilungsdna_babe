#!/usr/bin/env python3
"""
Lokaler Dev-Server für Intuition mit Herz.
Bedient — genau wie Vercel — das Frontend aus public/ und die API aus api/.

Starten:
    python3 dev.py
Dann im Browser öffnen:
    http://localhost:8000

Mindestens benötigt: pip install pyswisseph
Für den Städte-Fallback zusätzlich: pip install timezonefinder geonamescache
(Der Normalweg über das Städte-Autocomplete braucht die beiden nicht.)
"""
import json
import os
import sys
import mimetypes
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(BASE, "public")
sys.path.insert(0, os.path.join(BASE, "api"))

from analyze import build_result  # noqa: E402

try:
    from pdf import build_pdf as _build_pdf, _decode as _pdf_decode, _filename as _pdf_filename  # noqa: E402
except Exception:  # noqa
    _build_pdf = None

try:
    import subscribe as _subscribe  # noqa: E402
    # Lokal geht standardmaessig nichts an ActiveCampaign. Wer die echte
    # Anmeldung samt Bestaetigungsmail testen will: BAUPLAN_AC_LIVE=1 python3 dev.py
    _subscribe.DRY_RUN = os.environ.get("BAUPLAN_AC_LIVE") != "1"
except Exception:  # noqa
    _subscribe = None

PORT = int(os.environ.get("PORT", "8000"))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/api/track"):
            self.send_response(204); self.end_headers(); return
        if self.path.startswith("/api/feedback"):
            return self._feedback_ansicht()
        if self.path.startswith("/api/stats"):
            return self._stats()
        if self.path.startswith("/api/pdf"):
            return self._pdf()
        path = self.path.split("?")[0]
        if path in ("/", ""):
            path = "/index.html"
        elif "." not in path.rsplit("/", 1)[-1] and os.path.isfile(os.path.join(PUBLIC, path.strip("/") + ".html")):
            path = path.rstrip("/") + ".html"   # wie die Vercel-Routen /lebenszahl, /impressum …
        fp = os.path.normpath(os.path.join(PUBLIC, path.lstrip("/")))
        if not fp.startswith(PUBLIC) or not os.path.isfile(fp):
            return self._json(404, {"error": "not found"})
        ctype = mimetypes.guess_type(fp)[0] or "application/octet-stream"
        data = open(fp, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if "text" in ctype or "html" in ctype else ""))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _pdf(self):
        if _build_pdf is None:
            return self._json(500, {"ok": False, "error": "PDF-Modul nicht geladen (fpdf2 installiert?)"})
        try:
            d = (parse_qs(urlparse(self.path).query).get("d") or [""])[0]
            if not d:
                return self._json(400, {"ok": False, "error": "Kein Parameter d."})
            result = build_result(_pdf_decode(d))
            data = _build_pdf(result)
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition",
                             'inline; filename="%s"' % _pdf_filename(result["birth"].get("name")))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except ValueError as e:
            self._json(400, {"ok": False, "error": str(e)})
        except Exception as e:  # noqa
            self._json(500, {"ok": False, "error": "PDF fehlgeschlagen.", "detail": str(e)})

    def _stats(self):
        try:
            import stats as S
            html = S._dashboard() if os.environ.get("STATS_PASSWORD") else S._html(
                "<h1>Statistik</h1><div class=warn>Lokal kein Passwort/Speicher gesetzt.</div>")
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:  # noqa
            self._json(500, {"error": str(e)})

    def _feedback_modul(self):
        # Lokal: alles nur im Arbeitsspeicher, nichts an ActiveCampaign, keine KV, kein Telegram.
        import feedback as _fb
        sp = Handler.__dict__.get("_fb_speicher") or {"kv": {}, "listen": {}, "zaehler": {}}
        Handler._fb_speicher = sp
        _fb.kv_get = lambda k: sp["kv"].get(k)
        _fb.kv_setnx = lambda k, v, ttl=None: (k not in sp["kv"]) and (sp["kv"].__setitem__(k, v) or True)
        _fb.kv_del = lambda k: sp["kv"].pop(k, None) or True
        _fb.kv_incr_ttl = lambda k, ttl: 1
        _fb.incr = lambda keys: [sp["zaehler"].__setitem__(k, sp["zaehler"].get(k, 0) + 1) for k in keys]
        _fb.mget = lambda keys: [sp["zaehler"].get(k, 0) for k in keys]
        _fb.push_feedback = lambda r, key="imh:feedback": sp["listen"].setdefault(key, []).append(r) or True
        _fb.list_feedback = lambda key="imh:feedback": list(sp["listen"].get(key, []))
        _fb.configured = lambda: True
        _fb.update_contact = lambda email, fields: (False, "lokal")
        _fb.telegram = None
        return _fb

    def _feedback_ansicht(self):
        html = self._feedback_modul()._viewer().encode("utf-8")
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html))); self.end_headers(); self.wfile.write(html)

    def do_OPTIONS(self):
        self._json(204, {})

    def do_POST(self):
        if self.path.startswith("/api/track"):
            self.send_response(204); self.end_headers(); return
        length = int(self.headers.get("content-length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json(400, {"ok": False, "error": "ungültige Anfrage"})

        if self.path.startswith("/api/analyze"):
            try:
                self._json(200, build_result(body))
            except ValueError as e:
                self._json(400, {"ok": False, "error": str(e)})
            except Exception as e:  # noqa
                self._json(500, {"ok": False, "error": "Berechnung fehlgeschlagen.", "detail": str(e)})
        elif self.path.startswith("/api/subscribe"):
            if _subscribe is None:
                return self._json(500, {"ok": False, "stored": False, "error": "subscribe nicht geladen"})
            code, payload = _subscribe.handle_subscribe(body if isinstance(body, dict) else {})
            if payload.get("dry_run"):
                print("  ✉  Anmeldung lokal angenommen, nicht an ActiveCampaign gesendet")
            self._json(code, payload)
        elif self.path.startswith("/api/hoeren"):
            # Lokal nur mit ELEVENLABS_API_KEY in der Umgebung (kostet Credits), sonst 503 wie live ohne Schlüssel.
            import hoeren as _hoeren
            code, art, daten = _hoeren.handle(body if isinstance(body, dict) else {}, "127.0.0.1")
            self.send_response(code); self.send_header("Content-Type", art); self.send_header("Content-Length", str(len(daten))); self.end_headers(); self.wfile.write(daten)
        elif self.path.startswith("/api/feedback"):
            _fb = self._feedback_modul()
            art = body.get("art") if isinstance(body, dict) else ""
            if art == "kapitel":
                code, payload = _fb.handle_kapitel(body, "127.0.0.1", False)
            elif art == "bauplan":
                code, payload = _fb.handle_rueckmeldung(body, "127.0.0.1", False)
            else:
                code, payload = _fb.handle_feedback(body if isinstance(body, dict) else {})
            print("  ✦  /api/feedback lokal:", art or "mail3", code)
            self._json(code, payload)
        elif self.path.startswith("/api/bericht"):
            # Lokal nur eine Probe-Antwort: nichts an ActiveCampaign, nichts in die KV, kein Telegram.
            aktion = (body or {}).get("aktion") if isinstance(body, dict) else ""
            if aktion == "stand":
                # Stand lokal im Arbeitsspeicher abgleichen (wie live, nur ohne KV)
                import bericht as _bericht
                _speicher = Handler.__dict__.get("_stand_speicher") or {}
                Handler._stand_speicher = _speicher
                _bericht.kv_get = lambda k: _speicher.get(k)
                _bericht.kv_set = lambda k, v, ttl=None: _speicher.__setitem__(k, v) or True
                _bericht.kv_incr_ttl = lambda k, ttl: 1
                code, payload = _bericht.handle(body, "127.0.0.1")
                self._json(code, payload)
                return
            print("  ✦  /api/bericht lokal angenommen:", aktion)
            self._json(200 if aktion in ("warteliste", "frage") else 400, {"ok": aktion in ("warteliste", "frage"), "dry_run": True})
        else:
            self._json(404, {"error": "no route"})


def main():
    port = PORT
    for _ in range(10):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            port += 1
    else:
        print("Konnte keinen freien Port finden.")
        return
    print("\n  ✦  Intuition mit Herz — lokaler Dev-Server läuft")
    print(f"  →  Öffne im Browser:  http://localhost:{port}\n")
    print("  (Beenden mit Strg+C)\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server gestoppt. Bis bald 🤍\n")


if __name__ == "__main__":
    main()
