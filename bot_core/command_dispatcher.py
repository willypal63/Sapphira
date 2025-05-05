from bot_core.memory import (
    conversation_history,
    save_conversation,
    clear_conversation,
    export_conversation
)
from bot_core.logger_utils import log_error, log_info
from bot_core.constants_config import HELP_TEXT
from bot_core.ocr_tools import ocr_test, ocr_scan_file, ocr_extract_all
from bot_core.learning import learn_ocr_files, learn_all_supported_files
from pathlib import Path
from loguru import logger as training_logger
import json
import os

CONFIG_PATH = Path("D:/offline_codebot_prototype/config.json")
EXPORT_DIR = Path("D:/offline_codebot_prototype/logs/exports")
TRAIN_LOG = Path("logs/training_log.txt")
training_logger.add(str(TRAIN_LOG), level="INFO")

with CONFIG_PATH.open("r") as f:
    config = json.load(f)

def handle_command(prompt: str):
    try:
        match prompt.lower().strip():
            case "/forget":
                clear_conversation()
                log_info("Conversation memory cleared by user command.")
                return "Conversation memory has been cleared."

            case "/remember off":
                return "Conversation memory is always ON."

            case "/remember on":
                return "Conversation memory is always ON."

            case "/memory status":
                return "Conversation memory is currently ENABLED."

            case "/memory export":
                path = export_conversation()
                log_info(f"Memory exported to: {path}")
                return f"Conversation memory exported to: {path}"

            case "/memory list":
                files = sorted(EXPORT_DIR.glob("exported_memory_*.txt"), reverse=True)
                return "Available memory export files:\n" + "\n".join(f.name for f in files) if files else "No memory exports found."

            case "/memory open":
                latest = sorted(EXPORT_DIR.glob("exported_memory_*.txt"), reverse=True)
                if latest:
                    os.startfile(latest[0])
                    log_info(f"Opened memory file: {latest[0].name}")
                    return f"Opened latest memory export: {latest[0].name}"
                return "No memory exports found."

            case "/offline on":
                log_info("Offline mode activated.")
                return "Offline mode ENABLED. All online features will be bypassed."

            case "/offline off":
                log_info("Offline mode deactivated.")
                return "Offline mode DISABLED."

            case "/config show":
                return json.dumps(config, indent=2)

            case "/config reload":
                try:
                    with CONFIG_PATH.open("r") as f:
                        config.update(json.load(f))
                    log_info("Configuration reloaded from config.json")
                    return "Config reloaded successfully."
                except Exception as e:
                    log_error(e, "Reloading config")
                    return f"Failed to reload config: {e}"

            case "/help":
                return HELP_TEXT.strip()

            case "/knowledge status":
                return knowledge_status()

            case "/learn all":
                learned = learn_all_supported_files()
                log_info(f"Learned from {len(learned)} files: {', '.join(learned)}")
                training_logger.info(f"Learned from: {', '.join(learned)}")
                return f"Learned from: {', '.join(learned)}" if learned else "No learnable files found."

            case "/ocr test":
                return ocr_test()

            case p if p.startswith("/ocr scan"):
                parts = p.split(maxsplit=2)
                if len(parts) < 3:
                    return "Usage: /ocr scan <filename>"
                return ocr_scan_file(parts[2])

            case "/ocr extract all":
                extracted = ocr_extract_all()
                log_info(f"OCR extracted from {len(extracted)} files.")
                return f"OCR complete for: {', '.join(extracted)}" if extracted else "No OCR-compatible files found."

            case "/learn ocr":
                learned = learn_ocr_files()
                log_info(f"Learned from OCR: {len(learned)} files deleted.")
                training_logger.info(f"Learned OCR files: {', '.join(learned)}")
                return f"Learned and deleted: {', '.join(learned)}" if learned else "No .ocr.txt files to learn."

        return None  # Not a command

    except Exception as e:
        log_error(e, f"Command handling failed for prompt: {prompt}")
        return f"An error occurred while processing the command: {e}"

