# main.py

import json
import sys
from pathlib import Path
from datetime import datetime
from bot_core.formatting import format_user_input
from bot_core.formatting import format_sapphira_response
from bot_core.command_dispatcher import handle_command
from bot_core.model_llamacpp import init_llm
from bot_core.memory_vector_store import build_vector_store
from bot_core.constants_config import HELP_TEXT
from colorama import Style

def timestamped_input_label(prompt=">>> "):
    now = datetime.now().strftime("[%H:%M:%S]")
    return format_user_input(f"{now} {prompt}")

def main():
    config_path = Path("config.json")
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    llm = init_llm(config)
    print("[INFO] Launching assistant")

    if config.get("build_on_startup", False):
        print("[INFO] Building hybrid vector store...")
        build_vector_store()
        print("[INFO] Vector store ready.")

    while True:
        try:
            user_input = input(timestamped_input_label()).strip()
            if not user_input:
                continue

            cmd_resp = handle_command(user_input)
            if cmd_resp is not None:
                print(cmd_resp)
                continue

            response = llm(user_input)
            if isinstance(response, list) and response and isinstance(response[0], dict) and "generated_text" in response[0]:
                response = response[0]["generated_text"]

            print(format_sapphira_response(response))

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

if __name__ == "__main__":
    main()

