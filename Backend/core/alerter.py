# Backend/core/alerter.py
import json
from .logger import log
from .messaging import publish_message

ALERT_EXCHANGE_NAME = "alerts_exchange" # MUDANÇA: Usaremos um exchange

def send_alert(title: str, message: str, level: str = "INFO"):
    """
    Publishes an alert event to the alerts_exchange for all bots to consume.
    """
    try:
        log.info(f"Publishing alert to exchange '{ALERT_EXCHANGE_NAME}': [{level}] {title}")
        alert_payload = { "title": title, "message": message, "level": level }
        
        # MUDANÇA: Publicamos no exchange
        publish_message(exchange_name=ALERT_EXCHANGE_NAME, message=json.dumps(alert_payload))
    except Exception as e:
        log.error(f"Failed to publish alert to RabbitMQ exchange. Error: {e}")