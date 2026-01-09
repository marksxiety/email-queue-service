import json
import pika
from app.config import config
from app.utils.logger import print_logging


def publish_to_rabbitmq(email_data, priority_level):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT,
            virtual_host=config.RABBITMQ_VHOST,
            credentials=pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
        ))
        channel = connection.channel()
        
        if priority_level == 1:
            queue_name = config.EMAIL_QUEUE_HIGH
        elif priority_level == 2:
            queue_name = config.EMAIL_QUEUE_NORMAL
        else:
            queue_name = config.EMAIL_QUEUE_LOW
            
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(email_data),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        connection.close()
        return True
    except Exception as e:
        print_logging("error", f"Error publishing to RabbitMQ: {str(e)}")
        return False
