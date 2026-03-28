"""
Logging Configuration for Firmware Emulator
"""
import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Timestamp for log files
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Log file paths
MAIN_LOG_FILE = os.path.join(LOG_DIR, f"emulator_{TIMESTAMP}.log")
SERIAL_LOG_FILE = os.path.join(LOG_DIR, f"serial_{TIMESTAMP}.log")
COMMANDS_LOG_FILE = os.path.join(LOG_DIR, f"commands_{TIMESTAMP}.log")

# Log format
DETAILED_FORMAT = (
    "%(asctime)s.%(msecs)03d | "
    "%(levelname)-8s | "
    "%(name)-20s | "
    "%(funcName)-15s | "
    "%(message)s"
)

SIMPLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name, log_file, level=logging.DEBUG):
    """
    Set up a named logger with file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        log_file: File path for logging
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler (rotating, max 5MB per file, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(file_handler)
    
    # Console handler (INFO level for less verbosity)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(SIMPLE_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name):
    """
    Get or create a logger. Use in modules with: logger = get_logger(__name__)
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    if name.startswith("emulator.serial"):
        return setup_logger(name, SERIAL_LOG_FILE)
    elif name.startswith("emulator.commands"):
        return setup_logger(name, COMMANDS_LOG_FILE)
    else:
        return setup_logger(name, MAIN_LOG_FILE)


# Root logger configuration
def setup_root_logger(level=logging.DEBUG):
    """Set up the root logger."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        MAIN_LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT, datefmt=DATE_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(SIMPLE_FORMAT, datefmt=DATE_FORMAT))
    root_logger.addHandler(console_handler)


def setup_logging(level=logging.DEBUG):
    """Alias for setup_root_logger for consistency"""
    return setup_root_logger(level)


# Module-specific loggers
MAIN_LOGGER = get_logger("emulator.main")
SERIAL_LOGGER = get_logger("emulator.serial")
COMMANDS_LOGGER = get_logger("emulator.commands")
STATE_LOGGER = get_logger("emulator.state")
HANDLER_LOGGER = get_logger("emulator.handlers")
