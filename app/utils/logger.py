import logging
import os
from logging.handlers import RotatingFileHandler

# Create the logs directory
log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_folder, exist_ok=True)

def get_logger():
    """
    Creates a logger instance.
    :return: Logger instance
    """
    log_filename = os.path.join(log_folder, "app.log")

    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        log_filename,
        mode='a',
        maxBytes=200 * 1024 * 1024,  # 200 MB max size before rotating
        backupCount=15,
        encoding=None,
        delay=False
    )

    # Define log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Create a logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def print_logging(level, message):
    """
    Log a message at the specified level.
    :param level: Log level (e.g., 'debug', 'info', 'warning', 'error', 'critical')
    :param message: Log message
    """
    logger = get_logger()

    level = level.lower()
    if level == "debug":
        logger.debug(message)
    elif level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "critical":
        logger.critical(message)
    else:
        logger.info(message)