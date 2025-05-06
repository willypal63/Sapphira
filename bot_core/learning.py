# bot_core/learning.py

import logging
from pathlib import Path
from typing import List

from bot_core.constants_config import IMPORT_DIR
from bot_core.file_ingestor import ingest_directory, discover_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def learn_text(text: str) -> None:
    """
    Process raw text content for learning purposes.

    Args:
        text (str): The text content to learn from.
    """
    # TODO: implement embedding generation and storage
    length = len(text)
    logger.info(f"learn_text: received text of length {length}")


def learn_table(table_text: str) -> None:
    """
    Process tabular content for learning purposes.

    Args:
        table_text (str): Line-delimited rows with columns separated by '|'.
    """
    # TODO: implement row-wise embedding or structured storage
    row_count = table_text.count("\n") + 1 if table_text else 0
    logger.info(f"learn_table: received table with approximately {row_count} rows")


def learn_all_supported_files(root: Path = Path(IMPORT_DIR)) -> List[Path]:
    """
    Discover and ingest all supported files under the given directory.

    Args:
        root (Path): Directory to scan for files (defaults to IMPORT_DIR).

    Returns:
        List[Path]: Paths of files discovered and ingested.
    """
    logger.info(f"Starting learning pipeline on directory: {root}")
    files = discover_files(root)
    if not files:
        logger.warning(f"No files found in {root} matching allowed extensions.")
    else:
        logger.info(f"Discovered {len(files)} files to learn from.")
    ingest_directory(root)
    return files


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the learning pipeline on an import directory."
    )
    parser.add_argument(
        "--root", type=Path, default=Path(IMPORT_DIR),
        help="Directory to scan and learn from"
    )
    args = parser.parse_args()
    learn_all_supported_files(args.root)
