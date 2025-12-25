import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name="BridgeMonitor"):
    """
    Setup the global logger with console and file handlers.
    
    Args:
        name: Logger name
        
    Returns:
        logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
        
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Stream Handler (Console)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    
    # File Handler (Rotating)
    # Rotate every day ('D'), keep 7 backup files
    log_file = os.path.join(log_dir, "app.log")
    file_handler = TimedRotatingFileHandler(
        log_file, when='D', interval=1, backupCount=7, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    return logger

# Create a default global logger instance
logger = setup_logger()
