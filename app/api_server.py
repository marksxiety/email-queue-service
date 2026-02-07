from fastapi import FastAPI, UploadFile, File, Form, Request, Response
from app.config import config
import uvicorn
from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional, List
from app.database.transactions import insert_email_queues, check_email_type_registration
from app.utils.attachment_processor import process_attachments
from app.utils.rabbitmq_publisher import publish_to_rabbitmq
from app.utils.logger import print_logging
import json
import time
from datetime import datetime
from functools import wraps

if config.RATE_LIMIT_ENABLED:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded


class EmailQueueRequest(BaseModel):
    email_type: Any
    subject: Any
    email_template: Any
    email_data: Dict[str, Any]
    priority_level: int
    to_addresses: Optional[List[str]] = None
    cc_addresses: Optional[List[str]] = None
    bcc_addresses: Optional[List[str]] = None

    @field_validator('email_template')
    @classmethod
    def validate_template_exists(cls, v):
        template_name = v if v.endswith('.html') else f"{v}.html"
        try:
            from app.config import jinja_env
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
app_start_time = time.time()

if config.RATE_LIMIT_ENABLED:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[],
        headers_enabled=True
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def rate_limit_exempt_with_grace_period(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        elapsed = time.time() - app_start_time
        if elapsed < config.RATE_LIMIT_GRACE_PERIOD_SECONDS:
            return await f(*args, **kwargs)
        return await f(*args, **kwargs)
    return wrapper

@app.post("/api/v1/emails/queue")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute") if config.RATE_LIMIT_ENABLED else lambda f: f
@limiter.limit(f"{config.RATE_LIMIT_PER_HOUR}/hour") if config.RATE_LIMIT_ENABLED else lambda f: f
@rate_limit_exempt_with_grace_period if config.RATE_LIMIT_ENABLED else lambda f: f
async def queue_email(
    response: Response,
    request: Request,
    email_type: str = Form(...),
    subject: str = Form(...),
    email_template: str = Form(...),
    email_data: str = Form(...),
    priority_level: int = Form(...),
    to_addresses: Optional[List[str]] = Form(None),
    cc_addresses: Optional[List[str]] = Form(None),
    bcc_addresses: Optional[List[str]] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None)
) -> QueueEmailResponse:
    try:
        email_data_dict = json.loads(email_data)

        if isinstance(email_data_dict, dict) and "email_data" in email_data_dict:
            email_data_dict = email_data_dict["email_data"]

    except json.JSONDecodeError as e:
        print_logging("error", f"Invalid JSON in email_data: {str(e)}")
        response.status_code = 400
        return QueueEmailResponse(
            success=False,
            message="Invalid JSON format in email_data field",
            data=None
        )
    
    payload_dict = {
        "email_type": email_type,
        "subject": subject,
        "email_template": email_template,
        "email_data": email_data_dict,
        "priority_level": priority_level,
        "to_addresses": to_addresses,
        "cc_addresses": cc_addresses,
        "bcc_addresses": bcc_addresses
    }
    
    try:
        payload = EmailQueueRequest(**payload_dict)
    except Exception as e:
        print_logging("error", f"Payload validation failed: {str(e)}")
        response.status_code = 400
        return QueueEmailResponse(
            success=False,
            message=f"Payload validation failed: {str(e)}",
            data=None
        )
        
    # check first if the payload's email type is registered to avoid PK and FK relationship
    is_email_type_exists = check_email_type_registration(payload.email_type)
    
    if not is_email_type_exists:
        response.status_code = 422
        return QueueEmailResponse(
            success=False,
            message="Email type is not registered"
        )

    email_data = insert_email_queues(payload)

    if not email_data:
        response.status_code = 500
        return QueueEmailResponse(
            success=False,
            message="Failed to register the request into email queue",
            data=None
        )
    
    email_queue_id = email_data["id"]
    attachment_count = 0
    
    if attachments:
        attachment_count = await process_attachments(attachments, email_queue_id)
    
    published = publish_to_rabbitmq(email_data, payload.priority_level)

    if published:
        response.status_code = 201
        return QueueEmailResponse(
            success=True,
            message=f"Email {email_queue_id} received and published successfully",
            data=payload.model_dump(),
            email_id=email_queue_id,
            attachments_processed=attachment_count if attachments else None
        )
    else:
        response.status_code = 500
        print_logging('critical', f"Email {email_queue_id} inserted but failed to publish to queue")
        return QueueEmailResponse(
            success=False,
            message=f"Email {email_queue_id} inserted but failed to publish to queue",
            data=payload.model_dump(),
            email_id=email_queue_id,
            attachments_processed=attachment_count if attachments else None
        )
    
if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)