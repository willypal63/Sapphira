# bot_core/model_llamacpp.py

import re
import json
from pathlib import Path
from llama_cpp import Llama
from bot_core.memory import conversation_history, save_conversation
from config import MODEL_PATH, GPU_LAYERS, N_THREADS, CTX_SIZE, N_BATCH, TEMPERATURE, TOP_P, REPEAT_PENALTY, N_PREDICT

# Load Sapphira's personality profile
def load_profile() -> dict:
    """Load and return Sapphira's personality profile from JSON."""
    profile_path = Path("sapphira_profile.json")
    with profile_path.open("r", encoding="utf-8") as f:
        return json.load(f)

sapphira = load_profile()

# Model settings

_llm: Llama | None = None

def init_llm(config: dict | None = None) -> callable:
    """
    Initialize the LLM, perform a warm-up, and return the response-generating function.
    """
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=CTX_SIZE,
            n_batch=N_BATCH,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repeat_penalty=REPEAT_PENALTY,
            n_gpu_layers=GPU_LAYERS,
            n_threads=N_THREADS,
            verbose=False
    )
        # Warm up model to avoid first-call lag
        _llm("Hello", max_tokens=1, temperature=0.0)
    return generate_response


def clean_repetition(response: str) -> str:
    """Remove duplicate patterns like '1990s, 1990s'."""
    match = re.search(r"(\b\d{4}s\b)(?:, \1)+", response)
    if match:
        return response[:match.start()] + match.group(1)
    return response


def strip_prompt_formatting(text: str) -> str:
    """Strip off USER:, ASSISTANT:, or SAPPHIRA: prefixes."""
    return re.sub(r"^(USER:|ASSISTANT:|SAPPHIRA:)\s*", "", text.strip(), flags=re.IGNORECASE)


def generate_response(prompt: str, verbose: bool = False) -> str:
    """
    Generate a reply using the LLM, post-process, save to memory, and return clean text.
    """
    if _llm is None:
        raise RuntimeError("LLM not initialized; call init_llm() first.")

    if any(tok in prompt.lower() for tok in ("def ", "import ", "class ")):
        prompt += "\n(Please reply in natural language unless I request code.)"

    system_prompt = (
        f"SYSTEM: You are Sapphira, a {sapphira.get('age')}-year-old AI.\n"
        f"Personality: {sapphira.get('personality')}\n"
        f"Quirks: {', '.join(sapphira.get('quirks', []))}\n"
        f"Style: {sapphira.get('style')}\n"
        "Respond naturally in first person; stay in character.\n"
    )
    user_block = f"USER: {prompt}\n"
    full_prompt = system_prompt + user_block

    result = _llm(
        full_prompt,
        max_tokens=N_PREDICT,
        temperature=TEMPERATURE,
        stop=["USER:", "\nSAPPHIRA:"]
    )
    raw = result["choices"][0]["text"].strip()

    cleaned = clean_repetition(raw)
    final = strip_prompt_formatting(cleaned)

    conversation_history.append({"role": "assistant", "content": final})
    save_conversation(conversation_history)

    return final
