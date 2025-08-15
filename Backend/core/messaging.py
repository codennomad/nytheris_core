# Backend/core/messaging.py
import pika
import os
from dotenv import load_dotenv
from .logger import log

load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

def publish_message(exchange_name: str, message: str):
    """
    Publishes a message to a fanout exchange in RabbitMQ.
    """
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        # MUDANÇA: Declaramos o exchange do tipo 'fanout'
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        
        # MUDANÇA: Publicamos no exchange, sem routing_key específica
        channel.basic_publish(
            exchange=exchange_name,
            routing_key='', # Fanout ignora a routing key
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        log.error(f"Failed to publish to RabbitMQ exchange '{exchange_name}'. Error: {e}")
        return False