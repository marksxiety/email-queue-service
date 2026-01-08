from app.utils.logger import print_logging
from app.database.transactions import update_email_status
import pandas as pd
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from app.config import config, jinja_env
import time
import pika
        
def render_email_template(template_name, data):
    template = jinja_env.get_template(f"{template_name}.html")
    return template.render(**data)

def send_email_via_smtp(subject, body, to_address, cc_addresses=None, bcc_addresses=None):
    smtp_server = config.SMTP_HOST
    port = config.SMTP_PORT
    sender_email = config.SMTP_USER
    password = config.SMTP_PASSWORD

    sender_email = None if sender_email is None else str(sender_email)
    password = None if password is None else str(password)

    message = MIMEMultipart()
    message["From"] = sender_email

    to_list = to_address if isinstance(to_address, list) else [to_address]
    message["To"] = ", ".join([str(a) for a in to_list if a is not None])

    if cc_addresses:
        cc_list = cc_addresses if isinstance(cc_addresses, list) else [cc_addresses]
        message["Cc"] = ", ".join([str(a) for a in cc_list if a is not None])

    if bcc_addresses:
        bcc_list = bcc_addresses if isinstance(bcc_addresses, list) else [bcc_addresses]
        message["Bcc"] = ", ".join([str(a) for a in bcc_list if a is not None])

    message["Subject"] = str(subject)
    message.attach(MIMEText(body, "html"))

    all_recipients = to_list.copy()
    if cc_addresses:
        cc_list = cc_addresses if isinstance(cc_addresses, list) else [cc_addresses]
        all_recipients.extend(cc_list)
    if bcc_addresses:
        bcc_list = bcc_addresses if isinstance(bcc_addresses, list) else [bcc_addresses]
        all_recipients.extend(bcc_list)

    all_recipients = [str(a) for a in all_recipients if a is not None]

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, all_recipients, message.as_string())
        return True, "success"
    except Exception as e:
        print_logging("error", f"SMTP error: {str(e)}")
        return False, e


def parse_address_value(value):
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            import ast
            return ast.literal_eval(value)
        except:
            return [value]
    return [value]

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
        
        if isinstance(email_content, str):
            try:
                email_content = json.loads(email_content)
            except json.JSONDecodeError as e:
                print_logging("error", f"Invalid JSON for email {email_id}: {str(e)}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        
        body_content = render_email_template(template_name, email_content)
        
        success, message = send_email_via_smtp(subject, body_content, to_address, cc_addresses, bcc_addresses)
        if success:
            print_logging("info", f"Email {email_id} sent successfully!")
            update_email_status(1, email_id)
        else:
            print_logging("error", f"Failed to send email {email_id} due to: {message}")
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
        
if __name__ == "__main__":
    initialize_worker()
