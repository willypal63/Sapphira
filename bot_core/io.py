# bot_core/io.py

from pathlib import Path
from bot_core.logger_utils import log_error

def list_project_files(project_path):
    try:
        return [f for f in Path(project_path).glob("**/*.py")]
    except Exception as e:
        log_error(e, f"Failed to list files in: {project_path}")
        return []

def read_file(file_path):
    try:
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        log_error(e, f"Failed to read file: {file_path}")
        return ""

def write_file(file_path, content):
    try:
        Path(file_path).write_text(content, encoding="utf-8")
    except Exception as e:
        log_error(e, f"Failed to write file: {file_path}")
