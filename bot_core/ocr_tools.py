# bot_core/ocr_tools.py

import logging
from pathlib import Path
from typing import List

import pytesseract
import pdfplumber
from PIL import Image

from bot_core.constants_config import IMPORT_DIR, ALLOWED_EXTS

# Configure logger
t_logging = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# File extensions supported for OCR\

OCR_EXTS = {ext for ext in ALLOWED_EXTS if ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.svg', '.gif', '.pdf'}}


def ocr_test() -> str:
    """
    Verify that Tesseract OCR is available and return its version.
    """
    try:
        version = pytesseract.get_tesseract_version()
        return f"Tesseract OCR version: {version}"
    except Exception as e:
        t_logging.error(f"OCR test failed: {e}")
        return f"OCR test failed: {e}"


def ocr_scan_file(filename: str) -> str:
    """
    Perform OCR on a single file. Supports images and PDFs.

    Args:
        filename (str): Path to the file to scan (relative or absolute).

    Returns:
        Extracted text or an error message.
    """
    path = Path(filename)
    if not path.exists():
        path = Path(IMPORT_DIR) / filename
    if not path.exists():
        return f"File not found: {filename}"

    ext = path.suffix.lower()
    if ext not in OCR_EXTS:
        return f"Unsupported OCR file type: {ext}"

    try:
        if ext == '.pdf':
            text = ''
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or '') + '\n'
        else:
            img = Image.open(path)
            text = pytesseract.image_to_string(img)
        return text

    except Exception as e:
        t_logging.error(f"OCR failed for {path}: {e}")
        return f"OCR failed for {path}: {e}"


def ocr_extract_all() -> List[str]:
    """
    Perform OCR on all supported files in the IMPORT_DIR directory.

    Returns:
        List of output filenames (text files) created from OCR.
    """
    results: List[str] = []
    base = Path(IMPORT_DIR)

    for path in base.rglob('*'):
        if path.suffix.lower() in OCR_EXTS:
            out_name = f"{path.stem}_ocr.txt"
            out_path = base / out_name
            t_logging.info(f"Extracting OCR from {path} to {out_path}")
            text = ocr_scan_file(str(path))
            out_path.write_text(text, encoding='utf-8')
            results.append(out_name)

    return results
