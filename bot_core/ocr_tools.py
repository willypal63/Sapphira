# bot_core/ocr_tools.py

from pathlib import Path
from PIL import Image, ImageDraw
import pytesseract
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

from bot_core.memory import conversation_history, save_conversation
from bot_core.logger_utils import log_error, log_info
from bot_core.paths import LEARNING_DATA_PATH
from bot_core.constants_config import allowed_exts

def ocr_test():
    try:
        img = Image.new("RGB", (200, 50), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "OCR OK", fill=(0, 0, 0))
        result = pytesseract.image_to_string(img).strip()
        log_info(f"OCR test successful: '{result}'")
        return f"OCR test result: '{result}'"
    except Exception as e:
        log_error(e, "OCR test failed")
        return f"OCR test failed: {e}"

def ocr_scan_file(name: str):
    target = Path(LEARNING_DATA_PATH) / name
    if not target.exists():
        log_error("Missing file", f"OCR scan requested on missing file: {name}")
        return f"File not found: {name}"
    try:
        if target.suffix.lower() == ".pdf":
            images = convert_from_path(str(target))
            text = pytesseract.image_to_string(images[0]) if images else ""
        else:
            text = pytesseract.image_to_string(Image.open(target))
        preview = text.strip().splitlines()[0] if text.strip() else "(no text found)"
        log_info(f"OCR preview extracted from {name}: {preview}")
        return f"OCR preview from {name}: {preview}"
    except Exception as e:
        log_error(e, f"OCR scan failed on file: {name}")
        return f"OCR scan failed: {e}"

def ocr_extract_all():
    extracted = []
    for f in Path(LEARNING_DATA_PATH).glob("*"):
        try:
            if f.suffix.lower() == ".pdf":
                images = convert_from_path(str(f))
                full_text = "".join(pytesseract.image_to_string(img) for img in images)
            elif f.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                full_text = pytesseract.image_to_string(Image.open(f))
            else:
                continue
            out_file = f.with_suffix(".ocr.txt")
            out_file.write_text(full_text, encoding="utf-8")
            extracted.append(f.name)
            preview_line = full_text.strip().splitlines()[0] if full_text.strip() else "(no content extracted)"
            log_info(f"Trained on: {f.name} | Saved as: {out_file.name} | Preview: {preview_line}")
        except Exception as e:
            log_error(e, f"/ocr extract failed on {f.name}")
    log_info(f"OCR completed for {len(extracted)} files.")
    return extracted

