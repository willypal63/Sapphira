# bot_core/model_llamacpp.py

import json
import re
from pathlib import Path
from llama_cpp import Llama
from bot_core.memory import conversation_history, save_conversation

# Load Sapphira's personality profile
def load_profile() -> dict:
    """Load and return Sapphira's personality profile from JSON."""
    profile_path = Path("sapphira_profile.json")
    with profile_path.open("r", encoding="utf-8") as f:
        return json.load(f)

sapphira = load_profile()

# Model settings
MODEL_PATH = Path("D:/Models/CodeLlama-13B/codellama-13b.Q4_K_M.gguf")
N_CTX = 16384
N_GPU_LAYERS = 0
N_THREADS = 4

_llm: Llama | None = None

def init_llm(config: dict | None = None) -> callable:
    """
    Initialize the LLM, perform a warm-up, and return the response-generating function.
    """
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=N_CTX,
            n_gpu_layers=N_GPU_LAYERS,
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

    # Hint for code requests
    if any(tok in prompt.lower() for tok in ("def ", "import ", "class ")):
        prompt += "\n(Please reply in natural language unless I request code.)"

    # Build system + user prompt
    system_prompt = (
        f"SYSTEM: You are Sapphira, a {sapphira.get('age')}-year-old AI.\n"
        f"Personality: {sapphira.get('personality')}\n"
        f"Quirks: {', '.join(sapphira.get('quirks', []))}\n"
        f"Style: {sapphira.get('style')}\n"
        "Respond naturally in first person; stay in character.\n"
    )
    user_block = f"USER: {prompt}\n"
    full_prompt = system_prompt + user_block

    # Call the model with proper stop tokens
    result = _llm(
        full_prompt,
        max_tokens=256,
        temperature=0.7,
        stop=["\nUSER:", "\nSAPPHIRA:"]
    )
    raw = result["choices"][0]["text"].strip()

    # Post-process the reply
    cleaned = clean_repetition(raw)
    final = strip_prompt_formatting(cleaned)

    # Save to history
    conversation_history.append({"role": "assistant", "content": final})
    save_conversation(conversation_history)

    # Return plain LLM output—no hardcoded prefixes
    return final
