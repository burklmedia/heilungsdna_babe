"""
ActiveCampaign fuer BESTEHENDE Kontakte: Feedback und Themenwahl.

Die Anmeldung selbst laeuft NICHT hierueber, sondern ueber das AC-Formular
(api/subscribe.py), weil nur das Formular den Double-Opt-in ausloest. Dieses
Modul setzt danach nur noch Felder bei Kontakten, die es schon gibt: per
E-Mail suchen, dann PUT /api/3/contacts/<id> mit fieldValues. Es legt nie
jemanden an und abonniert nichts, genau wie der Kaeufer-Webhook von
MUSTER RESET.

Umgebungsvariablen (Vercel, Production und Preview):
  AC_API_URL   https://burkl-media.api-us1.com (Einstellungen -> Entwickler)
  AC_API_KEY   der API-Schluessel von dort

Uebergang: Wer sich vor der Umstellung angemeldet hat, steht noch in
MailerLite. Findet ActiveCampaign die Adresse nicht und ist
MAILERLITE_API_KEY noch gesetzt, landet der Wert dort, aber nur bei einem
Abonnenten, den MailerLite schon kennt. Ohne den Schluessel ist dieser Weg aus.

Im Log stehen nie E-Mail, Kontakt-ID, Schluessel oder Adresse.
"""
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT = 5

# Feld-IDs im Konto burkl-media, Liste 6 "Kosmischer Bauplan · Intuition mit
# Herz". Sie aendern sich nur, wenn ein Feld geloescht und neu angelegt wird.
FIELD_BAUPLAN_PDF = "4"      # %BAUPLAN_PDF%     Parameter d fuer /mein-bauplan
FIELD_FEEDBACK_TOKEN = "5"   # %FEEDBACK_TOKEN%  Links zu /feedback und /thema
FIELD_FEEDBACK_GIVEN = "6"   # %FEEDBACK_GIVEN%  "yes" nach dem Feedback
FIELD_BETA_TOPIC = "7"       # %BETA_TOPIC%      gewaehltes Thema

# Feldnamen wie frueher bei MailerLite -> Feld-ID in ActiveCampaign.
FIELD_IDS = {
    "feedback_given": FIELD_FEEDBACK_GIVEN,
    "beta_topic": FIELD_BETA_TOPIC,
}

_HOST = re.compile(r"^[a-z0-9-]+\.(api-us\d+\.com|activehosted\.com)$", re.I)


def _log(text, code=""):
    print("[activecampaign] " + text + ((" " + code) if code else ""))


def api_base(address):
    """Nur der Ursprung einer echten ActiveCampaign-API-Adresse
    (https://<konto>.api-us1.com oder https://<konto>.activehosted.com),
    sonst None. Pfad und Schraegstrich am Ende spielen keine Rolle."""
    try:
        u = urllib.parse.urlsplit(str(address or "").strip())
        if u.scheme != "https" or u.username or u.password or u.port:
            return None
        host = u.hostname or ""
    except ValueError:
        return None
    return ("https://" + host) if _HOST.match(host) else None


def configured():
    return bool(os.environ.get("AC_API_URL", "").strip()
                and os.environ.get("AC_API_KEY", "").strip())


def _call(base, key, method, path, payload=None):
    data = None
    headers = {"Api-Token": key, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base + "/api/3" + path, data=data,
                                 headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read() or b"{}")


def set_fields(email, values):
    """Setzt Felder beim bestehenden Kontakt mit dieser E-Mail.
    values: {feld_id: wert}. Rueckgabe (ok, grund), nie eine Ausnahme.
    grund: gesetzt | kein_kontakt | nicht_konfiguriert | ungueltige_adresse
           | email | http_<status> | timeout | netz"""
    key = os.environ.get("AC_API_KEY", "").strip()
    address = os.environ.get("AC_API_URL", "").strip()
    if not key or not address:
        _log("AC_API_URL oder AC_API_KEY fehlt")
        return False, "nicht_konfiguriert"
    base = api_base(address)
    if not base:
        _log("AC_API_URL ist keine ActiveCampaign-API-Adresse")
        return False, "ungueltige_adresse"
    wanted = email.strip().lower() if isinstance(email, str) else ""
    if not wanted:
        return False, "email"
    if not values:
        return False, "keine_felder"
    try:
        found = _call(base, key, "GET",
                      "/contacts?email=" + urllib.parse.quote(wanted, safe=""))
        contact = next((c for c in (found.get("contacts") or [])
                        if isinstance(c, dict) and c.get("id")
                        and str(c.get("email") or "").strip().lower() == wanted), None)
        if not contact:
            return False, "kein_kontakt"
        _call(base, key, "PUT", "/contacts/" + str(contact["id"]),
              {"contact": {"fieldValues": [{"field": str(f), "value": str(v)}
                                           for f, v in values.items()]}})
        return True, "gesetzt"
    except urllib.error.HTTPError as e:
        _log("ActiveCampaign lehnt ab", "http_%d" % e.code)
        return False, "http_%d" % e.code
    except Exception as e:  # noqa
        # Nie str(e) loggen, Netzfehler koennen die Adresse enthalten.
        reason = getattr(e, "reason", e)
        timeout = (isinstance(reason, (socket.timeout, TimeoutError))
                   or "timed out" in str(reason).lower())
        _log("ActiveCampaign nicht erreichbar", "timeout" if timeout else type(e).__name__)
        return False, "timeout" if timeout else "netz"


def _mailerlite_existing(email, fields):
    """Uebergang: nur bei einem Abonnenten, den MailerLite schon kennt.
    Rueckgabe (ok, grund) wie set_fields."""
    key = os.environ.get("MAILERLITE_API_KEY", "").strip()
    if not key:
        return False, "nicht_konfiguriert"
    headers = {"Authorization": "Bearer " + key, "Accept": "application/json"}
    base = "https://connect.mailerlite.com/api/subscribers"
    try:
        req = urllib.request.Request(base + "/" + urllib.parse.quote(email.strip(), safe=""),
                                     headers=headers, method="GET")
        urllib.request.urlopen(req, timeout=TIMEOUT).close()
    except urllib.error.HTTPError as e:
        return False, ("kein_kontakt" if e.code == 404 else "http_%d" % e.code)
    except Exception:  # noqa
        return False, "netz"
    try:
        req = urllib.request.Request(
            base, data=json.dumps({"email": email.strip(), "fields": fields}).encode("utf-8"),
            headers=dict(headers, **{"Content-Type": "application/json"}), method="POST")
        urllib.request.urlopen(req, timeout=TIMEOUT).close()
        return True, "gesetzt"
    except urllib.error.HTTPError as e:
        return False, "http_%d" % e.code
    except Exception:  # noqa
        return False, "netz"


def update_contact(email, fields):
    """fields mit den alten Namen, z. B. {"feedback_given": "yes"}.
    Erst ActiveCampaign, bei unbekannter Adresse im Uebergang MailerLite.
    Rueckgabe (ok, wo) mit wo = activecampaign | mailerlite | <grund>."""
    values = {FIELD_IDS[k]: v for k, v in fields.items() if k in FIELD_IDS}
    ok, grund = set_fields(email, values)
    if ok:
        return True, "activecampaign"
    if grund in ("kein_kontakt", "nicht_konfiguriert"):
        ml_ok, ml_grund = _mailerlite_existing(email, fields)
        if ml_ok:
            return True, "mailerlite"
        if ml_grund != "nicht_konfiguriert":
            grund = grund + "/mailerlite_" + ml_grund
    return False, grund
