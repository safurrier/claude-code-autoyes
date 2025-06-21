"""Centralized logging configuration for claude-autoyes."""

import logging
import os
from typing import Optional


def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Set up a logger with consistent formatting and configuration.

    Args:
        name: Logger name (typically __name__)
        log_file: Optional log file path. If None, logs to console.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    # Set log level
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add file handler if log_file specified
    if log_file:
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Console handler for development/testing
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_daemon_logger(log_file: str = "/tmp/claude-autoyes.log") -> logging.Logger:
    """Get logger specifically configured for daemon operations.

    Args:
        log_file: Path to daemon log file.

    Returns:
        Daemon logger instance.
    """
    return setup_logger("claude-autoyes.daemon", log_file)
