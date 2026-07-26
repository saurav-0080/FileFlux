"""
Logging configuration for the Smart File Organizer.

Sets up a logger that writes to both the console and a log file,
with timestamps and log levels, replacing scattered print() calls.
"""

import logging
from pathlib import Path

from app.constants import LOG_DIR, LOG_FILE


def setup_logger(name: str = "organizer") -> logging.Logger:
    """
    Configure and return a logger that writes to console and file.

    Args:
        name: Name of the logger instance.

    Returns:
        A configured Logger instance ready to use.
    """
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_dir / LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger