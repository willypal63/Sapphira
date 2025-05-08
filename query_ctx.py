from llama_cpp import Llama

# Paths to your model files
MODEL_PATHS = {
    "mistral-7b-q5_k_m": "D:/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf",
    "codellama-13b-q4_k_m": "D:/models/codellama-13b.Q4_K_M.gguf",
    "phi-2-q5_k_m": "D:/models/phi-2.Q5_K_M.gguf",
}

# Load each model (CPU only) to query its max context size
def main():
    for name, path in MODEL_PATHS.items():
        print(f"Loading {name} from {path}...")
        model = Llama(model_path=path, n_gpu_layers=0, n_threads=1)
        print(f"{name} max context size (n_ctx): {model.n_ctx}\n")

if __name__ == "__main__":
    main()
