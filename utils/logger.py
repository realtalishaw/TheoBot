import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup a logger with specified name and log file."""
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a formatter that includes the time, level, filename, and line number
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    # Create handlers for both file and console output
    file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024*5, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
