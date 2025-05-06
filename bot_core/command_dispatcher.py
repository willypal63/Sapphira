# bot_core/command_dispatcher.py

import json
import os
import socket
import threading
import time
import shutil
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Optional
from colorama import Fore, Style, init as colorama_init
from loguru import logger as training_logger

from bot_core.memory import clear_memory, export_conversation, memory_status
from bot_core.logger_utils import log_error
from bot_core.constants_config import HELP_TEXT
from bot_core.ocr_tools import ocr_test, ocr_scan_file, ocr_extract_all
from bot_core.learning import learn_all_supported_files
from bot_core.formatting import format_user_input, format_sapphira_response
from bot_core.code_generation import generate_file, generate_patch  # helpers for file generation and patching

# Initialize colorama
colorama_init(autoreset=True)

# Flag to control memory retention
memory_enabled = True

# Pending generation state
pending_generation: Optional[dict] = None

# Supported languages for file generation
SUPPORTED_LANGUAGES = [
    "Python", "JavaScript", "Java", "C#", "C++", "Ruby",
    "Go", "Rust", "TypeScript", "PHP", "Swift", "Kotlin"
]

# === TIME UTILITIES ===

def get_local_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_local_date() -> str:
    return datetime.now().strftime("%A, %B %d, %Y")

# Configuration paths
CONFIG_PATH = Path("D:/offline_codebot_prototype/config.json")
EXPORT_DIR = Path("D:/offline_codebot_prototype/logs/exports")
TRAIN_LOG = Path("logs/training_log.txt")
VECTORS_DIR = Path("memory/vectors")
SHARD_INDEX_PATH = Path("memory/shard_index.json")
# Directories for generated code, patch backups, import files, and import backups
GENERATED_DIR = Path("generated")
PATCH_BACKUP_DIR = GENERATED_DIR / "patch_backups"
IMPORT_DIR = Path("IMPORT FILES")
IMPORT_BACKUP_DIR = Path("import_backups")

# Setup training logger
training_logger.add(str(TRAIN_LOG), level="INFO")
with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config = json.load(f)

# Network status tracking
online_status = {"connected": True, "offline_mode": config.get("offline", False), "awaiting_user": False}
previous_state = {"connected": True}
instability_window = deque(maxlen=100)  # increased window to reduce false positives
stable_check_time = 0

# === NETWORK MONITOR ===

def has_internet_connection(timeout=3) -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout)
        return True
    except OSError:
        return False


def monitor_network():
    global stable_check_time
    while True:
        now = time.time()
        connected = has_internet_connection()
        if not connected and previous_state["connected"]:
            print(format_sapphira_response("Connection lost. Switching to OFFLINE mode."))
            previous_state["connected"] = False
            online_status.update({"connected": False, "offline_mode": True, "awaiting_user": True})
            instability_window.append(now)
        elif connected:
            if not previous_state["connected"]:
                previous_state["connected"] = True
                online_status.update({"connected": True, "awaiting_user": True})
                print(format_sapphira_response("Internet reconnected. Would you like to go back ONLINE? (yes/no)"))
                instability_window.append(now)
            elif online_status.get("offline_mode") and stable_check_time and now - stable_check_time >= 120:
                print(format_sapphira_response("Network has stabilized. Try to reconnect? (yes/no)"))
                stable_check_time = 0
        instability_window.append(now)
        recent = [t for t in instability_window if now - t <= 60]  # use 60s window
        # trigger offline prompt only after 20 unstable checks
        if len(recent) >= 20 and not online_status.get("offline_mode"):
            print(format_sapphira_response("Detected unstable connection. Enter offline mode? (y/n)"))
            online_status.update({"offline_mode": True, "awaiting_user": True})
            instability_window.clear()
            stable_check_time = now
        time.sleep(5)

# Start network monitoring thread
target_thread = threading.Thread(target=monitor_network, daemon=True)
target_thread.start()

