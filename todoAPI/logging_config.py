import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Set up logging for the application"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create a logger
    logger = logging.getLogger('todo_api')
    logger.setLevel(logging.DEBUG)  # Set the lowest level to capture all messages

    # Create a file handler for logging to a file
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)  # Log INFO and above to file

    # Create a console handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Log DEBUG and above to console

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Initialize the logger
logger = setup_logging()
