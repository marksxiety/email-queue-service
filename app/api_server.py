from fastapi import FastAPI, UploadFile, File, Form
from app.config import config, jinja_env
import uvicorn
from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional, List
from app.database.transactions import insert_email_queues, insert_email_attachments
from app.utils.logger import print_logging
import json
import pika
import hashlib
from pathlib import Path
import uuid

def calculate_sha256(file_content: bytes) -> str:
    """Calculate SHA256 checksum of file content"""
    return hashlib.sha256(file_content).hexdigest()

def save_attachment_to_disk(file_content: bytes, filename: str, email_queue_id: str) -> str:
    """
    Save attachment to disk and return the file path
    Organize files by email_queue_id to avoid conflicts
    Handles duplicate filenames by appending counter (1.pdf, 2.pdf, etc.)
    """
    # Define base upload directory
    upload_dir = Path(config.UPLOAD_DIR)
    
    # Create directory structure: uploads/email_queue_id/
    email_dir = upload_dir / str(email_queue_id)
    email_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle duplicate filenames
    file_path = email_dir / filename
    counter = 1
    
    while file_path.exists():
        name = filename.rsplit('.', 1)
        if len(name) == 2:
            base, ext = name
            new_filename = f"{base} {counter}.{ext}"
        else:
            new_filename = f"{filename} {counter}"
        
        file_path = email_dir / new_filename
        counter += 1
    
    # Write file to disk
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return str(file_path)

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

async def process_attachments(attachments: List[UploadFile], email_queue_id: str) -> int:
    """Process and save attachments, return count of successfully processed files"""
    attachment_count = 0
    
    for attachment in attachments:
        try:
            # Read file content
            file_content = await attachment.read()
            file_size = len(file_content)
            
            # Validate MIME type if config exists
            if hasattr(config, 'ALLOWED_MIME_TYPES'):
                if attachment.content_type not in config.ALLOWED_MIME_TYPES:
                    print_logging("warning", f"Skipping attachment '{attachment.filename}' with disallowed MIME type '{attachment.content_type}'")
                    continue
            
            # Calculate checksum
            checksum = calculate_sha256(file_content)
            
            # Save file to disk
            file_path = save_attachment_to_disk(
                file_content, 
                attachment.filename, 
                email_queue_id
            )
            
            # Insert attachment metadata into database
            insert_email_attachments(
                email_queue_id=email_queue_id,
                file_name=attachment.filename,
                file_path=file_path,
                mime_type=attachment.content_type,
                file_size=file_size,
                checksum=checksum
            )
            
            attachment_count += 1
            print_logging("info", f"Saved attachment: {attachment.filename} for email {email_queue_id}")
            
        except Exception as e:
            print_logging("error", f"Error processing attachment {attachment.filename}: {str(e)}")
            # Continue processing other attachments even if one fails
    
    return attachment_count

class EmailQueueRequest(BaseModel):
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

class QueueEmailResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    email_id: Optional[str] = None
    attachments_processed: Optional[int] = None

app = FastAPI()

@app.post("/api/v1/emails/queue")
async def queue_email(
    email_type: str = Form(...),
    subject: str = Form(...),
    email_template: str = Form(...),
    email_data: str = Form(...),  # This will be JSON stringified
    priority_level: int = Form(...),
    attachments: Optional[List[UploadFile]] = File(None)
) -> QueueEmailResponse:
    try:
        # Decode the JSON stringified email_data
        # Handle both regular JSON and escaped JSON strings
        email_data_dict = json.loads(email_data)

        # If the result contains an "email_data" key, extract it
        if isinstance(email_data_dict, dict) and "email_data" in email_data_dict:
            email_data_dict = email_data_dict["email_data"]

    except json.JSONDecodeError as e:
        print_logging("error", f"Invalid JSON in email_data: {str(e)}")
        return QueueEmailResponse(
            success=False,
            message="Invalid JSON format in email_data field",
            data=None
        )
    
    # Create payload
    payload_dict = {
        "email_type": email_type,
        "subject": subject,
        "email_template": email_template,
        "email_data": email_data_dict,
        "priority_level": priority_level
    }
    
    # Validate payload
    try:
        payload = EmailQueueRequest(**payload_dict)
    except Exception as e:
        print_logging("error", f"Payload validation failed: {str(e)}")
        return QueueEmailResponse(
            success=False,
            message=f"Payload validation failed: {str(e)}",
            data=None
        )

    # Insert email queue entry
    email_data = insert_email_queues(payload)

    if not email_data:
        return QueueEmailResponse(
            success=False,
            message="Failed to register the request into email queue",
            data=None
        )
    
    email_queue_id = email_data["id"]
    attachment_count = 0
    
    # Process attachments if provided (BEFORE publishing to RabbitMQ)
    if attachments:
        attachment_count = await process_attachments(attachments, email_queue_id)
    
    # Publish to RabbitMQ after attachments are processed
    published = publish_to_rabbitmq(email_data, payload.priority_level)

    if published:
        message = f"Email {email_queue_id} received and published successfully"
        success = True
    else:
        message = f"Email {email_queue_id} inserted but failed to publish to queue"
        success = False
        print_logging('critical', message)

    return QueueEmailResponse(
        success=success,
        message=message,
        data=payload.model_dump(),
        email_id=email_queue_id,
        attachments_processed=attachment_count if attachments else None
    )
    
if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)