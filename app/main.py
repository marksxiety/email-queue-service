from fastapi import FastAPI
from app.config import config, jinja_env
import uvicorn
from pydantic import BaseModel, field_validator
from typing import Dict, Any
from app.utils.database_connect import connect
from app.utils.logger import print_logging
import json

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
        """
        cursor = conn.cursor()
        email_data_json = json.dumps(payload.email_data) # parse the email data to json
        cursor.execute(query, (
            payload.sender,
            payload.email_type,
            payload.subject,
            payload.email_template,
            email_data_json,
            payload.priority_level
        ))
        conn.commit()
        return True

    except Exception as e:
        print_logging("error", f"Error inserting in email queues: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        conn.close()

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
    result = insert_email_queues(payload)
    if result:
        return {
            "message": "Payload received successfully",
            "data": payload.model_dump()
        }
    else:
        return {
            "message": "Failed to register  the request into email queue",
            "data": None
        }
    
if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)