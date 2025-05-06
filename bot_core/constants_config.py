from pathlib import Path

CONFIG_PATH = Path("D:/offline_codebot_prototype/config.json")
LOG_PATH = Path("D:/offline_codebot_prototype/logs/conversation_log.txt")
MEMORY_PATH = Path("D:/offline_codebot_prototype/logs/history_memory.txt")
EXPORT_DIR = Path("D:/offline_codebot_prototype/logs/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

allowed_exts = [".txt", ".md", ".html", ".py", ".json", ".pdf"]

# Slash-command help text
HELP_TEXT = '''
Memory Management
/forget--------------→ Clear all conversation memory
/remember on|off-----→ Toggle memory status (always ON)
/memory status-------→ Show memory stats
/memory export-------→ Save memory to timestamped file
/memory list---------→ List exported memory files
/memory open---------→ Open the latest memory export
/remember off--------→ Turn OFF memory retention (won’t store new inputs)
/remember on---------→ Turn ON memory retention (will start storing inputs again)

Learning & Knowledge
/learn all           → Ingest all supported files from knowledge folder
/learn summary       → Show count of chunks, shards, vectors
/vector status       → Show vector store disk usage and index size

OCR Tools
/ocr test            → Run built-in OCR test
/ocr scan <file>     → OCR scan a specific image or PDF
/ocr extract all     → Extract all OCR-compatible files

System + Config
/config show         → Display current loaded config.json
/config reload       → Reload settings from config file
/offline             → Force disconnect from internet (manual offline mode)
/connect             → Reconnect to internet and enable online mode
/net status          → Show current online/offline and connection status
/knowledge status    → Show list of loaded knowledge files

Support
/help                → Show this help menu
'''


