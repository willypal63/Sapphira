# command_dispatcher.py (fully rewritten)

import json
import os
import socket
import threading
import time
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

colorama_init(autoreset=True)

# === TIME UTIL ===
def get_local_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_local_date() -> str:
    return datetime.now().strftime("%A, %B %d, %Y")

CONFIG_PATH = Path("D:/offline_codebot_prototype/config.json")
EXPORT_DIR = Path("D:/offline_codebot_prototype/logs/exports")
TRAIN_LOG = Path("logs/training_log.txt")
VECTORS_DIR = Path("memory/vectors")
SHARD_INDEX_PATH = Path("memory/shard_index.json")
training_logger.add(str(TRAIN_LOG), level="INFO")

with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config = json.load(f)

online_status = {"connected": True, "offline_mode": config.get("offline", False), "awaiting_user": False}

# === FORMAT ===
def format_user_input(text: str) -> str:
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"

def format_sapphira_response(text: str) -> str:
    ts = datetime.now().strftime("[%H:%M:%S]")
    return f"\033[96m{ts} Sapphira: {text}{Style.RESET_ALL}"

# === NETWORK ===
def has_internet_connection(timeout=3) -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout)
        return True
    except OSError:
        return False

previous_state = {"connected": True}
instability_window = deque(maxlen=10)
stable_check_time = 0


def monitor_network():
    global stable_check_time
    while True:
        now = time.time()
        connected = has_internet_connection()

        if not connected:
            if previous_state["connected"]:
                print(format_sapphira_response("Connection lost. Switching to OFFLINE mode."))
                previous_state["connected"] = False
                online_status.update({"connected": False, "offline_mode": True, "awaiting_user": True})
            instability_window.append(now)

        elif connected:
            if not previous_state["connected"]:
                previous_state["connected"] = True
                online_status["connected"] = True
                instability_window.append(now)
                if online_status["offline_mode"]:
                    online_status["awaiting_user"] = True
                    print(format_sapphira_response("Internet reconnected. Would you like to go back ONLINE? (yes/no)"))

            # check if it stabilized after instability
            if (not online_status["connected"] or online_status["offline_mode"]) and stable_check_time:
                if now - stable_check_time >= 120:
                    print(format_sapphira_response("Network has stabilized for 2–4 minutes since last disconnect. Try to reconnect?"))
                    stable_check_time = 0

        # monitor instability
        instability_cut = [t for t in instability_window if now - t <= 30]
        if len(instability_cut) >= 4 and not online_status["offline_mode"]:
            print(format_sapphira_response("Detected unstable connection (4+ events in 30s). Stay offline? (y/n)"))
            online_status["awaiting_user"] = True
            online_status["offline_mode"] = True
            stable_check_time = time.time()
            instability_window.clear()

        time.sleep(5)


threading.Thread(target=monitor_network, daemon=True).start()

# === VECTOR STATS ===
def get_learned_summary():
    jsonl_files = list(VECTORS_DIR.glob("shard_*.jsonl"))
    npz_files = list(VECTORS_DIR.glob("shard_*.npz"))
    chunk_count = sum(sum(1 for _ in open(f, "r", encoding="utf-8")) for f in jsonl_files)
    return f"Shards: {len(jsonl_files)}, Vectors: {len(npz_files)}, Chunks: {chunk_count}"

def get_vector_status():
    index_kb = SHARD_INDEX_PATH.stat().st_size // 1024 if SHARD_INDEX_PATH.exists() else 0
    total_bytes = sum(f.stat().st_size for f in VECTORS_DIR.glob("*"))
    return f"Index size: {index_kb} KB, Total vector memory: {total_bytes / (1024 * 1024):.2f} MB"

# === DISPATCH ===
def handle_command(prompt: str) -> str | None:
    try:
        cmd = prompt.lower().strip()

        match cmd:
            case "yes" if online_status["awaiting_user"] and online_status["connected"]:
                online_status.update({"offline_mode": False, "awaiting_user": False})
                return format_sapphira_response("Back ONLINE. Internet features re-enabled.")

            case "no" if online_status["awaiting_user"]:
                online_status.update({"offline_mode": True, "awaiting_user": False})
                return format_sapphira_response("Remaining OFFLINE. You can type /connect to reconnect manually.")

            case "/connect":
                if has_internet_connection():
                    online_status.update({"connected": True, "offline_mode": False, "awaiting_user": False})
                    return format_sapphira_response("Successfully reconnected. Online mode active.")
                return format_sapphira_response("Reconnection failed. Still offline. Check your network connection.")

            case "/offline":
                online_status.update({"offline_mode": True, "connected": False, "awaiting_user": False})
                if not has_internet_connection():
                    return format_sapphira_response("Internet was already disconnected. Offline mode activated.")
                return format_sapphira_response("You are now OFFLINE. Internet will not be used until you type /connect.")

            case "/net status":
                return format_sapphira_response(
                    f"Online: {'Yes' if online_status['connected'] else 'No'} | Offline Mode: {'Enabled' if online_status['offline_mode'] else 'Disabled'}")

            case "/forget":
                clear_memory()
                return format_sapphira_response("Conversation memory has been cleared.")

            case "/remember on" | "/remember off":
                return format_sapphira_response("Conversation memory is always ON.")

            case "/memory status":
                return format_sapphira_response(memory_status())

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

            case "/learn all":
                start = time.time()
                learned = learn_all_supported_files()
                return format_sapphira_response(
                    f"Learned from {len(learned)} files in {time.time() - start:.2f}s: {', '.join(learned)}")

            case "/learn summary":
                return format_sapphira_response(get_learned_summary())

            case "/vector status":
                return format_sapphira_response(get_vector_status())

            case "/ocr test":
                return format_sapphira_response(ocr_test())

            case _ if cmd.startswith("/ocr scan"):
                args = prompt.split(maxsplit=2)
                return format_sapphira_response(ocr_scan_file(args[2]) if len(args) > 2 else "Usage: /ocr scan <filename>")

            case "/ocr extract all":
                return format_sapphira_response(f"OCR complete: {', '.join(ocr_extract_all())}")

            case "/config show":
                return format_sapphira_response(json.dumps(config, indent=2))

            case "/config reload":
                with CONFIG_PATH.open("r", encoding="utf-8") as f:
                    config.update(json.load(f))
                return format_sapphira_response("Config reloaded.")

            case "/knowledge status":
                kdir = Path("D:/offline_codebot_prototype/knowledge")
                files = sorted(kdir.glob("*"))
                return format_sapphira_response("\n".join(f.name for f in files) if files else "No knowledge files loaded.")

            case "/help":
                return format_sapphira_response(HELP_TEXT.strip())

# === HANDLE COMMAND ===
def handle_command(prompt: str) -> Optional[str]:
    try:
        cmd = prompt.lower().strip()

        if any(q in cmd for q in ["what is today", "what's today", "what is the date", "today's date"]):
            return format_sapphira_response(f"Today is {get_local_date()}.")

        if any(q in cmd for q in ["what time is it", "current time", "what is the time", "date and time", "time and date"]):
            return format_sapphira_response(f"Current system time is {get_local_time()}.")

        return None

    except Exception as e:
        log_error(e)
        return format_sapphira_response(f"Error: {e}")
