# Backend/core/messaging.py
import pika
import os
from dotenv import load_dotenv
from .logger import log  # Importa nosso logger configurado

load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = "click_events_queue"

def publish_click_event(short_code: str):
    """
    Publishes a click event to the RabbitMQ queue.
    """
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=short_code,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ))
        connection.close()
        return True
    except Exception as e:
        # Substituímos o print() pelo nosso logger estruturado
        log.error(f"Failed to publish message to RabbitMQ. Error: {e}")
        return False