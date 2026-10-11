"""
Meldung in Telegram bei jeder Bauplan-Anmeldung (seit 11.10.2026).

Ein Bot schreibt in die Gruppe von Tobias und Denise, sobald jemand auf der Seite
die E-Mail eingetragen hat. Die Nachricht enthaelt keine Daten der Person (kein
Name, keine E-Mail), es geht also nur das "dass" an Telegram.

Erwartete Umgebungsvariablen (in Vercel, nie im Repo):
  TELEGRAM_BOT_TOKEN   Token von @BotFather
  TELEGRAM_CHAT_ID     Chat-ID der Gruppe (tools/telegram_chat_id.py)
Fehlt eins, tut melden() nichts. Ein Fehler bei Telegram bricht nie die Anmeldung ab.
"""
import json
import os
import urllib.request


def _creds():
    tok = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    return tok, chat


def configured():
    tok, chat = _creds()
    return bool(tok and chat)


def melden(text):
    tok, chat = _creds()
    if not (tok and chat):
        return False
    try:
        req = urllib.request.Request(
            "https://api.telegram.org/bot%s/sendMessage" % tok,
            data=json.dumps({"chat_id": chat, "text": text}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=4) as r:
            return 200 <= r.status < 300
    except Exception as e:  # noqa
        # Nur der Fehlertyp, nie die Adresse: darin steckt der Token.
        print("[telegram] fehlgeschlagen", type(e).__name__)
        return False
