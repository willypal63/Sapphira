# bot_core/memory_vector_store.py

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from bot_core.logger_utils import log_error
from bot_core.paths import LEARNING_DATA_PATH

VECTOR_DB = Path("memory/learned_memory_vectors.jsonl")
MEMORY_FILE = Path("memory/learned_memory.txt")
EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")

def build_vector_store():
    try:
        if not MEMORY_FILE.exists():
            return

        chunks = MEMORY_FILE.read_text(encoding="utf-8", errors="ignore").split("\n\n")
        VECTOR_DB.unlink(missing_ok=True)

        with VECTOR_DB.open("w", encoding="utf-8") as out:
            for chunk in chunks:
                if chunk.strip():
                    embedding = EMBEDDER.encode(chunk.strip()).tolist()
                    out.write(json.dumps({"text": chunk.strip(), "embedding": embedding}) + "\n")

    except Exception as e:
        log_error(f"Failed to build vector store: {e}")

def search_memory(query: str, top_k=3):
    try:
        if not VECTOR_DB.exists():
            return []

        query_vec = EMBEDDER.encode(query)
        results = []

        with VECTOR_DB.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    sim = util.cos_sim(query_vec, record["embedding"])[0][0].item()
                    results.append((sim, record["text"]))
                except Exception as parse_err:
                    log_error(f"Failed to parse memory vector line: {parse_err}")

        results.sort(reverse=True)
        return [text for _, text in results[:top_k]]

    except Exception as e:
        log_error(f"Search failed: {e}")
        return []
