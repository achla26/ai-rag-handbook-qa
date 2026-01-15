import logging
import sys

def Logger(name=__name__, level=logging.INFO):
    """Set up and return a logger with the given name and level."""
    logger = logging.getLogger(name)
   
    # Only set up the logger if it hasn't been set up before
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
    
    return logger

# Create logger instance
logger = Logger()

def die(message="Execution stopped"):
    """Log an error message and exit the program."""
    logger.error(message) 
    sys.exit(1)
 