# bot_core/model_llamacpp.py

from llama_cpp import Llama
import json
import re
from bot_core.memory import conversation_history, save_conversation

# Load Sapphira's personality from file
with open("sapphira_profile.json", "r", encoding="utf-8") as f:
    sapphira = json.load(f)

MODEL_PATH = r"D:\Models\CodeLlama-13B\codellama-13b.Q4_K_M.gguf"
llm = None

def load_model():
    global llm
    if llm is None:
        llm = Llama(
            model_path=str(MODEL_PATH),
            n_ctx=2048,
            n_gpu_layers=0,
            n_threads=4,
            verbose=False
        )
    return generate_response

def clean_repetition(response: str) -> str:
    match = re.search(r"(\b\d{4}s\b)(, \1)+", response)
    if match:
        return response[:match.start()] + match.group(1)
    return response

def strip_prompt_formatting(text: str) -> str:
    # Remove injected role markers like USER:, ASSISTANT:, Sapphira:
    return re.sub(r"^(USER:|ASSISTANT:|Sapphira:)[\s]*", "", text.strip(), flags=re.IGNORECASE)

def generate_response(prompt: str, verbose: bool = False):
    if llm is None:
        raise RuntimeError("Model not loaded")

    if any(keyword in prompt.lower() for keyword in ["def ", "print(", "import ", "main()"]):
        prompt += "\n(Please reply in natural language unless I request code.)"

    system_prompt = (
        f"You are Sapphira, a {sapphira['age']}-year-old AI with the following traits:\n"
        f"{sapphira['personality']}\n"
        f"Your quirks: {', '.join(sapphira['quirks'])}\n"
        f"Your communication style: {sapphira['style']}\n\n"
        "Respond in first person, naturally, as if you're speaking directly to the user.\n"
        "Stay in character and remember your tone. Do not explain that you are an AI.\n"
        "Note: Respond conversationally unless the user clearly asks for code."
    )

    chat_prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    full_prompt = ""
    for msg in chat_prompt:
        if msg["role"] == "user":
            full_prompt += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            full_prompt += f"Sapphira: {msg['content']}\n"
        else:
            full_prompt += f"{msg['content']}\n"
    full_prompt += "Sapphira: "

    conversation_history.append({"role": "user", "content": strip_prompt_formatting(prompt)})

    def call_llm():
        return llm(
            full_prompt,
            max_tokens=512,
            temperature=0.7,
            stop=["User:", "Sapphira:", "\n\n"],
        )["choices"][0]["text"].strip()

    response = call_llm()
    if not response or response.strip() in ["USER:", "ASSISTANT:"] or response.lower().startswith("assistant"):
        response = call_llm()

    response = clean_repetition(response)
    response_clean = strip_prompt_formatting(response)

    if "{" in response_clean and "}" in response_clean and response_clean.count("{") > 5:
        response_clean = "Sorry — I think I overthought that one. Try me again?"

    conversation_history.append({"role": "assistant", "content": response_clean})
    save_conversation(conversation_history)

    return [{"generated_text": response_clean}]