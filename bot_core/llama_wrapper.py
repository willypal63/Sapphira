# bot_core/llama_wrapper.py — unified logger integration

import time
from llama_cpp import Llama
from pathlib import Path
from bot_core.logger_utils import get_logger

# Configurable constants
MODEL_PATH = "D:/Models/CodeLlama-13B/codellama-13b.Q4_K_M.gguf"
CTX_LEN = 2048
N_THREADS = 4
N_GPU_LAYERS = 0

logger = get_logger()
_llm_instance = None

def load_model():
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    try:
        logger.info("⏳ Loading Llama model from: {}", MODEL_PATH)
        _llm_instance = Llama(
            model_path=MODEL_PATH,
            n_ctx=CTX_LEN,
            n_threads=N_THREADS,
            n_gpu_layers=N_GPU_LAYERS,
            verbose=True,
        )
        logger.success("✅ Llama model initialized")
        return _llm_instance
    except Exception as e:
        logger.exception("❌ Llama init failed: {}", e)
        raise

def generate_response(prompt: str) -> str:
    if not prompt.strip():
        return "[Error: Empty prompt]"

    llm = load_model()
    logger.info("📩 Prompt received: {}", prompt)
    
    start = time.time()
    result = llm(prompt, max_tokens=256, stop=["</s>"])
    end = time.time()

    response = result["choices"][0]["text"].strip()
    duration = end - start
    tokens_used = result.get("usage", {}).get("total_tokens", "[?]")

    logger.info("📨 Response generated: {}", response)
    logger.info("🧠 Tokens used: {} | ⏱️ Time: {:.2f}s", tokens_used, duration)
    return response

