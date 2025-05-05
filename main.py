# main.py

import platform
from pathlib import Path
import datetime
import json

FALLBACK_LOG = Path("logs/boot_errors.log")
FALLBACK_LOG.parent.mkdir(exist_ok=True)

def fallback_log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(FALLBACK_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

try:
    import psutil
    import GPUtil
    from bot_core.interface import command_loop
    from bot_core.model_llamacpp import load_model
    from bot_core.paths import ensure_directories, LEARNING_DATA_PATH
    from bot_core.logger_utils import log_error
    from bot_core.memory import cold_start_build
    from bot_core.memory_vector_store import build_vector_store
except Exception as e:
    fallback_log(f"CRITICAL IMPORT FAILURE: {e}")
    raise

def log_system_specs():
    try:
        mem = psutil.virtual_memory()
        _ = mem.total
        _ = GPUtil.getGPUs()
    except Exception as e:
        log_error(f"Failed to gather system specs: {e}")

def safe_boot_sequence():
    try:
        if cold_start_build():
            return True
        VECTOR_DB = Path("memory/learned_memory_vectors.jsonl")
        init_entry = {"meta": "__init__", "message": "Cold start initialized new vector store."}
        VECTOR_DB.write_text(json.dumps(init_entry) + "\n", encoding="utf-8")
        return True
    except Exception as e:
        fallback_log(f"Vector DB boot sequence failure: {e}")
        log_error(f"Vector DB boot failure: {e}")
        return False

def main():
    try:
        log_system_specs()
        ensure_directories()

        if not safe_boot_sequence():
            return

        generator = load_model()
        command_loop(generator)

    except Exception as e:
        fallback_log(f"Unhandled startup error: {e}")
        log_error(f"[MAIN CRASH] {e}")

if __name__ == "__main__":
    main()
