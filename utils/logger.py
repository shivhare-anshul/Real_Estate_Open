"""
Logging utility with enable/disable functionality
Uses Python's built-in logging module
"""

import sys
import logging
from pathlib import Path
from config.settings import settings

# Configure logging based on settings
if settings.ENABLE_LOGGING:
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    log_file_path = Path(settings.LOG_FILE_PATH)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info("✅ Logging enabled and configured")
else:
    # Create a minimal logger that only shows errors
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)
    logger.warning("⚠️ Logging is disabled")

# Export logger
__all__ = ["logger"]