# === VECTOR UTILITIES ===

def get_learned_summary() -> str:
    jsonl_files = list(VECTORS_DIR.glob("shard_*.jsonl"))
    npz_files = list(VECTORS_DIR.glob("shard_*.npz"))
    chunk_count = sum(1 for f in jsonl_files for _ in open(f, "r", encoding="utf-8"))
    return f"Shards: {len(jsonl_files)}, Vectors: {len(npz_files)}, Chunks: {chunk_count}"

def get_vector_status() -> str:
    index_kb = SHARD_INDEX_PATH.stat().st_size // 1024 if SHARD_INDEX_PATH.exists() else 0
    total_bytes = sum(f.stat().st_size for f in VECTORS_DIR.glob("*"))
    return f"Index size: {index_kb} KB, Total vector memory: {total_bytes / (1024 * 1024):.2f} MB"

# Ensure directories exist at startup
for d in (GENERATED_DIR, PATCH_BACKUP_DIR, IMPORT_DIR, IMPORT_BACKUP_DIR):
    d.mkdir(parents=True, exist_ok=True)

# === COMMAND DISPATCH ===

def handle_command(prompt: str) -> Optional[str]:
    global memory_enabled, pending_generation
    try:
        cmd = prompt.strip()
        lower = cmd.lower()

        # Handle pending language selection
        if pending_generation:
            for lang in SUPPORTED_LANGUAGES:
                if lower == lang.lower():
                    filename = pending_generation['filename']
                    description = pending_generation['description']
                    code_content = generate_file(description, lang)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base = Path(filename)
                    stem = base.stem
                    ext = base.suffix or ".txt"
                    new_name = f"{stem}_{lang.lower()}_{ts}{ext}"
                    file_path = GENERATED_DIR / new_name
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(code_content)
                    pending_generation = None
                    return format_sapphira_response(
                        f"Generated '{file_path}' in {lang}.\n\n{code_content}"
                    )
            langs = ", ".join(SUPPORTED_LANGUAGES)
            return format_sapphira_response(f"Please choose a language from: {langs}.")

        # Date & time
        if any(q in lower for q in ["what is today", "today's date"]):
            return format_sapphira_response(f"Today is {get_local_date()}.")
        if any(q in lower for q in ["what time is it", "current time"]):
            return format_sapphira_response(f"Current system time is {get_local_time()}.")

        match lower:
            # Connection commands
            case "yes" if online_status["awaiting_user"] and online_status["connected"]:
                online_status.update({"offline_mode": False, "awaiting_user": False})
                return format_sapphira_response("Back ONLINE. Internet features re-enabled.")
            case "no" if online_status["awaiting_user"]:
                online_status.update({"offline_mode": True, "connected": False, "awaiting_user": False})
                return format_sapphira_response("Remaining OFFLINE. You can type /connect to reconnect manually.")
            case "/connect":
                if has_internet_connection():
                    online_status.update({"connected": True, "offline_mode": False, "awaiting_user": False})
                    return format_sapphira_response("Successfully reconnected. Online mode active.")
                return format_sapphira_response("Reconnection failed. Still offline. Check your network connection.")
            case "/offline":
                online_status.update({"offline_mode": True, "connected": False, "awaiting_user": False})
                return format_sapphira_response("Offline mode activated. Internet features disabled until you reconnect.")
            case "/net status":
                status = f"Online: {'Yes' if online_status['connected'] else 'No'} | Offline Mode: {'Enabled' if online_status['offline_mode'] else 'Disabled'}"
                return format_sapphira_response(status)

            # Memory commands
            case "/forget":
                clear_memory()
                return format_sapphira_response("Conversation memory has been cleared.")
            case "/remember off":
                memory_enabled = False
                return format_sapphira_response("Memory retention is now OFF. I will not remember new inputs until you turn it back on with /remember on.")
            case "/remember on":
                memory_enabled = True
                return format_sapphira_response("Memory retention is now ON. I will remember your inputs again.")
            case "/memory status":
                base = memory_status()
                retention = 'ON' if memory_enabled else 'OFF'
                return format_sapphira_response(f"Memory status: {base} | Retention: {retention}")
            case "/memory export":
                return format_sapphira_response(f"Memory exported to: {export_conversation()}")
            case "/memory list":
                files = sorted(EXPORT_DIR.glob("exported_memory_*.txt"), reverse=True)
                return format_sapphira_response("\n".join(f.name for f in files) if files else "No memory export files found.")
            case "/memory open":
                latest = sorted(EXPORT_DIR.glob("exported_memory_*.txt"), reverse=True)
                if latest:
                    os.startfile(latest[0])
                    return format_sapphira_response(f"Opened {latest[0].name}")
                return format_sapphira_response("No memory export found to open.")

            # Learning & OCR
            case "/learn all":
                start = time.time()
                learned = learn_all_supported_files()
                duration = time.time() - start
                return format_sapphira_response(f"Learned from {len(learned)} files in {duration:.2f}s: {', '.join(learned)}")
            case "/learn summary":
                return format_sapphira_response(get_learned_summary())
            case "/vector status":
                return format_sapphira_response(get_vector_status())
            case "/ocr test":
                return format_sapphira_response(ocr_test())
            case _ if lower.startswith("/ocr scan"):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    return format_sapphira_response("Usage: /ocr scan <filename>")
                return format_sapphira_response(ocr_scan_file(parts[2]))
            case "/ocr extract all":
                results = ocr_extract_all()
                return format_sapphira_response(f"OCR complete: {', '.join(results)}")

            # File generation
            case _ if lower.startswith("/generate file"):
                parts = cmd.split(maxsplit=3)
                if len(parts) < 4:
                    return format_sapphira_response("Usage: /generate file <filename> <description>")
                raw_name = parts[2]
                description = parts[3]
                pending_generation = {'filename': raw_name, 'description': description}
                langs = ", ".join(SUPPORTED_LANGUAGES)
                return format_sapphira_response(
                    f"Which language should I generate the file in? Choose from: {langs}."
                )

            # File patching
            case _ if lower.startswith("/patch file"):
                parts = cmd.split(maxsplit=3)
                if len(parts) < 4:
                    return format_sapphira_response("Usage: /patch file <filename> <patch description>")
                filename = parts[2]
                patch_desc = parts[3]
                target_path = Path(filename)
                if not target_path.exists():
                    target_path = IMPORT_DIR / filename
                if not target_path.exists():
                    return format_sapphira_response(
                        f"File not found in working dir or '{IMPORT_DIR}': {filename}"
                    )
                original_code = target_path.read_text(encoding="utf-8")
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{target_path.stem}_backup_{ts}{target_path.suffix}"
                backup_path = PATCH_BACKUP_DIR / backup_name
                backup_path.write_text(original_code, encoding="utf-8")
                patched_code = generate_patch(original_code, patch_desc)
                target_path.write_text(patched_code, encoding="utf-8")
                if target_path.parent == IMPORT_DIR:
                    ts_import = datetime.now().strftime("%Y%m%d_%H%M%S")
                    stem = target_path.stem
                    ext = target_path.suffix or ""
                    dest_name = f"{stem}_import_{ts_import}{ext}"
                    dest = IMPORT_BACKUP_DIR / dest_name
                    shutil.move(str(target_path), str(dest))
                return format_sapphira_response(
                    f"Patched '{target_path.name}' successfully. Backup at '{backup_path}'. Imported file moved to '{dest}'.\n\n{patched_code}"
                )

            # Help
            case "/help":
                return format_sapphira_response(HELP_TEXT.strip())

        return None
    except Exception as e:
        log_error(e)
        return format_sapphira_response(f"Error: {e}")
