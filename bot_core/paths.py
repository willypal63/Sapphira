# bot_core/paths.py

from pathlib import Path
from bot_core.logger_utils import log_info, log_error

PROJECT_PATH = Path("workspace")
LEARNING_DATA_PATH = Path("knowledge")
EMBEDDING_DB_PATH = Path("embeddings")
SESSION_PATH = Path("sessions")

ALL_PATHS = [PROJECT_PATH, LEARNING_DATA_PATH, EMBEDDING_DB_PATH, SESSION_PATH]

def ensure_directories():
    for path in ALL_PATHS:
        try:
            path.mkdir(parents=True, exist_ok=True)
            log_info(f"Verified or created directory: {path.resolve()}")
        except Exception as e:
            log_error(f"Failed to ensure directory {path}: {e}")
