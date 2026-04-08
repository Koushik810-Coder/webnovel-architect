import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the Webnovel Architect project.
    It logs to both the console (stdout) and a central rotating file.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if the logger already exists
    if logger.hasHandlers():
        return logger
        
    # Standard level is INFO for the logger itself
    logger.setLevel(logging.DEBUG)
    
    # Detailed formatter for files
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Cleaner formatter for console
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console Handler (INFO and above)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(console_formatter)
    
    # Rotating File Handler (DEBUG and above, 10MB limit, 5 backups)
    log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'webnovel_architect.log')
    try:
        fh = RotatingFileHandler(
            log_file_path, 
            maxBytes=10*1024*1024, 
            backupCount=5, 
            encoding='utf-8'
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)
    except Exception as e:
        # Fallback if file logging fails (e.g. permissions)
        print(f"Warning: Could not initialize file logger at {log_file_path}: {e}")
    
    logger.addHandler(ch)
    
    # Prevent propagation to the root logger to avoid duplicate logs in some setups
    logger.propagate = False
    
    return logger
