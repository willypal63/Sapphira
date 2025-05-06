# bot_core/constants_config.py

from pathlib import Path

# --- Directory paths ---
# Where your JSON config lives
CONFIG_PATH = Path("config.json")

# Where conversation logs and memory exports go
LOG_PATH = Path("logs/conversation_log.txt")
MEMORY_PATH = Path("logs/history_memory.txt")
EXPORT_DIR = Path("logs/exports")

# Where you drop files to be ingested/learned
IMPORT_DIR = Path("IMPORT FILES")

# Make sure all these directories exist at startup
for d in (LOG_PATH.parent, EXPORT_DIR, IMPORT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --- Supported file extensions for ingestion ---
ALLOWED_EXTS = [
    # Text & code
    ".txt", ".md", ".html", ".py", ".json", ".jsonl", ".csv", ".tsv", ".log",
    ".xml", ".yaml", ".yml", ".ini", ".toml", ".properties",
    ".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".sass", ".less",

    # Office docs
    ".pdf", ".doc", ".docx", ".odt",
    ".xls", ".xlsx", ".ods",
    ".ppt", ".pptx", ".odp",

    # E-books & markup
    ".epub", ".tex", ".rtf",

    # Images & graphics
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".svg", ".ico", ".gif", ".heic", ".webp",

    # Audio
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".opus", ".wma", ".m4a", ".m4b", ".alac",

    # Video
    ".mp4", ".avi", ".mov", ".mkv", ".flv", ".webm", ".wmv", ".mpeg", ".mpg",

    # Archives
    ".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".rar", ".7z", ".jar",
    ".iso", ".img", ".dmg",

    # Data formats
    ".h5", ".hdf5", ".pkl", ".pickle", ".mat", ".sav", ".dta", ".sql", ".db", ".mdb",
    ".sqlite", ".sqlite3", ".parquet", ".avro", ".orc", ".msgpack", ".arrow",

    # ML models
    ".pt", ".pth", ".pb", ".onnx", ".ckpt",

    # Notebooks
    ".ipynb",

    # 3D models
    ".stl", ".obj", ".fbx",

    # GIS & mapping
    ".shp", ".geojson", ".kml",

    # Email
    ".eml",

    # Config & env
    ".conf", ".cfg", ".env",

    # Certs & keys
    ".pem", ".crt", ".key",

    # Executables & installers
    ".apk", ".exe", ".msi", ".deb", ".rpm", ".pkg",

    # Compressed
    ".bz2", ".gz", ".xz", ".lzma",

    # Misc
    ".djvu", ".ps", ".eps", ".mobi", ".poi", ".mo", ".dcm", ".nii"
]

# --- Slash-command help text ---
HELP_TEXT = """
Available slash commands:

Network Commands:
  /connect                 Attempt to reconnect to the internet.
  /offline                 Switch to offline mode (disable internet features).
  /net status              Display current network connection and offline mode status.

Memory Commands:
  /forget                  Clear the conversation memory.
  /remember off            Disable memory retention (forget new inputs).
  /remember on             Enable memory retention again.
  /memory status           Show memory base stats and retention state.
  /memory export           Export the full conversation memory to a file.
  /memory list             List all exported memory files available.
  /memory open             Open the most recent memory export.

Learning & OCR Commands:
  /learn all               Learn from all supported files in the project workspace.
  /learn summary           Show a summary of learned knowledge (shard counts, vector status).
  /vector status           Report storage size and chunk counts of the vector database.
  /ocr test                Run the OCR test suite to verify functionality.
  /ocr scan <filename>     Perform OCR scan on the specified file.
  /ocr extract all         Extract text from all imported files using OCR.

File Generation & Patching:
  /generate file <filename> <description>
                           Generate a new file with the given name and description.
  /patch file <filename> <description>
                           Apply a patch to an existing file based on the description.

Utility Commands:
  /help                    Show this help message.
"""
