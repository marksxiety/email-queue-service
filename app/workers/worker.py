from app.utils.logger import print_logging
from app.utils.database_connect import connect
import pandas as pd
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from app.config import config

# Load templates
# Priority: user-added templates (app/user/templates) override default templates (app/templates)
env = Environment(loader=ChoiceLoader([
    FileSystemLoader("app/user/templates"),   # user-added or uploaded templates
    FileSystemLoader("app/templates")         # default/base templates
]))

def get_on_queue_emails():
    conn = connect()
    if conn is None:
        print_logging("error", "Failed to connect to database")
        return False

    cursor = None
    try:
        query = """
            SELECT id, email_type, subject, email_template, email_data, status 
            FROM email_queues  WHERE status = 0 ORDER BY priority_level ASC
        """
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        emails_df = pd.DataFrame(results, columns=columns)
        return emails_df

    except Exception as e:
        print_logging("error", f"Error querying emails: {str(e)}")
        return False

    finally:
        if cursor:
            cursor.close()
        conn.close()

def render_email_template(template_name, data):
    template = env.get_template(f"{template_name}.html")
    return template.render(**data)

def send_email_via_smtp(subject, body):
    smtp_server = config.SMTP_HOST
    port = config.SMTP_PORT
    sender_email = config.SMTP_USER
    password = config.SMTP_PASSWORD
    receiver_email = "markciril.jamon@gmail.com"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print_logging("error", f"SMTP error: {str(e)}")
        return False

def update_email_status(email_id):
    conn = connect()
    if conn is None:
        print_logging("error", f"Failed to connect to DB to update email {email_id}")
        return

    cursor = None
    try:
        query = "UPDATE email_queues SET status = 1, sent_at = NOW() WHERE id = %s"
        cursor = conn.cursor()
        cursor.execute(query, (email_id,))
        conn.commit()
    except Exception as e:
        print_logging("error", f"Failed to update email {email_id}: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        conn.close()

def initialize_worker():
    pending_emails = get_on_queue_emails()
    if pending_emails is False or pending_emails.empty:
        print_logging("info", "No emails to process.")
        return

    for row_index, row_series in pending_emails.iterrows():
        email_id = row_series["id"]
        subject = row_series["subject"]
        template_name = row_series["email_template"]
        email_data = row_series["email_data"]

        # Parse JSON data if needed
        if isinstance(email_data, str):
            try:
                email_data = json.loads(email_data)
            except json.JSONDecodeError as e:
                print_logging("error", f"Invalid JSON for email {email_id}: {str(e)}")
                continue

        # Render email
        body = render_email_template(template_name, email_data)

        # Send email
        success = send_email_via_smtp(subject, body)
        if success:
            print_logging("info", f"Email {email_id} sent successfully!")
            update_email_status(email_id)
        else:
            print_logging("error", f"Failed to send email {email_id}")

if __name__ == "__main__":
    initialize_worker()
