# bot_core/code_generation.py

import pathlib
import logging
import openai
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_file(template: str,
                  destination: pathlib.Path,
                  **kwargs) -> Optional[pathlib.Path]:
    """
    Generate a new file based on a template string or identifier.
    This function uses a local import of the command dispatcher to avoid circular dependencies.

    Args:
        template (str): The template content or template ID.
        destination (pathlib.Path): Where to write the generated file.
        **kwargs: Additional parameters for generation.

    Returns:
        pathlib.Path if successful, None otherwise.
    """
    # Local import to break circular import with command_dispatcher
    from bot_core.command_dispatcher import dispatcher

    try:
        # Dispatch the template generation
        content = dispatcher.dispatch(template, **kwargs)
        destination.write_text(content, encoding="utf-8")
        logger.info(f"Generated file at {destination}")
        return destination
    except Exception as e:
        logger.error(f"File generation failed for {destination}: {e}")
        return None


def generate_patch(file_path: pathlib.Path,
                   diff_prompt: str,
                   model: str = "gpt-4",
                   temperature: float = 0.0,
                   max_tokens: int = 2048) -> Optional[str]:
    """
    Generate a unified diff patch for the given file based on the diff_prompt.
    Returns the patch text, or None if generation fails.

    Args:
        file_path (pathlib.Path): Path to the original file to patch.
        diff_prompt (str): Instructions describing desired changes.
        model (str): OpenAI model to use.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum tokens to generate.
    """
    try:
        original = file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return None

    system_msg = (
        "You are a helpful assistant specialized in generating unified diff patches."
    )
    user_msg = (
        f"Here is the original code from `{file_path.name}`:\n```{original}```\n"
        f"---\n{diff_prompt}\n"
        "Please respond with a unified diff patch only."
    )

    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": user_msg},
            ],
        )
        patch = response.choices[0].message.content.strip()
        return patch
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return None


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Generate files or unified diff patches using OpenAI GPT models."
    )
    parser.add_argument("--file", type=pathlib.Path,
                        help="Target file path for patch generation.")
    parser.add_argument("--prompt", type=str,
                        help="Diff prompt describing desired changes.")
    parser.add_argument("--template", type=str,
                        help="Template string or identifier for file generation.")
    parser.add_argument("--dest", type=pathlib.Path,
                        help="Destination path for generated file.")
    args = parser.parse_args()

    if args.template and args.dest:
        result = generate_file(args.template, args.dest)
        if not result:
            logger.error("File generation failed.")
    elif args.file and args.prompt:
        result = generate_patch(args.file, args.prompt)
        if result:
            print(result)
        else:
            logger.error("Patch generation failed.")
    else:
        parser.print_help()
