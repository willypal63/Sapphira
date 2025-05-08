from code_model import generate_code
from chat_model import generate_chat
from memory_model import summarize_or_retrieve


def route(prompt: str) -> str:
    """
    Routes a prompt to the appropriate model based on content.
    """
    prompt_lower = prompt.lower()

    # 1. Code-related prompts
    if prompt_lower.startswith("/code") or "generate a script" in prompt_lower or "write code" in prompt_lower:
        return generate_code(prompt)

    # 2. Memory queries or summarization
    elif prompt_lower.startswith("/memory") or "summarize" in prompt_lower or "what did i say" in prompt_lower:
        return summarize_or_retrieve(prompt)

    # 3. Default: chat model handles it
    else:
        return generate_chat(prompt)


# Optional: Add routing debug if needed
if __name__ == "__main__":
    test_input = input("Type a prompt: ")
    print("\nResponse:\n", route(test_input))
