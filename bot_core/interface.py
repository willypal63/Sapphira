from rich.console import Console
from rich.prompt import Prompt
from bot_core.paths import PROJECT_PATH, LEARNING_DATA_PATH, EMBEDDING_DB_PATH
from bot_core.io import list_project_files, read_file
from bot_core.learning import learn_all_supported_files, learn_from_text_file, learn_from_archive, reset_memory
from bot_core.memory import build_embeddings, query_embeddings
from bot_core.logger_utils import log_error, log_info, log_interaction
from config import MAX_PROMPT_TOKENS, MAX_RETRIEVED_CHUNKS, MAX_CHUNK_CHARS
import os

os.environ["LLAMA_CPP_FORCE_CPU"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

console = Console()
verbose_mode = False

def command_loop(gen):
    global verbose_mode
    
    log_info("Assistant started")
    context = ""

    try:
        while True:
            user_input = Prompt.ask("[bold cyan]>>>", default="")

            if user_input == "/exit":
                log_info("Assistant exited by user")
                break
            elif user_input == "/verbose on":
                verbose_mode = True
                console.print("[dim green]Verbose mode enabled.")
                continue
            elif user_input == "/verbose off":
                verbose_mode = False
                console.print("[dim red]Verbose mode disabled.")
                continue
            elif user_input.startswith("/files"):
                files = list_project_files(PROJECT_PATH)
                console.print("\n".join(map(str, files)))
            elif user_input.startswith("/read"):
                _, file = user_input.split(" ", 1)
                console.print(read_file(file))
            elif user_input == "/learn all":
                console.print(learn_all_supported_files())
                continue
            elif user_input == "/learn archive":
                console.print(learn_from_archive())
                continue
            elif user_input == "/reset_memory":
                console.print(reset_memory())
                continue
            elif user_input.startswith("/learn"):
                _, file_name = user_input.split(" ", 1)
                learn_from_text_file(file_name)
            elif user_input == "/build_index":
                build_embeddings()
            else:
                
                try:
                    raw_chunks = query_embeddings(user_input)
                    filtered_chunks = [chunk[:MAX_CHUNK_CHARS] for chunk in raw_chunks[:MAX_RETRIEVED_CHUNKS]]
                    if not user_input.strip().endswith(("?", ".", ":")):
                        user_input += "?"
                    prompt = "\n\n".join(filtered_chunks) + f"\n\nUSER: {user_input}\nASSISTANT:"

                    if len(prompt) > MAX_PROMPT_TOKENS * 4:
                        raise ValueError("Prompt exceeds model context window. Reduce input or memory size.")

                    result = gen(prompt, verbose=verbose_mode)

                    if isinstance(result, list) and isinstance(result[0], dict):
                        
                        console.print(result[0].get("generated_text", "[no response]"))
                        log_interaction(user_input, result[0].get("generated_text", "[no response]"))
                        # log_info removed for quiet output
                    else:
                        console.print(str(result).strip())
                        log_interaction(user_input, str(result))
                        log_info(f"RESPONSE: {str(result).strip()[:100]}...")
                except Exception as inner_error:
                    log_error(f"Error during generation: {inner_error}")
                    console.print("[red]Error processing your request.[/red]")

    except Exception as e:
        log_error(f"Unhandled exception in command loop: {e}")
        console.print("[bold red]A fatal error occurred. Check logs for details.[/bold red]")
