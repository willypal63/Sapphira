# bot_core/file_ingestor.py

import logging
from pathlib import Path
import magic

from bot_core.constants_config import ALLOWED_EXTS, IMPORT_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize python-magic for MIME detection
_mime = magic.Magic(mime=True)


def discover_files(root: Path) -> list[Path]:
    """
    Recursively discover all files under `root` matching known extensions.
    """
    files = [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS
    ]
    logger.info(f"Discovered {len(files)} files for ingestion under {root}")
    return files


def detect_mime(path: Path) -> str:
    """
    Return the true MIME type of a file using libmagic.
    """
    try:
        return _mime.from_file(str(path))
    except Exception as e:
        logger.warning(f"MIME detection failed for {path}: {e}")
        return "application/octet-stream"


def normalize(path: Path) -> tuple[str, any]:
    """
    Normalize file content based on its MIME type.
    Returns a tuple of (kind, payload):
      - kind="text" and payload=str
      - kind="table" and payload=str
      - kind="media" and payload=dict metadata
    """
    mime_type = detect_mime(path)

    # Text files and JSON
    if mime_type.startswith("text/") or mime_type == "application/json":
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            return "text", text
        except Exception as e:
            logger.error(f"Failed to read text from {path}: {e}")
            return "media", {"path": str(path), "mime": mime_type}

    # Spreadsheets and CSV/TSV
    if "spreadsheet" in mime_type or path.suffix.lower() in (".csv", ".tsv"):
        try:
            import pandas as pd
            df = (
                pd.read_excel(path, engine="openpyxl")
                if path.suffix.lower() != ".csv"
                else pd.read_csv(path)
            )
            table_text = "\n".join(
                df.astype(str).agg(" | ".join, axis=1)
            )
            return "table", table_text
        except Exception as e:
            logger.error(f"Failed to parse table from {path}: {e}")
            return "media", {"path": str(path), "mime": mime_type}

    # Images and PDFs for OCR
    if mime_type.startswith("image/") or mime_type == "application/pdf":
        try:
            from PIL import Image
            import pytesseract
            text = ""
            if mime_type == "application/pdf":
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        text += (page.extract_text() or "") + "\n"
            else:
                img = Image.open(path)
                text = pytesseract.image_to_string(img)
            return "text", text
        except Exception as e:
            logger.error(f"OCR failed for {path}: {e}")
            return "media", {"path": str(path), "mime": mime_type}

    # Fallback: treat as media/metadata
    metadata = {"path": str(path), "mime": mime_type, "size": path.stat().st_size}
    return "media", metadata


def ingest_directory(root: Path) -> None:
    """
    Ingest all supported files under `root`, delegating to learning or media tools.
    """
    files = discover_files(root)
    for path in files:
        kind, payload = normalize(path)
        if kind == "text":
            from bot_core.learning import learn_text
            learn_text(payload)
        elif kind == "table":
            from bot_core.learning import learn_table
            learn_table(payload)
        else:
            from bot_core.knowledge_tools import ingest_media_metadata
            ingest_media_metadata(payload)


def ingest_root() -> None:
    """
    Convenience entrypoint: ingest from the configured import directory.
    """
    ingest_directory(Path(IMPORT_DIR))


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Discover and ingest files into the learning pipeline."
    )
    parser.add_argument(
        "root", type=Path, nargs="?", default=Path(IMPORT_DIR),
        help="Root directory to scan for files"
    )
    args = parser.parse_args()
    ingest_directory(args.root)
