
import logging
import sys

def setup_logger(name, level=logging.INFO):
    """Set up and configure logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if handlers are already configured
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    return logger