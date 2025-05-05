# verify_gpu.py
# Run this to check if llama-cpp-python is using GPU acceleration

from llama_cpp import Llama
import subprocess
import sys

try:
    # Print basic info
    print("✅ llama_cpp.Llama loaded successfully")
    print("------------------------------------")
    print("Llama class docstring:")
    print(Llama.__doc__ or "[no docstring found]")

    # Optional: run a subprocess to check for nvidia-smi (GPU status)
    print("\n📊 NVIDIA GPU status (nvidia-smi):")
    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    print(result.stdout if result.returncode == 0 else result.stderr)

except Exception as e:
    print(f"❌ Failed to verify llama-cpp GPU support: {e}", file=sys.stderr)

input("\nPress Enter to close...")
