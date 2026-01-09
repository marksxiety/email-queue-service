from app.database.transactions import is_has_file_attachments
import os


def get_file_attachments(email_queue_id):
    attachments_metadata = is_has_file_attachments(email_queue_id)
    file_list = []
    
    for attachment in attachments_metadata:
        file_path = attachment["file_path"]
        if os.path.exists(file_path):
            file_list.append(file_path)
    
    return file_list
