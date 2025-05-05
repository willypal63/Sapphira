# bot_core/formatting.py

from datetime import datetime
from colorama import Style, Fore
from collections import deque

BRIGHT_CYAN = "\033[96m"


def format_sapphira_response(text: str) -> str:
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    return f"{BRIGHT_CYAN}{timestamp} Sapphira: {text}{Style.RESET_ALL}"


def format_user_input(text: str) -> str:
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


def timestamped_input_label(prompt=">>> "):
    now = datetime.now().strftime("[%H:%M:%S]")
    return format_user_input(f"{now} {prompt}")

def get_local_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_local_date() -> str:
    return datetime.now().strftime("%A, %B %d, %Y")