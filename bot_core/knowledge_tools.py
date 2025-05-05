# bot_core/knowledge_tools.py

from pathlib import Path
import shutil
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from bot_core.logger_utils import log_error, log_info
from bot_core.memory import conversation_history, save_conversation, export_conversation
from bot_core.paths import LEARNING_DATA_PATH
from bot_core.constants_config import allowed_exts
from bot_core.epub_converter import epub_to_text
from bot_core.memory_vector_store import build_vector_store
from loguru import logger as training_logger

# Training log path
TRAIN_LOG = Path("logs/training_log.txt")
training_logger.add(str(TRAIN_LOG), level="INFO")

ARCHIVE_PATH = LEARNING_DATA_PATH / "archive"
ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)

def move_to_archive(file_path):
    try:
        shutil.move(str(file_path), str(ARCHIVE_PATH / file_path.name))
        log_info(f"Archived: {file_path.name}")
    except Exception as e:
        log_error(e, f"Failed to archive: {file_path.name}")

def learn_ocr_files():
    learned = []
    for f in Path(LEARNING_DATA_PATH).glob("*.ocr.txt"):
        if f.is_dir() or f.parent.name == "archive":
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if content.strip():
                with open("memory/learned_memory.txt", "a", encoding="utf-8") as mem:
                    mem.write(f"### {f.name}\n{content.strip()}\n")
                conversation_history.append(f"USER: [imported file] {f.name}\n{content.strip()}")
                learned.append(f.name)
                move_to_archive(f)
                training_logger.info(f"Learned OCR: {f.name}")
            else:
                training_logger.info(f"Skipped empty OCR: {f.name}")
        except Exception as e:
            log_error(e, f"/learn ocr failed on {f.name}")
    save_conversation()
    if learned:
        export_path = export_conversation()
        log_info(f"Auto-exported memory to: {export_path}")
        build_vector_store()
        log_info("🔄 Rebuilt memory vector store after learning OCR files.")
    return learned

def learn_all_supported_files():
    log_info("📂 Starting file scan in learning path...")
    learned = []
    for f in Path(LEARNING_DATA_PATH).glob("*"):
        if f.is_dir() or f.parent.name == "archive":
            continue
        training_logger.info(f"📄 Checking: {f.name}")
        try:
            content = ""
            if f.suffix.lower() in allowed_exts:
                content = f.read_text(encoding="utf-8", errors="ignore")
            elif f.suffix.lower() == ".pdf":
                reader = PdfReader(str(f))
                content = "".join((page.extract_text() or "") for page in reader.pages)
                if not content.strip():
                    images = convert_from_path(str(f))
                    content = "".join(pytesseract.image_to_string(img, lang="eng", config="--psm 3") for img in images)
            elif f.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                content = pytesseract.image_to_string(Image.open(f), lang="eng", config="--psm 3")
            elif f.suffix.lower() == ".epub":
                txt_out = f.with_name(f.stem + ".converted.txt")
                epub_to_text(f, txt_out)
                content = txt_out.read_text(encoding="utf-8", errors="ignore")

            if content.strip():
                training_logger.info(f"Learned: {f.name}")
                conversation_history.append(f"USER: [imported file] {f.name}\n{content.strip()}")
                learned.append(f.name)
                move_to_archive(f)
            else:
                training_logger.info(f"Skipped empty or unhandled: {f.name}")
        except Exception as e:
            log_error(e, f"learn_all_supported_files failed on {f.name}")
    save_conversation()
    result_msg = f"✅ Learned from: {', '.join(learned)}" if learned else "⚠️ No learnable files found."
    log_info(result_msg)
    if learned:
        export_path = export_conversation()
        log_info(f"Auto-exported memory to: {export_path}")
        build_vector_store()
        log_info("🔄 Rebuilt memory vector store after learning all supported files.")
    return result_msg
