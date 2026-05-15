"""
Logging Configuration Module

Provides centralized logging setup for the Data Quality Validation Framework.
Supports file and console logging with configurable levels and formats.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class LoggerConfig:
    """Centralized logging configuration."""
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    # Log directory
    LOG_DIR = Path(__file__).parent.parent.parent / "logs"
    
    # Log file names
    APP_LOG = "app.log"
    ERROR_LOG = "error.log"
    ANOMALY_LOG = "anomaly_detection.log"
    VALIDATION_LOG = "validation.log"
    RECONCILIATION_LOG = "reconciliation.log"
    API_LOG = "api.log"
    
    # Default log format
    VERBOSE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    SIMPLE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    CONSOLE_FORMAT = "%(levelname)s - %(name)s - %(message)s"
    
    # Default date format
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @staticmethod
    def ensure_log_directory():
        """Create logs directory if it doesn't exist."""
        LoggerConfig.LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    verbose: bool = True
) -> logging.Logger:
    """
    Setup a logger with file and console handlers.
    
    Args:
        name (str): Logger name (typically __name__)
        log_file (Optional[str]): Log file name (relative to LOG_DIR)
        level (int): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output (bool): Enable console output
        file_output (bool): Enable file output
        max_bytes (int): Maximum size of log file before rotation
        backup_count (int): Number of backup log files to keep
        verbose (bool): Use verbose format (includes filename and line number)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure log directory exists
    LoggerConfig.ensure_log_directory()
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Select format
    log_format = LoggerConfig.VERBOSE_FORMAT if verbose else LoggerConfig.SIMPLE_FORMAT
    formatter = logging.Formatter(log_format, datefmt=LoggerConfig.DATE_FORMAT)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(LoggerConfig.CONSOLE_FORMAT, datefmt=LoggerConfig.DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_output and log_file:
        log_path = LoggerConfig.LOG_DIR / log_file
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to setup file handler for {log_file}: {e}")
    
    return logger


def get_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """
    Get a logger instance with default configuration.
    
    Args:
        name (str): Logger name (typically __name__)
        log_file (Optional[str]): Log file name
        level (int): Logging level
        
    Returns:
        logging.Logger: Logger instance
    """
    return setup_logger(name, log_file=log_file, level=level)


def setup_app_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Setup the main application logger.
    
    Args:
        level (int): Logging level
        
    Returns:
        logging.Logger: Application logger
    """
    return setup_logger(
        "app",
        log_file=LoggerConfig.APP_LOG,
        level=level,
        console_output=True,
        file_output=True,
        verbose=True
    )


def setup_error_logger(level: int = logging.ERROR) -> logging.Logger:
    """
    Setup error-specific logger.
    
    Args:
        level (int): Logging level
        
    Returns:
        logging.Logger: Error logger
    """
    return setup_logger(
        "app.error",
        log_file=LoggerConfig.ERROR_LOG,
        level=level,
        console_output=True,
        file_output=True,
        verbose=True
    )


def setup_anomaly_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Setup anomaly detection logger.
    
    Args:
        level (int): Logging level
        
    Returns:
        logging.Logger: Anomaly detection logger
    """
    return setup_logger(
        "app.anomaly_detection",
        log_file=LoggerConfig.ANOMALY_LOG,
        level=level,
        console_output=True,
        file_output=True,
        verbose=True
    )


def setup_validation_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Setup validation logger.
    
    Args:
        level (int): Logging level
        
    Returns:
        logging.Logger: Validation logger
    """
    return setup_logger(
        "app.validation",
        log_file=LoggerConfig.VALIDATION_LOG,
        level=level,
        console_output=True,
        file_output=True,
        verbose=True
    )


def setup_reconciliation_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Setup reconciliation logger.
    
    Args:
        level (int): Logging level
        
    Returns:
        logging.Logger: Reconciliation logger
    """
    return setup_logger(
        "app.reconciliation",
        log_file=LoggerConfig.RECONCILIATION_LOG,
        level=level,
        console_output=True,
        file_output=True,
        verbose=True
    )


def setup_api_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Setup API request/response logger.
    
    Args:
        level (int): Logging level
        
    Returns:
        logging.Logger: API logger
    """
    return setup_logger(
        "app.api",
        log_file=LoggerConfig.API_LOG,
        level=level,
        console_output=True,
        file_output=True,
        verbose=False
    )


def setup_all_loggers(level: int = logging.INFO) -> dict:
    """
    Setup all application loggers.
    
    Args:
        level (int): Logging level for all loggers
        
    Returns:
        dict: Dictionary with all configured loggers
    """
    return {
        "app": setup_app_logger(level),
        "error": setup_error_logger(level),
        "anomaly": setup_anomaly_logger(level),
        "validation": setup_validation_logger(level),
        "reconciliation": setup_reconciliation_logger(level),
        "api": setup_api_logger(level)
    }


class LoggerMixin:
    """
    Mixin class for adding logging to other classes.
    
    Usage:
        class MyClass(LoggerMixin):
            pass
        
        obj = MyClass()
        obj.logger.info("Log message")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)
        return self._logger


# Initialize logging directory
LoggerConfig.ensure_log_directory()

# Module-level logger
logger = setup_app_logger()
