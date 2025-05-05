# bot_core/memory_vector_store.py

"""
Sharded vector store with shard-level metadata index.
Splits embeddings into multiple JSONL shards when exceeding size thresholds.
Maintains a shard index of average embeddings for quick branch pruning during search.
Supports efficient hybrid format with JSONL for text and NPZ for float vectors.
"""
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import numpy as np
from bot_core.logger_utils import log_error

VECTORS_DIR = Path("memory/vectors")
SHARD_INDEX_PATH = Path("memory/shard_index.json")
PROCESSED_COUNT_PATH = Path("memory/processed_count.txt")

VECTORS_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
MAX_SHARD_SIZE = 75 * 1024 * 1024


def _get_shard_files():
    return sorted(VECTORS_DIR.glob("shard_*.jsonl"))


def _get_text_and_ids(shard_path):
    texts = []
    ids = []
    with shard_path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            texts.append(obj["text"])
            ids.append(obj["id"])
    return ids, texts


def build_vector_store():
    index = {}
    total_chunks = 0
    for shard in tqdm(_get_shard_files(), desc="Encoding shards", unit="shard", ncols=80):
        try:
            ids, texts = _get_text_and_ids(shard)
            embeddings = EMBEDDER.encode(texts, convert_to_numpy=True)
            shard_npz = VECTORS_DIR / shard.name.replace(".jsonl", ".npz")
            np.savez_compressed(shard_npz, embeddings=embeddings)
            index[shard.name] = np.mean(embeddings, axis=0).tolist()
            total_chunks += len(ids)
        except Exception as e:
            log_error(f"Failed processing {shard.name}: {e}")

    try:
        with SHARD_INDEX_PATH.open("w", encoding="utf-8") as f:
            json.dump(index, f)
        PROCESSED_COUNT_PATH.write_text(str(total_chunks))
    except Exception as e:
        log_error(f"Failed writing shard index or processed count: {e}")


def search_memory(query: str, top_k: int = 3) -> list[str]:
    try:
        if SHARD_INDEX_PATH.exists():
            with SHARD_INDEX_PATH.open("r", encoding="utf-8") as f:
                index = json.load(f)
        else:
            index = {}

        query_vec = EMBEDDER.encode(query)
        shard_sims = []
        for shard_name, avg_vec in index.items():
            try:
                sim = util.cos_sim(query_vec, avg_vec)[0][0].item()
                shard_sims.append((sim, shard_name))
            except Exception:
                continue

        shard_sims.sort(key=lambda x: x[0], reverse=True)
        top_shards = [name for _, name in shard_sims[:2]] if shard_sims else []
        results = []

        for shard_name in top_shards:
            jsonl_path = VECTORS_DIR / shard_name
            npz_path = jsonl_path.with_suffix(".npz")
            try:
                ids, texts = _get_text_and_ids(jsonl_path)
                embeddings = np.load(npz_path)["embeddings"]
                sims = util.cos_sim(query_vec, embeddings)[0].tolist()
                reranked = sorted(zip(sims, texts), key=lambda x: x[0], reverse=True)
                results.extend(reranked)
            except Exception as e:
                log_error(f"Search failed in {shard_name}: {e}")

        results.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in results[:top_k]]

    except Exception as e:
        log_error(f"Search failed: {e}")
        return []

