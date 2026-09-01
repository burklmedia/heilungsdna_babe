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
    e = os.environ
    # 1) bekannte Namenspaare (Vercel KV / Upstash direkt)
    for u, t in (("KV_REST_API_URL", "KV_REST_API_TOKEN"),
                 ("UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN")):
        if e.get(u) and e.get(t):
            return e[u], e[t]
    # 2) automatisch: eine REST-URL-Variable (https) + passender Token, egal
    #    wie das Upstash/Vercel-Integration die Variablen genau benannt hat.
    for k, v in e.items():
        ku = k.upper()
        if isinstance(v, str) and v.startswith("http") and "REST" in ku and "URL" in ku:
            prefix = ku.rsplit("URL", 1)[0].rstrip("_")
            for tk, tv in e.items():
                tku = tk.upper()
                if tv and "TOKEN" in tku and tku.startswith(prefix):
                    return v, tv
            for tk, tv in e.items():
                tku = tk.upper()
                if tv and "REST" in tku and "TOKEN" in tku:
                    return v, tv
    return None, None


def diag_names():
    """Nur Namen (keine Werte) der speicher-relevanten Variablen, fuer die
    Diagnose. Werte werden nie ausgegeben."""
    out = []
    for k in sorted(os.environ.keys()):
        ku = k.upper()
        if any(s in ku for s in ("KV", "REDIS", "UPSTASH", "STORAGE")):
            out.append(k)
    u, t = _creds()
    return {"gefundene_namen": out, "url_erkannt": bool(u), "token_erkannt": bool(t)}


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


# --- einfache Schluessel/Wert-Helfer (fuer die Feedback-Zuordnung) ---------

def kv_set(key, value, ttl=None):
    """Speichert einen einzelnen Wert, optional mit Ablauf in Sekunden.
    Rueckgabe True bei Erfolg, sonst False (z. B. kein Speicher verbunden)."""
    try:
        cmd = ["SET", key, value]
        if ttl:
            cmd += ["EX", int(ttl)]
        res = _request("", cmd)
        return res is not None
    except Exception:  # noqa
        return False


def kv_get(key):
    """Liest einen einzelnen Wert. Nicht vorhanden/Fehler -> None."""
    try:
        res = _request("", ["GET", key])
        return (res or {}).get("result")
    except Exception:  # noqa
        return None


def kv_setnx(key, value, ttl=None):
    """Setzt den Wert nur, wenn der Schluessel noch nicht existiert (atomar).
    Rueckgabe True, wenn NEU gesetzt wurde; False, wenn schon vorhanden oder
    kein Speicher verbunden ist."""
    try:
        cmd = ["SET", key, value, "NX"]
        if ttl:
            cmd += ["EX", int(ttl)]
        res = _request("", cmd)
        # Upstash: result == "OK" wenn gesetzt, None wenn bereits vorhanden
        return bool(res) and (res.get("result") == "OK")
    except Exception:  # noqa
        return False


def kv_del(key):
    """Loescht einen Schluessel (best effort)."""
    try:
        _request("", ["DEL", key])
        return True
    except Exception:  # noqa
        return False


def push_feedback(record, key="imh:feedback"):
    """Haengt einen Feedback-Datensatz (dict) als JSON an die Liste an."""
    try:
        res = _request("", ["RPUSH", key, json.dumps(record, ensure_ascii=False)])
        return res is not None
    except Exception:  # noqa
        return False


def list_feedback(key="imh:feedback"):
    """Liest alle Feedback-Datensaetze als Liste von dicts (aelteste zuerst)."""
    try:
        res = _request("", ["LRANGE", key, 0, -1])
        raw = (res or {}).get("result") or []
    except Exception:  # noqa
        raw = []
    out = []
    for item in raw:
        try:
            out.append(json.loads(item))
        except Exception:  # noqa
            pass
    return out
