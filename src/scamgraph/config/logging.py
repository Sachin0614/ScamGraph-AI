"""
ScamGraph AI - Logging Configuration
Provides consistent logging across the application.
"""

import logging
import sys
from pathlib import Path

from scamgraph.config.config import config


def setup_logging(log_level: str | None = None) -> logging.Logger:
    """
    Configure application logging.

    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured root logger
    """
    level = getattr(logging, (log_level or config.app.log_level).upper(), logging.INFO)

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    simple_formatter = logging.Formatter(
        fmt="%(levelname)-8s | %(name)s | %(message)s",
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # Console handler (simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # File handler (detailed format)
    file_handler = logging.FileHandler(log_dir / "scamgraph.log", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Error file handler (ERROR and above only)
    error_handler = logging.FileHandler(log_dir / "scamgraph_errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)