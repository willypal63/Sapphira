from llama_cpp import Llama
from config import CODELLAMA_PATH

# Load the CodeLLaMA model
code_model = Llama(
    model_path=CODELLAMA_PATH,
    n_ctx=4096,
    n_threads=8,
    n_batch=64,
    n_gpu_layers=0
)

def generate_code(prompt: str) -> str:
    """
    Uses the CodeLLaMA 13B Instruct model to generate or edit code from prompts.
    """
    result = code_model(prompt, max_tokens=768, stop=["###", "User:"])
    return result["choices"][0]["text"].strip()
