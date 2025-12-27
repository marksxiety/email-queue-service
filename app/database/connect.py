import psycopg2
from app.config import config
from app.utils.logger import print_logging

def connect():
    """Create a database connection using credentials from environment variables."""
    try:
        conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            port=config.POSTGRES_PORT
        )
        return conn
    except Exception as e:
        print_logging("error", f"Failed to connect to the database: {e}")
        return None