import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from app.config import config
from app.utils.logger import print_logging


def send_email_via_smtp(subject, body, to_address, cc_addresses=None, bcc_addresses=None, attachments=[]):
    smtp_server = config.SMTP_HOST
    port = config.SMTP_PORT
    sender_email = config.SMTP_USER
    password = config.SMTP_PASSWORD

    sender_email = None if sender_email is None else str(sender_email)
    password = None if password is None else str(password)

    message = MIMEMultipart()
    message["From"] = sender_email

    to_list = to_address if isinstance(to_address, list) else [to_address]
    message["To"] = ", ".join([str(a) for a in to_list if a is not None])

    if cc_addresses:
        cc_list = cc_addresses if isinstance(cc_addresses, list) else [cc_addresses]
        message["Cc"] = ", ".join([str(a) for a in cc_list if a is not None])

    if bcc_addresses:
        bcc_list = bcc_addresses if isinstance(bcc_addresses, list) else [bcc_addresses]
        message["Bcc"] = ", ".join([str(a) for a in bcc_list if a is not None])

    message["Subject"] = str(subject)
    message.attach(MIMEText(body, "html"))

    for file_path in attachments:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            message.attach(part)

    all_recipients = to_list.copy()
    if cc_addresses:
        cc_list = cc_addresses if isinstance(cc_addresses, list) else [cc_addresses]
        all_recipients.extend(cc_list)
    if bcc_addresses:
        bcc_list = bcc_addresses if isinstance(bcc_addresses, list) else [bcc_addresses]
        all_recipients.extend(bcc_list)

    all_recipients = [str(a) for a in all_recipients if a is not None]

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, all_recipients, message.as_string())
        return True, "success"
    except Exception as e:
        print_logging("error", f"SMTP error: {str(e)}")
        return False, e
