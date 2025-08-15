# telegram_bot.py
import os
import pika
import json
import time
import httpx
from dotenv import load_dotenv
from Backend.core.logger import log

# -- Configuração Inicial --
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
ALERT_QUEUE_NAME = "alerts_queue"
ALERT_EXCHANGE_NAME = "alerts_exchange"

def send_telegram_message(title: str, message: str):
    """Sends a formatted message to the Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram token or chat ID not configured. Skipping alert.")
        return
    
    # Formata a mensagem para o Telegram
    telegram_message = f"*{title}*\n\n{message}"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": telegram_message, "parse_mode": "Markdown"}
    
    try:
        with httpx.Client() as client:
            response = client.post(api_url, json=payload)
            if response.status_code != 200:
                log.error(f"Failed to send Telegram alert: {response.status_code} - {response.text}")
            else:
                log.info("Successfully sent alert to Telegram.")
    except Exception as e:
        log.error(f"An exception occurred while sending Telegram alert: {e}")

def alert_consumer_thread():
    """Connects to RabbitMQ and consumes alert messages."""
    
    def process_alert_message(ch, method, properties, body):
        """Callback function to process a message from the alerts_queue."""
        try:
            data = json.loads(body.decode())
            log.info(f"Telegram Bot received alert from RabbitMQ: {data['title']}")
            send_telegram_message(title=data.get("title"), message=data.get("message"))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            log.error(f"Error processing alert message for Telegram: {e}")

    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            
            
            channel.exchange_declare(exchange=ALERT_EXCHANGE_NAME, exchange_type='fanout')
            
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
        
            channel.queue_bind(exchange=ALERT_EXCHANGE_NAME, queue=queue_name)
            
            channel.basic_consume(queue=queue_name, on_message_callback=process_alert_message)
            
            log.info(f"Alert consumer thread started, listening to exchange '{ALERT_EXCHANGE_NAME}'.")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:    
            log.error(f"Telegram Bot could not connect to RabbitMQ: {e}. Retrying...")
            time.sleep(5)
        except KeyboardInterrupt:
            log.info("Telegram Bot consumer interrupted.")
            break

if __name__ == '__main__':
    print("Starting Telegram Bot consumer...")
    alert_consumer_thread()