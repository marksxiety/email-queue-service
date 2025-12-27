from fastapi import FastAPI
from app.config import config, jinja_env
import uvicorn
from pydantic import BaseModel, field_validator
from typing import Dict, Any
from app.database.transactions import insert_email_queues
from app.utils.logger import print_logging
import json
import pika

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