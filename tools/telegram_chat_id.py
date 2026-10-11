"""
Findet die Chat-ID der Telegram-Gruppe fuer die Bauplan-Meldungen.

Vorher: Bot bei @BotFather anlegen, Bot in die Gruppe aufnehmen und einmal
etwas in die Gruppe schreiben. Dann:

    python3 tools/telegram_chat_id.py

Der Token wird verdeckt abgefragt und nirgends gespeichert.
"""
import getpass
import json
import sys
import urllib.error
import urllib.request

tok = getpass.getpass("Bot-Token von @BotFather (Eingabe bleibt unsichtbar): ").strip()
if not tok:
    sys.exit("Kein Token eingegeben.")
try:
    with urllib.request.urlopen("https://api.telegram.org/bot%s/getUpdates" % tok, timeout=15) as r:
        daten = json.loads(r.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    sys.exit("Telegram lehnt den Token ab (HTTP %d). Bitte Token pruefen." % e.code)

chats = {}
for u in daten.get("result", []):
    for art in ("message", "my_chat_member", "channel_post"):
        chat = (u.get(art) or {}).get("chat")
        if chat:
            chats[chat["id"]] = (chat.get("type"), chat.get("title") or chat.get("first_name") or "")

if not chats:
    sys.exit("Noch keine Nachricht gefunden. Bot in die Gruppe aufnehmen, dort etwas schreiben und erneut starten.")
for cid, (typ, titel) in chats.items():
    print("%-14s %-11s %s" % (cid, typ, titel))
print("\nFuer die Gruppe die (negative) Zahl der Zeile mit Typ group oder supergroup nehmen.")
