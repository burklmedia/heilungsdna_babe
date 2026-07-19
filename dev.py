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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(BASE, "public")
sys.path.insert(0, os.path.join(BASE, "api"))

from analyze import build_result  # noqa: E402

try:
    from subscribe import subscribe_contact  # noqa: E402
except Exception:  # noqa
    def subscribe_contact(name, email):
        return False, "kein Dienst verbunden"

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
        path = "/index.html" if self.path in ("/", "") else self.path.split("?")[0]
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

    def do_OPTIONS(self):
        self._json(204, {})

    def do_POST(self):
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
            email = (body.get("email") or "").strip()
            if "@" not in email or "." not in email:
                return self._json(400, {"ok": False, "error": "Bitte gib eine gültige E-Mail an."})
            ok, msg = subscribe_contact((body.get("name") or "").strip(), email)
            print(f"  ✉  E-Mail erfasst: {email}  ({msg})")
            self._json(200, {"ok": True, "stored": ok, "message": msg})
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
