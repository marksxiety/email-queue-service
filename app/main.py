from fastapi import FastAPI
from app.config import config, jinja_env
import uvicorn
from pydantic import BaseModel, field_validator
from typing import Dict, Any
from app.utils.database_connect import connect
from app.utils.logger import print_logging
import json
import pika

def insert_email_queues(payload):
    conn = connect()
    if conn is None:
        print_logging("error", "Failed to connect to database")
        return False
    cursor = None
    try:
        query = """
           INSERT INTO email_queues (sender, email_type, subject, email_template, email_data, priority_level)
           VALUES (%s, %s, %s, %s, %s, %s)
           RETURNING id
        """
        cursor = conn.cursor()
        email_data_json = json.dumps(payload.email_data)
        cursor.execute(query, (
            payload.sender,
            payload.email_type,
            payload.subject,
            payload.email_template,
            email_data_json,
            payload.priority_level
        ))
        email_id = cursor.fetchone()[0]
        conn.commit()
        
        query = """
            SELECT et.to_address, et.cc_addresses, et.bcc_addresses
            FROM email_types et
            WHERE et.type = %s
        """
        cursor.execute(query, (payload.email_type,))
        result = cursor.fetchone()
        
        email_data = {
            "id": email_id,
            "email_type": payload.email_type,
            "subject": payload.subject,
            "email_template": payload.email_template,
            "email_data": email_data_json,
            "to_address": result[0],
            "cc_addresses": result[1],
            "bcc_addresses": result[2]
        }
        return email_data

    except Exception as e:
        print_logging("error", f"Error inserting in email queues: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        conn.close()

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

class EmailQueueRequest(BaseModel):
    sender: Any
    email_type: Any
    subject: Any
    email_template: Any
    email_data: Dict[str, Any]
    priority_level: int

    @field_validator('email_template')
    @classmethod
    def validate_template_exists(cls, v):
        template_name = v if v.endswith('.html') else f"{v}.html"
        try:
            jinja_env.get_template(template_name)
            return v
        except Exception as e:
            error_msg = f"Template '{template_name}' does not exist in templates folders: {str(e)}"
            raise ValueError(error_msg)

app = FastAPI()

@app.post("/api/v1/emails/queue")
async def queue_email(payload: EmailQueueRequest):
    email_data = insert_email_queues(payload)
    if email_data:
        published = publish_to_rabbitmq(email_data, payload.priority_level)
        if published:
            return {
                "message": "Payload received successfully",
                "data": payload.model_dump(),
                "email_id": email_data["id"]
            }
        else:
            return {
                "message": "Email inserted but failed to publish to queue",
                "data": payload.model_dump(),
                "email_id": email_data["id"]
            }
    else:
        return {
            "message": "Failed to register  the request into email queue",
            "data": None
        }
    
if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)