# bot_core/memory.py

"""
Memory module: handles conversation history, exports, and hybrid vector embeddings with progress feedback.
"""
from pathlib import Path
from sentence_transformers import SentenceTransformer
import json
from datetime import datetime
from bot_core.memory_vector_store import build_vector_store, search_memory

# Paths
CONVO_PATH = Path("memory/conversation.json")
EXPORT_DIR = Path("memory/exports")

# Ensure directories exist
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
CONVO_PATH.parent.mkdir(parents=True, exist_ok=True)

# Load or initialize conversation history
conversation_history: list = []
if CONVO_PATH.exists():
    try:
        with CONVO_PATH.open("r", encoding="utf-8") as f:
            conversation_history = json.load(f)
    except (json.JSONDecodeError, IOError):
        conversation_history = []


def save_conversation(convo: list) -> None:
    with CONVO_PATH.open("w", encoding="utf-8") as f:
        json.dump(convo, f, indent=2)


def clear_memory() -> str:
    conversation_history.clear()
    save_conversation(conversation_history)
    return "Memory cleared."


def memory_status() -> str:
    count = len(conversation_history)
    return f"Memory entries: {count}"


def export_conversation() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = EXPORT_DIR / f"conversation_{timestamp}.json"
    with export_path.open("w", encoding="utf-8") as f:
        json.dump(conversation_history, f, indent=2)
    return str(export_path)


def build_embeddings() -> str:
    try:
        build_vector_store()
        return "✅ Hybrid vector store built."
    except Exception as e:
        return f"❌ Failed to build hybrid store: {e}"


def query_embeddings(query: str, top_k: int = 5) -> list[str]:
    return search_memory(query, top_k=top_k)


def cold_start_build() -> bool:
    try:
        build_vector_store()
        return True
    except:
        return False

