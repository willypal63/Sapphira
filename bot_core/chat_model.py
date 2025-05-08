from llama_cpp import Llama
from config import MISTRAL_PATH

# Load the Mistral model
chat_model = Llama(
    model_path=MISTRAL_PATH,
    n_ctx=4096,
    n_threads=8,
    n_batch=64,
    n_gpu_layers=0
)

def generate_chat(prompt: str) -> str:
    """
    Uses the Mistral 7B model to generate a response for general conversation and reasoning tasks.
    """
    result = chat_model(prompt, max_tokens=512, stop=["User:", "###"])
    return result["choices"][0]["text"].strip()
