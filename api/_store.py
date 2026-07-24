"""
Winziger Speicher-Helfer fuer die eigene Besucher-Statistik.

Nutzt einen kostenlosen Upstash-Redis (bzw. Vercel KV, das dieselben
Umgebungsvariablen setzt) ueber die HTTP-REST-Schnittstelle. Keine zusaetzliche
Bibliothek noetig, nur urllib. Ohne konfigurierten Speicher machen die
Funktionen nichts (die Seite laeuft trotzdem, es werden nur keine Zahlen
gezaehlt).

Erwartete Umgebungsvariablen (eine der beiden Paare):
  KV_REST_API_URL         / KV_REST_API_TOKEN            (Vercel KV / Upstash)
  UPSTASH_REDIS_REST_URL  / UPSTASH_REDIS_REST_TOKEN     (Upstash direkt)
"""
import os
import json
import urllib.request


def _creds():
    url = os.environ.get("KV_REST_API_URL") or os.environ.get("UPSTASH_REDIS_REST_URL")
    tok = os.environ.get("KV_REST_API_TOKEN") or os.environ.get("UPSTASH_REDIS_REST_TOKEN")
    return url, tok


def configured():
    url, tok = _creds()
    return bool(url and tok)


def _request(path, payload):
    url, tok = _creds()
    if not (url and tok):
        return None
    req = urllib.request.Request(
        url.rstrip("/") + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + tok,
                 "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def incr(keys):
    """Erhoeht mehrere Zaehler in einem Rutsch (Redis-Pipeline)."""
    if not keys:
        return
    try:
        _request("/pipeline", [["INCR", k] for k in keys])
    except Exception:  # noqa
        pass


def mget(keys):
    """Liest mehrere Zaehler. Fehlende oder Fehler -> 0."""
    if not keys:
        return []
    try:
        res = _request("", ["MGET", *keys])
        vals = (res or {}).get("result") or []
    except Exception:  # noqa
        vals = []
    out = []
    for i in range(len(keys)):
        v = vals[i] if i < len(vals) else None
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            out.append(0)
    return out
