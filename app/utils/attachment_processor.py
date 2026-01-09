from pathlib import Path
from app.config import config
from app.utils.logger import print_logging
from app.utils.file_utils import calculate_sha256
from app.database.transactions import insert_email_attachments
from typing import List
from fastapi import UploadFile


def save_attachment_to_disk(file_content: bytes, filename: str, email_queue_id: str) -> str:
    """
    Save attachment to disk and return the file path
    Organize files by email_queue_id to avoid conflicts
    Handles duplicate filenames by appending counter (1.pdf, 2.pdf, etc.)
    """
    upload_dir = Path(config.UPLOAD_DIR)
    
    email_dir = upload_dir / str(email_queue_id)
    email_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return str(file_path)


async def process_attachments(attachments: List[UploadFile], email_queue_id: str) -> int:
    """Process and save attachments, return count of successfully processed files"""
    attachment_count = 0
    
    for attachment in attachments:
        try:
            file_content = await attachment.read()
            file_size = len(file_content)
            
            if hasattr(config, 'ALLOWED_MIME_TYPES'):
                if attachment.content_type not in config.ALLOWED_MIME_TYPES:
                    print_logging("warning", f"Skipping attachment '{attachment.filename}' with disallowed MIME type '{attachment.content_type}'")
                    continue
            
            checksum = calculate_sha256(file_content)
            
            file_path = save_attachment_to_disk(
                file_content, 
                attachment.filename, 
                email_queue_id
            )
            
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
    
    return attachment_count
