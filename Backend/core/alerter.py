# Backend/core/alerter.py
import os
import httpx
from dotenv import load_dotenv
from .logger import log

load_dotenv()

# Carrega as credenciais de ambos os serviços
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def _send_to_telegram(message: str):
    """Sends a message to the configured Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        with httpx.Client() as client:
            client.post(api_url, json=payload)
    except Exception as e:
        log.error(f"Failed to send Telegram alert: {e}")

def _send_to_discord(title: str, message: str, level: str):
    """Sends a rich embedded message to the configured Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        return

    colors = {
        "INFO": 3447003,    # Azul
        "WARNING": 15105570, # Laranja
        "CRITICAL": 15158332 # Vermelho
    }
    
    payload = {
        "embeds": [{
            "title": title,
            "description": message,
            "color": colors.get(level.upper(), 0),
            "footer": { "text": "Encurtador de Links API" }
        }]
    }

    try:
        with httpx.Client() as client:
            client.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        log.error(f"Failed to send Discord alert: {e}")


def send_alert(title: str, message: str, level: str = "INFO"):
    """
    Generic alert function that sends a message to all configured services.
    """
    log.info(f"Sending alert: [{level}] {title}")
    
    telegram_message = f"*{title}*\n\n{message}"
    
    _send_to_telegram(telegram_message)
    _send_to_discord(title, message, level)