import sys
from llama_cpp import Llama

def main():
    try:
        # Offload just 1 layer to verify cuBLAS is active
        model = Llama(
            model_path="D:/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf",
            n_gpu_layers=1,
            n_threads=1
        )
        print("✅ CUDA support OK!")
    except Exception as e:
        print("❌ CUDA support FAILED:")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
