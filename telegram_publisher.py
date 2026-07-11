# -*- coding: utf-8 -*-
"""
Pubblicazione messaggi sul canale Telegram tramite Bot API (gratuita).

Richiede due variabili d'ambiente (impostate come GitHub Secrets in produzione):
  - TELEGRAM_BOT_TOKEN : token ottenuto da @BotFather
  - TELEGRAM_CHANNEL_ID : es. "@nome_canale" oppure "-1001234567890"
"""

import os
import time

import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def pubblica(titolo: str, riassunto: str, link: str, fonte: str) -> bool:
    """Pubblica una notizia sul canale. Ritorna True se l'invio ha successo."""
    if not BOT_TOKEN or not CHANNEL_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID mancanti nelle variabili d'ambiente."
        )

    testo = f"✈️ *{titolo}*\n\n{riassunto}\n\n🔗 [Fonte: {fonte}]({link})"

    payload = {
        "chat_id": CHANNEL_ID,
        "text": testo,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }

    risposta = requests.post(API_URL, data=payload, timeout=15)

    if risposta.status_code != 200:
        print(f"[telegram] errore invio: {risposta.status_code} {risposta.text}")
        return False

    # piccola pausa di cortesia tra un messaggio e l'altro
    time.sleep(2)
    return True
