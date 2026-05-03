"""Logging configuration for SK-OCI application"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logger(name: str, log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If log_level is invalid
    """
    # Validate log level
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {log_level}. Must be one of {valid_levels}")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with rotation (10 MB, keep 5 files)
    log_file = os.path.join(log_dir, f"sk-oci_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def redact_credentials(message: str) -> str:
    """
    Redact sensitive information from log messages.
    
    Args:
        message: Message to redact
        
    Returns:
        Redacted message
    """
    redaction_patterns = [
        ("ocid1.", "ocid1.***REDACTED***"),
        ("fingerprint", "***REDACTED***"),
        ("key_file", "***REDACTED***"),
        ("api_key", "***REDACTED***"),
    ]
    
    redacted = message
    for pattern, replacement in redaction_patterns:
        if pattern.lower() in message.lower():
            redacted = redacted.replace(pattern, replacement)
    
    return redacted
