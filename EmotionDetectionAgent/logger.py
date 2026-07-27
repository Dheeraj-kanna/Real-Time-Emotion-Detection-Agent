"""
Logging module for the Real-Time Emotion Detection Agent.

Provides a centralized Logger class that writes formatted log entries
to both the console and application.log file.

Dependencies: logging (standard library), config
"""

import logging
from logging.handlers import RotatingFileHandler

from config import ConfigManager


class Logger:
    """Application-wide logger with file and console output."""

    _instance: logging.Logger | None = None

    @classmethod
    def setup(cls, name: str = "EmotionDetectionAgent") -> logging.Logger:
        """
        Initialize and return the application logger.

        Args:
            name: Logger name used for identification.

        Returns:
            Configured logging.Logger instance.
        """
        if cls._instance is not None:
            return cls._instance

        ConfigManager.ensure_directories()

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            file_handler = RotatingFileHandler(
                ConfigManager.LOG_FILE,
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        cls._instance = logger
        return logger

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Return the existing logger or create a new one.

        Returns:
            Configured logging.Logger instance.
        """
        if cls._instance is None:
            return cls.setup()
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Close and release all logger handlers."""
        if cls._instance is not None:
            for handler in cls._instance.handlers[:]:
                handler.close()
                cls._instance.removeHandler(handler)
            cls._instance = None
