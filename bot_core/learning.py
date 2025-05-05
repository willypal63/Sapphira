# bot_core/learning.py

import json
import fitz  # PyMuPDF
from pathlib import Path
from uuid import uuid4
from bs4 import BeautifulSoup
from ebooklib import epub
from tqdm import tqdm
from bot_core.paths import LEARNING_DATA_PATH

VECTORS_DIR = Path("memory/vectors")
VECTORS_DIR.mkdir(parents=True, exist_ok=True)
MAX_SHARD_SIZE = 75 * 1024 * 1024  # 75 MB

SUPPORTED_EXTS = [".txt", ".md", ".html", ".pdf", ".epub"]
IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"]

class ShardWriter:
    def __init__(self):
        self.current_shard = []
        self.current_size = 0
        self.shard_index = 0

    def _current_shard_path(self):
        return VECTORS_DIR / f"shard_{self.shard_index}.jsonl"

    def write(self, chunk_text):
        chunk_id = str(uuid4())
        record = {"id": chunk_id, "text": chunk_text}
        record_json = json.dumps(record) + "\n"
        encoded = record_json.encode("utf-8")
        size = len(encoded)

        if self.current_size + size > MAX_SHARD_SIZE:
            self._flush()
            self.shard_index += 1

        self.current_shard.append(encoded)
        self.current_size += size

    def _flush(self):
        if not self.current_shard:
            return
        path = self._current_shard_path()
        with open(path, "wb") as f:
            f.writelines(self.current_shard)
        self.current_shard = []
        self.current_size = 0

    def close(self):
        self._flush()


def chunk_text(text: str, max_len: int = 800) -> list[str]:
    lines = text.splitlines()
    chunks: list[str] = []
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


def extract_pdf_text(file_path: Path) -> str:
    doc = fitz.open(str(file_path))
    return "\n".join([page.get_text() for page in doc])


def extract_epub_text(file_path: Path) -> str:
    book = epub.read_epub(str(file_path))
    texts = []
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.content, "html.parser")
            texts.append(soup.get_text())
    return "\n".join(texts)


def learn_all_supported_files() -> list[str]:
    writer = ShardWriter()
    learned = []
    files = list(Path(LEARNING_DATA_PATH).iterdir())
    for file in tqdm(files, desc="Learning files", unit="file", ncols=80):
        ext = file.suffix.lower()
        try:
            if ext in IMAGE_EXTS:
                from bot_core.ocr_tools import ocr_scan_file
                text = ocr_scan_file(str(file)) or ""
            elif ext in [".txt", ".md", ".html"]:
                text = file.read_text(encoding="utf-8", errors="ignore")
            elif ext == ".pdf":
                text = extract_pdf_text(file)
            elif ext == ".epub":
                text = extract_epub_text(file)
            else:
                continue

            if not text.strip():
                continue

            chunks = chunk_text(text)
            for chunk in chunks:
                writer.write(chunk)
            learned.append(file.name)
        except Exception as e:
            from bot_core.logger_utils import log_error
            log_error(f"Failed to learn {file.name}: {e}")
    writer.close()
    return learned

