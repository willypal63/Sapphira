# bot_core/logger_utils.py — unified loguru logger

from loguru import logger
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"bot-{datetime.now().strftime('%Y-%m-%d')}.log"

logger.add(
    str(LOG_FILE),
    level="ERROR",
    backtrace=True,
    diagnose=True
)

def get_logger():
    return logger

def log_error(error_msg: str):
    logger.error("{}", error_msg)

def log_info(info_msg: str):
    pass

def log_interaction(prompt: str, response: str):
    pass
