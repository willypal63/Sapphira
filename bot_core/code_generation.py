"""
This module provides code generation and patching utilities for the assistant, powered by llama-cpp-python.
Make sure you have your GGUF model file locally and set the LLM_MODEL_PATH environment variable if needed.
Includes robust error handling and fallback logic for offline inference.
"""
import os
from pathlib import Path
import logging
from llama_cpp import Llama, LlamaError

from bot_core.formatting import format_user_input
from bot_core.logger_utils import log_error

# === Configuration ===
MODEL_PATH = Path(os.getenv("LLM_MODEL_PATH", "models/CodeLLaMA-13B-Q4_K_M.gguf"))
LLM_CTX = int(os.getenv("LLM_CTX", "2048"))
FALLBACK_MODEL = Path(os.getenv("FALLBACK_LLM_MODEL", "models/CodeLLaMA-7B-Q4_K_M.gguf"))

# Configure local logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === LLM Client Setup ===
llm = None

try:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    logger.info(f"Loading model from {MODEL_PATH}")
    llm = Llama(model_path=str(MODEL_PATH), n_ctx=LLM_CTX, verbose=False)
except Exception as init_err:
    log_error(init_err)
    # Attempt fallback
    try:
        if FALLBACK_MODEL.is_file():
            logger.warning(f"Primary model load failed, loading fallback model {FALLBACK_MODEL}")
            llm = Llama(model_path=str(FALLBACK_MODEL), n_ctx=LLM_CTX, verbose=False)
        else:
            raise FileNotFoundError(
                f"Fallback model not found at {FALLBACK_MODEL}"
            )
    except Exception as fallback_err:
        log_error(fallback_err)
        llm = None
        logger.error("No usable LLM model available. Code generation will be disabled.")


def ai_generate(prompt: str, max_tokens: int = 1024, temperature: float = 0.2) -> str:
    """
    Core wrapper to call the LLM and return the generated text.
    Returns an error message if inference fails or no model is loaded.
    """
    if llm is None:
        err_msg = "Error: No LLM model loaded for inference."
        logger.error(err_msg)
        return err_msg

    try:
        response = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["\n```"],
        )
        choice = response.get("choices", [{}])[0]
        text = choice.get("text") or choice.get("message", {}).get("content")
        return text or ""
    except LlamaError as e:
        log_error(e)
        return f"LLM inference error: {e}"
    except Exception as e:
        log_error(e)
        return f"Unexpected error during inference: {e}"


def generate_file(description: str, language: str) -> str:
    """
    Generate a full source file in the specified language based on the provided description.
    Returns the code as a string or an error message.
    """
    prompt = format_user_input(
        f"Generate a complete {language} file that does the following: {description}\n"
        "Include necessary imports or boilerplate, and output the code within code fences."
    )
    result = ai_generate(prompt, max_tokens=2048)
    if result.startswith("Error"):
        return result
    return result


def generate_patch(original_code: str, patch_description: str) -> str:
    """
    Produce a patched version of original_code applying patch_description.
    Returns the patched code as a string or an error message.
    """
    prompt = format_user_input(
        f"Here is the original code:\n```\n{original_code}\n```\n"
        f"Please apply the following changes: {patch_description}\n"
        "Output only the full updated file inside code fences."
    )
    result = ai_generate(prompt, max_tokens=2048)
    if result.startswith("Error"):
        return result
    return result
