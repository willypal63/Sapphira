# bot_core/learning.py

from pathlib import Path
import shutil
import os
from bot_core.paths import LEARNING_DATA_PATH
from bot_core.logger_utils import log_error, log_info
from bot_core.memory_vector_store import build_vector_store

SUPPORTED_EXTS = [".txt", ".md", ".html"]
ARCHIVE_PATH = LEARNING_DATA_PATH.parent / "archive"
ARCHIVE_PATH.mkdir(exist_ok=True)
MAX_CHUNK_CHARS = 800


def chunk_text(text, max_len=MAX_CHUNK_CHARS):
    lines = text.splitlines()
    chunks = []
    buffer = ""
    for line in lines:
        if len(buffer) + len(line) + 1 > max_len:
            chunks.append(buffer.strip())
            buffer = line
        else:
            buffer += "\n" + line
    if buffer.strip():
        chunks.append(buffer.strip())
    return chunks


def learn_all_supported_files():
    learned = []
    try:
        for file in Path(LEARNING_DATA_PATH).glob("*"):
            if file.suffix.lower() in SUPPORTED_EXTS:
                text = file.read_text(encoding="utf-8", errors="ignore")
                chunks = chunk_text(text)
                with open("memory/learned_memory.txt", "a", encoding="utf-8") as f:
                    for chunk in chunks:
                        f.write(chunk + "\n\n")
                learned.append(file.name)
                shutil.move(str(file), ARCHIVE_PATH / file.name)
        if learned:
            build_vector_store()
            # log_info removed} file(s): {', '.join(learned)}")
        else:
            log_info("No learnable files found.")
    except Exception as e:
        log_error(f"Learning failed: {e}")
    return learned if learned else "No learnable files found."


def learn_from_text_file(file_path: Path):
    try:
        if file_path.suffix.lower() in SUPPORTED_EXTS:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            chunks = chunk_text(text)
            with open("memory/learned_memory.txt", "a", encoding="utf-8") as f:
                for chunk in chunks:
                    f.write(chunk + "\n\n")
            build_vector_store()
            shutil.move(str(file_path), ARCHIVE_PATH / file_path.name)
            log_info(f"Learned from file: {file_path.name}")
            return f"Learned from {file_path.name}"
        else:
            return f"Unsupported file type: {file_path.suffix}"
    except Exception as e:
        log_error(f"Learning from file failed: {e}")
        return f"Failed to learn from {file_path.name}"


def learn_from_archive():
    learned = []
    try:
        for file in ARCHIVE_PATH.glob("*"):
            if file.suffix.lower() in SUPPORTED_EXTS:
                text = file.read_text(encoding="utf-8", errors="ignore")
                chunks = chunk_text(text)
                with open("memory/learned_memory.txt", "a", encoding="utf-8") as f:
                    for chunk in chunks:
                        f.write(chunk + "\n\n")
                learned.append(file.name)
        if learned:
            build_vector_store()
            log_info(f"Re-learned from archive: {', '.join(learned)}")
        else:
            log_info("No learnable files found in archive.")
    except Exception as e:
        log_error(f"Learning from archive failed: {e}")
    return learned if learned else "No learnable files found in archive."


def learn_ocr_files():
    log_info("OCR learning stub invoked — functionality not implemented.")
    return "OCR learning is not currently supported in this build."


def reset_memory():
    try:
        for path in ["memory/learned_memory.txt", "memory/learned_memory_vectors.jsonl"]:
            if os.path.exists(path):
                os.remove(path)
        embed_dir = Path("embeddings")
        if embed_dir.exists():
            for file in embed_dir.glob("*"):
                file.unlink()
        log_info("Memory and embeddings reset.")
        return "✅ Memory and embeddings have been reset."
    except Exception as e:
        log_error(f"Reset memory failed: {e}")
        return f"❌ Failed to reset memory: {e}"
