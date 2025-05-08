import os
import time
import argparse
from llama_cpp import Llama
from bot_core.command_dispatcher import handle_command
from bot_core.memory import save_conversation, conversation_history, build_embeddings, query_embeddings

# ---- Model configurations ----
MODEL_CONFIGS = {
    "codellama-13b-q4_k_m": {"path": "D:models/codellama-13b.Q4_K_M.gguf", "kwargs": {"n_gpu_layers": 0, "n_threads": 88, "n_ctx": 16384}},
    "mistral-7b-q5_k_m": {"path": "D:models/mistral-7b-instruct-v0.2.Q5_K_M.gguf", "kwargs": {"n_gpu_layers": 32, "n_threads": 8, "n_ctx": 8192}},
    "phi-2-q5_k_m":     {"path": "D:models/phi-2.Q5_K_M.gguf", "kwargs": {"n_gpu_layers": 0, "n_threads": 88, "n_ctx": 2048}},
}

class Sapphira:
    def __init__(self):
        # Load all models
        self.models = {}
        for name, cfg in MODEL_CONFIGS.items():
            print(f"Loading {name} (ctx={cfg['kwargs']['n_ctx']})...")
            self.models[name] = Llama(model_path=cfg['path'], **cfg['kwargs'])

    def index_text(self, text: str):
        # Append to conversation history and persist
        conversation_history.append({"text": text, "timestamp": time.time()})
        save_conversation(conversation_history)
        # Update vector store for retrieval
        build_embeddings()

    def retrieve(self, query: str, top_k: int = 5):
        # Use memory hybrid vector search
        return query_embeddings(query, top_k=top_k)

    def generate(self, prompt: str, model_name: str, max_tokens: int = 128) -> str:
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not loaded.")
        resp = self.models[model_name](prompt=prompt, max_tokens=max_tokens)
        return resp['choices'][0]['text']

# Routing: code-like inputs → code model, else → chat model
CODE_TRIGGERS = ["import ", "def ", "class ", "```", "# "]
def select_model(text: str) -> str:
    return "codellama-13b-q4_k_m" if any(kw in text for kw in CODE_TRIGGERS) else "mistral-7b-q5_k_m"


def main():
    parser = argparse.ArgumentParser(description="Sapphira CLI")
    parser.add_argument('--model', choices=list(MODEL_CONFIGS.keys()) + ['auto'], default='auto')
    args = parser.parse_args()

    sapphira = Sapphira()
    print(f"Sapphira ready (mode={args.model}). Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # 1) Handle slash/utility commands
        cmd = handle_command(user_input)
        if cmd:
            print(f"Sapphira (cmd): {cmd}\n")
            continue

        # 2) Standard flow: index & retrieve
        sapphira.index_text(user_input)
        hits = sapphira.retrieve(user_input)
        context = "\n".join(hits)
        full_prompt = context + "\n" + user_input

        # 3) Model selection
        model_key = select_model(user_input) if args.model == 'auto' else args.model
        answer = sapphira.generate(full_prompt, model_key)
        print(f"\nSapphira ({model_key}): {answer}\n")

if __name__ == "__main__":
    main()
