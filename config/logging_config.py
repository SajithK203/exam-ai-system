"""
Logging Configuration Module - Setup application-wide logging.
"""

import logging
import logging.config
import os
from config.settings import LOG_FOLDER, LOG_LEVEL

# Ensure log directory exists
os.makedirs(LOG_FOLDER, exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': LOG_LEVEL,
            'formatter': 'detailed',
            'filename': os.path.join(LOG_FOLDER, 'app.log'),
            'maxBytes': 10485760,
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': os.path.join(LOG_FOLDER, 'error.log'),
            'maxBytes': 10485760,
            'backupCount': 5
        }
    },
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['console', 'file', 'error_file']
    }
}

# Apply configuration
logging.config.dictConfig(LOGGING_CONFIG)
