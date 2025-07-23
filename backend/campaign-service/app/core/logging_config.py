
# app/core/logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging():
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "campaign_service.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure specific loggers
    loggers = {
        "app": logging.INFO,
        "sqlalchemy.engine": logging.WARNING,
        "uvicorn": logging.INFO,
        "fastapi": logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
