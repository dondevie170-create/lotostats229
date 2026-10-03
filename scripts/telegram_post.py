"""
Publie automatiquement la tendance du jour sur le canal Telegram,
via l'API Bot Telegram (gratuite).

Configuration requise (variables d'environnement, à définir comme
"secrets" dans GitHub Actions) :
  TELEGRAM_BOT_TOKEN  -> token obtenu via @BotFather
  TELEGRAM_CHAT_ID    -> identifiant du canal (ex: @lotostats229 ou -100xxxxxxxxxx)

Comment créer le bot (à faire une seule fois, manuellement) :
  1. Ouvrir Telegram, chercher "@BotFather"
  2. Envoyer /newbot, suivre les instructions -> récupérer le token
  3. Ajouter le bot comme administrateur du canal LotoStats229
  4. Pour le chat_id : si le canal est public, c'est "@lotostats229"
     (son nom d'utilisateur) ; sinon il faut le récupérer via l'API
     getUpdates après avoir posté un message dans le canal.
"""

import json
import os
import sys
from pathlib import Path

import requests

TENDANCES_FILE = Path(__file__).parent.parent / "data" / "tendances.json"


def build_message(t: dict) -> str:
    dernier = t["dernier_tirage"]
    nums = " · ".join(str(n) for n in dernier["numeros"])
    tendance = " · ".join(str(n) for n in t["a_surveiller"])
    ecarts = " · ".join(f'{e["numero"]} ({e["ecart"]})' for e in t["numeros_en_retard"][:3])
    duos = " · ".join(f'{d["paire"][0]}-{d["paire"][1]}' for d in t["duos_frequents"][:2])
    trios = " · ".join("-".join(map(str, tr["trio"])) for tr in t["trios_frequents"][:1])

    doubles_note = ""
    if t.get("doubles_actifs"):
        doubles_note = f"\n🔁 Règle des doubles activée ({', '.join(map(str, t['doubles_actifs']))} sorti)"

    return (
        f"🎱 LotoStats229 — Tendances du jour\n\n"
        f"Dernier tirage ({dernier['type']} {dernier['heure']}) : {nums}\n"
        f"{doubles_note}\n"
        f"📊 À surveiller\n{tendance}\n\n"
        f"⏳ En retard\n{ecarts}\n\n"
        f"🔗 2 Nap tendance : {duos}\n"
        f"🔗 3 Nap tendance : {trios}\n\n"
        f"ℹ️ Statistiques historiques — chaque numéro garde 5,6% de chance "
        f"à chaque tirage. Jouez avec modération, 18 ans et plus."
    )


def send(message: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID manquant — message non envoyé.", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=15)
    if not resp.ok:
        print(f"Erreur Telegram : {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)
    print("Message envoyé sur Telegram.")


if __name__ == "__main__":
    tendances = json.loads(TENDANCES_FILE.read_text())
    msg = build_message(tendances)
    print(msg)
    send(msg)
