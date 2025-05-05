from pathlib import Path

CONFIG_PATH = Path("D:/offline_codebot_prototype/config.json")
LOG_PATH = Path("D:/offline_codebot_prototype/logs/conversation_log.txt")
MEMORY_PATH = Path("D:/offline_codebot_prototype/logs/history_memory.txt")
EXPORT_DIR = Path("D:/offline_codebot_prototype/logs/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

allowed_exts = [".txt", ".md", ".html", ".py", ".json", ".pdf"]

HELP_TEXT = """
/github import <repo_url> – Clone and learn from a GitHub repo
Available Commands:
/memory list      – List all saved memory export files
/forget           – Clear all saved conversation history
/remember on      – Enable memory (default ON)
/remember off     – Disable memory temporarily
/memory status    – Show whether memory is ON or OFF
/memory export    – Save current memory to a timestamped file
/memory open      – Open most recent memory export file
/offline on       – Activate offline mode (blocks online logic)
/offline off      – Deactivate offline mode
/knowledge status – Show which knowledge files are loaded
/ocr test         – Run built-in OCR check
/ocr scan <file>  – OCR extract from PDF/image in knowledge/
/ocr extract all  – OCR all PDFs/images and save .ocr.txt files
/learn ocr        – Learn from and delete all .ocr.txt files in knowledge/
/learn all        – Automatically learn from all supported files in knowledge/
/error log        – Show recent error log entries
/error clear      – Clear all error log contents
/config show      – Show current config settings
/config reload    – Reload config.json values
/help             – Show this help message
"""
