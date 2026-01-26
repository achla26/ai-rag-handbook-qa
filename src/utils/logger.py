import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

def Logger(
    name: str = __name__,
    level: int = logging.INFO,
    log_file: str | Path | None = "logs/app.log",      # Set to None to disable file logging
    file_level: int | None = None,                # None = same as console level
    max_bytes: int = 10 * 1024 * 1024,            # 10 MB (for RotatingFileHandler)
    backup_count: int = 5,
    use_timed_rotation: bool = False,             # Set True for daily logs
    console: bool = True
) -> logging.Logger:
    """
    Create and return a configured logger with console and/or file output.
    
    Parameters:
        log_file: Path to log file. Set None or "" to disable file logging.
        use_timed_rotation: If True, uses TimedRotatingFileHandler (daily logs)
        max_bytes / backup_count: Used only with RotatingFileHandler
    """
    logger = logging.getLogger(name)
    
    # Prevent adding handlers multiple times (important in notebooks/scripts that reload)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    file_level = file_level or level

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s'
    )

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)  # ensure directory exists
        
        if use_timed_rotation:
            # Daily logs: app.log, app.log.2025-04-05, etc.
            file_handler = TimedRotatingFileHandler(
                filename=log_file,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='utf-8'
            )
        else:
            # Size-based rotation (default)
            file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

logger = Logger()


def die(message="Execution stopped"):
    """Log an error message and exit the program."""
    logger.error(message) 
    sys.exit(1)
 