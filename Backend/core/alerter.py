import os 
import httpx
from dotenv import load_dotenv
from .logger import log

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_alert(message: str):
    """Sends an asynchronous alert message to a telegram chat"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram token or chat ID not configured. Skipping alert.")
        return
    
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=payload)
            if response.status_code != 200:
                log.error(f"Failed to send Telegram alert: {response.status_code} - {response.text}")
        
    except Exception as e:
        log.error(f"An exception occurred while sending Telegram alert: {e}")