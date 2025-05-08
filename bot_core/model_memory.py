from llama_cpp import Llama
from config import PHI2_PATH

# Load the Phi-2 model
memory_model = Llama(
    model_path=PHI2_PATH,
    n_ctx=2048,
    n_threads=8,
    n_batch=32,
    n_gpu_layers=0
)

def summarize_or_retrieve(prompt: str) -> str:
    """
    Uses the Phi-2 model to summarize input text or help answer memory-related questions.
    """
    result = memory_model(prompt, max_tokens=512, stop=["###", "User:"])
    return result["choices"][0]["text"].strip()
