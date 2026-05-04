"""
Logger Configuration - Application logging setup.
"""

import logging
import logging.handlers
from pathlib import Path
from config.settings import LOG_FOLDER, LOG_LEVEL, APP_NAME

# Create logs directory
Path(LOG_FOLDER).mkdir(exist_ok=True)


def setup_logger(name=None):
    """
    Setup logger with file and console handlers.
    
    Args:
        name: Logger name (default: APP_NAME)
        
    Returns:
        Configured logger instance
    """
    name = name or APP_NAME
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set level
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # File handler with rotation
    log_file = Path(LOG_FOLDER) / f"{name.lower().replace(' ', '_')}.log"
    
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    except Exception as e:
        logger.warning(f"Could not setup file handler: {e}")
    
    return logger


# Create default logger
app_logger = setup_logger()
