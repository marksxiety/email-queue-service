import json
import pika
import time
from app.config import config
from app.utils.logger import print_logging
from app.utils.email_utils import send_email_via_smtp
from app.utils.template_utils import render_email_template
from app.utils.attachment_utils import get_file_attachments
from app.utils.email_parser import parse_address_value
from app.database.transactions import update_email_status


def callback(ch, method, properties, body):
    try:
        body_str = body.decode('utf-8') if isinstance(body, bytes) else body
        email_data = json.loads(body_str)
        email_id = email_data["id"]
        template_name = email_data["email_template"]
        subject = str(email_data["subject"])
        to_address = parse_address_value(email_data["to_address"])
        cc_addresses = parse_address_value(email_data["cc_addresses"])
        bcc_addresses = parse_address_value(email_data["bcc_addresses"])
        email_content = email_data["email_data"]
        
        MAX_RETRIES = config.MAX_RETRIES
        RETRY_SLEEP = config.RETRY_DELAY_SECONDS
        CURRENT_TRY = 0
        
        if isinstance(email_content, str):
            try:
                email_content = json.loads(email_content)
            except json.JSONDecodeError as e:
                print_logging("error", f"Invalid JSON for email {email_id}: {str(e)}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
        attachments = get_file_attachments(email_id)
        body_content = render_email_template(template_name, email_content)
        
        success = False
        message = ""
        
        while CURRENT_TRY < MAX_RETRIES and not success:
            CURRENT_TRY += 1
            success, message = send_email_via_smtp(subject, body_content, to_address, cc_addresses, bcc_addresses, attachments)
            
            if success:
                print_logging("info", f"Email {email_id} sent successfully on attempt {CURRENT_TRY}/{MAX_RETRIES}!")
                update_email_status(1, email_id)
            else:
                print_logging("warning", f"Attempt {CURRENT_TRY}/{MAX_RETRIES} failed for email {email_id}: {message}")
                if CURRENT_TRY < MAX_RETRIES:
                    time.sleep(RETRY_SLEEP)
        
        if not success:
            print_logging("error", f"Failed to send email {email_id} after {MAX_RETRIES} attempts due to: {message}")
            update_email_status(2, email_id)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except json.JSONDecodeError as e:
        print_logging("error", f"Invalid JSON message format: {str(e)}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print_logging("error", f"Error processing message: {str(e)}")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def initialize_worker():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT,
            virtual_host=config.RABBITMQ_VHOST,
            credentials=pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
        ))
        channel = connection.channel()
        
        channel.queue_declare(queue=config.EMAIL_QUEUE_HIGH, durable=True)
        channel.queue_declare(queue=config.EMAIL_QUEUE_NORMAL, durable=True)
        channel.queue_declare(queue=config.EMAIL_QUEUE_LOW, durable=True)
        
        channel.basic_qos(prefetch_count=1)
        
        print_logging("info", "Worker started and listening to queues...")
        
        channel.basic_consume(queue=config.EMAIL_QUEUE_HIGH, on_message_callback=callback)
        channel.basic_consume(queue=config.EMAIL_QUEUE_NORMAL, on_message_callback=callback)
        channel.basic_consume(queue=config.EMAIL_QUEUE_LOW, on_message_callback=callback)
        
        channel.start_consuming()
    except Exception as e:
        print_logging("critical", f"Worker error: {str(e)}")
        time.sleep(5)
        initialize_worker()
