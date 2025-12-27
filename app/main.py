from fastapi import FastAPI
from app.config import config, jinja_env
import uvicorn
from pydantic import BaseModel, field_validator
from typing import Dict, Any

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
            return template_name
        except Exception:
            # This triggers the 422 Unprocessable Entity error
            raise ValueError(f"Template '{template_name}' does not exist in templates folders.")

app = FastAPI()

@app.post("/api/v1/emails/queue")
async def queue_email(payload: EmailQueueRequest):
    return {
        "message": "Payload received successfully",
        "data": payload.dict()
    }
    
if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)