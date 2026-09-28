"""
Herkunft: ueber welchen Weg Menschen zum Bauplan kommen (seit 28.09.2026, wie beim MUSTER-Test).

Kurzlinks fuer Instagram (bauplan.intuitionmitherz.de/story, /kommentar, /bio, /dm) zaehlen den Aufruf
und leiten mit ?q=<kanal> weiter. Die Seite gibt den Kanal mit der Anmeldung zurueck; die Anmeldung
schreibt ihn in das ActiveCampaign-Feld "Herkunft" (ID 8, gilt fuer alle Listen) und zaehlt sie.

Gespeichert wird je Ereignis nur Art, Kanal und Zeitpunkt, in der Liste imh:herkunft der KV. Keine Namen,
keine Adressen, keine IP, kein Cookie. Bots und Link-Vorschauen zaehlen nicht.
"""
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from _store import push_feedback, list_feedback, mget
except Exception:  # noqa
    def push_feedback(record, key=None):
        return False

    def list_feedback(key=None):
        return []

    def mget(keys):
        return [0] * len(keys)

# Die Schritte, die api/track.py je Sitzung zaehlt (imh:t:<schritt>), fuer den Funnel im Dashboard.
SCHRITTE = ("visit", "himmel", "teaser", "email", "bauplan", "scroll", "pdf")


def schritte():
    """Summen je Schritt seit Beginn der Zaehlung, {schritt: zahl}."""
    try:
        werte = mget(["imh:t:" + s for s in SCHRITTE])
        return {s: int(w or 0) for s, w in zip(SCHRITTE, werte)}
    except Exception:  # noqa
        return {}

# Eigene Geraete zaehlen nicht mit (seit 29.09.2026): Wer einmal /?intern=1 oeffnet, bekommt das Cookie
# imh_intern=1. Das setzt nur, wer es selbst aufruft (Tobias, Denise); Besucherinnen bekommen kein Cookie.
INTERN_COOKIE = "imh_intern=1"


def ist_intern(cookie_header):
    return bool(cookie_header) and INTERN_COOKIE in str(cookie_header).replace(" ", "").split(";")


# Ab hier zaehlen die Schritte im Dashboard (Tobias, 28.09.2026): davor stecken Tests und die MailerLite-Zeit drin.
STICHTAG = "2026-09-29"


def schritte_tage(heute=None):
    """Je Tag (UTC) ab STICHTAG die Summen je Schritt aus imh:d:<tag>:<schritt>, {tag: {schritt: zahl}}."""
    from datetime import date, timedelta
    try:
        ende = heute or datetime.now(timezone.utc).date()
        tag = date.fromisoformat(STICHTAG)
        tage = []
        while tag <= ende and len(tage) < 400:
            tage.append(tag.isoformat())
            tag += timedelta(days=1)
        if not tage:
            return {}
        schluessel = ["imh:d:%s:%s" % (t, s) for t in tage for s in SCHRITTE]
        werte = mget(schluessel)
        out = {}
        for k, w in zip(schluessel, werte):
            _, _, t, s = k.split(":")
            if int(w or 0):
                out.setdefault(t, {})[s] = int(w)
        return out
    except Exception:  # noqa
        return {}


LISTE = "imh:herkunft"
# Die Kurzlinks. Weitere Kanaele (Mails, Seiten) duerfen als ?q= ankommen, wenn sie dem Muster folgen.
KURZLINKS = ("story", "kommentar", "bio", "dm")
_KANAL = re.compile(r"^[a-z0-9][a-z0-9-]{0,23}$")
_BOT = re.compile(r"bot|crawl|spider|preview|facebookexternalhit|facebot|whatsapp|telegram|slack|discord|"
                  r"skype|linkedin|embedly|curl|wget|python-requests|headless", re.I)
FIELD_HERKUNFT = "8"


def kanal(wert):
    """Ein gueltiger Kanal oder None."""
    if not isinstance(wert, str):
        return None
    w = wert.strip().lower()[:24]
    return w if _KANAL.match(w) else None


def ist_bot(user_agent):
    return not user_agent or bool(_BOT.search(user_agent))


def merken(art, k):
    """Haengt ein Ereignis an. art: klick oder anmeldung. Best effort, nie eine Ausnahme."""
    if art not in ("klick", "anmeldung") or not kanal(k):
        return False
    zeit = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        return push_feedback({"a": art, "k": kanal(k), "t": zeit}, key=LISTE)
    except Exception:  # noqa
        return False


def ereignisse():
    """Alle Ereignisse, aelteste zuerst: [{a, k, t}]."""
    out = []
    for e in list_feedback(key=LISTE):
        if isinstance(e, dict) and e.get("a") in ("klick", "anmeldung") and kanal(e.get("k")) and isinstance(e.get("t"), str):
            out.append({"a": e["a"], "k": e["k"], "t": e["t"]})
    return out
