# bot_core/epub_converter.py

from ebooklib import epub
from bs4 import BeautifulSoup
from pathlib import Path
from bot_core.logger_utils import log_error, log_info
import ebooklib

def epub_to_text(epub_path: Path, output_path: Path):
    """
    Convert an .epub file to plain .txt format.

    Parameters:
    - epub_path: Path to the .epub file
    - output_path: Path to save the .txt file
    """
    try:
        book = epub.read_epub(str(epub_path))
        texts = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                texts.append(soup.get_text())

        output_path.write_text("\n".join(texts), encoding="utf-8")

        if output_path.exists() and output_path.stat().st_size > 0:
            log_info(f"EPUB successfully converted and verified: {epub_path.name} -> {output_path.name}")
        else:
            log_error("EPUB output file empty or missing", f"Post-write verification failed: {output_path.name}")
            return None

        return output_path
    except Exception as e:
        log_error(e, f"Failed to convert EPUB: {epub_path.name}")
        return None
