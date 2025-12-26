from fastapi import FastAPI
from app.config import config
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any

class EmailQueueRequest(BaseModel):
    sender: str
    email_type: str
    subject: str
    email_template: str
    email_data: Dict[str, Any]
    priority_level: int

app = FastAPI()

@app.post("/api/v1/emails/queue")
async def queue_email(payload: EmailQueueRequest):
    return {
        "message": "Payload received successfully",
        "data": payload.dict()
    }
    
if __name__ == '__main__':
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)