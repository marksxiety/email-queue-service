from dotenv import load_dotenv
import os
from jinja2 import Environment, FileSystemLoader, ChoiceLoader

load_dotenv(override=True)

class Config:
    APP_NAME = os.getenv("APP_NAME")
    
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_DEBUG = os.getenv("API_DEBUG", "True") == "True"
    
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    
    EMAIL_QUEUE_HIGH = os.getenv("EMAIL_QUEUE_HIGH", "email.high")
    EMAIL_QUEUE_NORMAL = os.getenv("EMAIL_QUEUE_NORMAL", "email.normal")
    EMAIL_QUEUE_LOW = os.getenv("EMAIL_QUEUE_LOW", "email.low")
    
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM")
    
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
    RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "30"))

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True") == "True"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "100"))
    RATE_LIMIT_GLOBAL_PER_MINUTE = int(os.getenv("RATE_LIMIT_GLOBAL_PER_MINUTE", "500"))
    RATE_LIMIT_GLOBAL_PER_HOUR = int(os.getenv("RATE_LIMIT_GLOBAL_PER_HOUR", "5000"))
    RATE_LIMIT_GRACE_PERIOD_SECONDS = int(os.getenv("RATE_LIMIT_GRACE_PERIOD_SECONDS", "300"))
    
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "application/zip",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/webp",
        "image/tiff",
    }
    
config = Config()

jinja_env = Environment(loader=ChoiceLoader([
    FileSystemLoader("app/user/templates"),
    FileSystemLoader("app/templates")
]))
