import logging
import sys
import os

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the Webnovel Architect project.
    It logs to both the console (stdout) and a central file.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if the logger already exists
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    
    # File Handler
    log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'webnovel_architect.log')
    fh = logging.FileHandler(log_file_path, encoding='utf-8')
    fh.setLevel(logging.DEBUG)  # File gets more verbose logs if available
    fh.setFormatter(formatter)
    
    logger.addHandler(ch)
    logger.addHandler(fh)
    
    # Prevent propagation to the root logger to avoid duplicate logs in some setups
    logger.propagate = False
    
    return logger
