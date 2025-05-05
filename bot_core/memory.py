# bot_core/memory.py

from pathlib import Path
from sentence_transformers import SentenceTransformer
import json

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_PATH = Path("embeddings")
MEMORY_TXT_PATH = Path("memory/learned_memory.txt")
MEMORY_VECTOR_PATH = Path("memory/learned_memory_vectors.jsonl")

model = SentenceTransformer(MODEL_NAME)

CONVO_PATH = Path("memory/conversation.json")
conversation_history = []

if CONVO_PATH.exists():
    with open(CONVO_PATH, "r", encoding="utf-8") as f:
        try:
            conversation_history = json.load(f)
        except json.JSONDecodeError:
            conversation_history = []

def save_conversation(convo):
    with open(CONVO_PATH, "w", encoding="utf-8") as f:
        json.dump(convo, f, indent=2)

def build_embeddings():
    if not MEMORY_TXT_PATH.exists():
        return "No memory file found."

    text = MEMORY_TXT_PATH.read_text(encoding="utf-8", errors="ignore")
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    vectors = model.encode(chunks).tolist()

    with open(MEMORY_VECTOR_PATH, "w", encoding="utf-8") as f:
        for chunk, vector in zip(chunks, vectors):
            entry = {"text": chunk, "vector": vector}
            f.write(json.dumps(entry) + "\n")

    return f"Indexed {len(vectors)} memory chunks."

def query_embeddings(query, top_k=5):
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    if not MEMORY_VECTOR_PATH.exists():
        return []

    vectors = []
    texts = []

    with open(MEMORY_VECTOR_PATH, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            texts.append(data["text"])
            vectors.append(data["vector"])

    if not vectors:
        return []

    query_vec = model.encode([query])
    scores = cosine_similarity(query_vec, vectors)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [texts[i] for i in top_indices]

def cold_start_build():
    if MEMORY_VECTOR_PATH.exists():
        return True
    return build_embeddings() != "No memory file found."
