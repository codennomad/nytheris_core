import pika
import os
import time
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from Backend.core.database import SessionLocal
from Backend.models.models import URL
from Backend.core.logger import log 

load_dotenv()
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = "click_events_queue"

def get_db_session():
    """Generates a database session for the worker."""
    return SessionLocal()

def process_click_event(ch, method, properties, body):
    """
    Callback function executed for each message received from the queue.
    """
    short_code = body.decode()
    log.info(f"Received click event for: '{short_code}'")

    db: Session = get_db_session()
    try:
        db_url = db.query(URL).filter(URL.short_code == short_code).first()
        if db_url:
            db_url.current_clicks += 1
            db.commit()
            log.info(f"Database updated for '{short_code}'. Clicks: {db_url.current_clicks}")
        else:
            log.warning(f"Short code '{short_code}' not found in DB.")
        
        # Acknowledge the message has been successfully processed.
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        log.error(f"Failed to process message for '{short_code}'. Error: {e}")
        db.rollback()
    finally:
        db.close()

def connect_and_consume():
    """Connects to RabbitMQ and starts consuming messages with a retry mechanism."""
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            
            # durable=True ensures that the queue will survive a RabbitMQ restart.
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            
            # Set up the subscription on the queue
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_click_event)
            
            log.info('Worker is waiting for click events. To exit press CTRL+C')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            log.error(f"Could not connect to RabbitMQ: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            log.info("Worker consumer interrupted by user.")
            break
        except Exception as e:
            log.critical(f"An unrecoverable error occurred in the worker: {e}")
            break

if __name__ == '__main__':
    connect_and_consume()