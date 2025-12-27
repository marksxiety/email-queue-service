import json
from app.database.connect import connect
from app.utils.logger import print_logging


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


def update_email_status(status, email_id):
    """
    Updates the delivery status of an email in the queue.
    
    Status Levels:
    - 0: Pending (In queue, not yet processed)
    - 1: Sent (Successfully delivered)
    - 2: Failed (Permanent or temporary delivery failure)
    """
    conn = connect()
    if conn is None:
        print_logging("error", f"Database connection unavailable. Cannot update email {email_id}")
        return

    cursor = None
    try:
        query = "UPDATE email_queues SET status = %s, sent_at = NOW() WHERE id = %s"      
        cursor = conn.cursor()
        cursor.execute(query, (status, email_id))
        conn.commit()
    except Exception as e:
        print_logging("error", f"Database error while updating email {email_id}: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        conn.close()
