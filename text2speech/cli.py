"""Command-line interface for text2speech."""

import argparse
from .text2speech import Text2Speech


def main() -> None:
    """Command-line interface for text2speech."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Convert text to speech")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("--voice", help="Voice identifier to use")
    parser.add_argument("--config", help="Path to config.yaml file")

    args: argparse.Namespace = parser.parse_args()

    tts: Text2Speech = Text2Speech(config_path=args.config)
    if args.voice:
        tts.set_voice(args.voice)

    # Using the new speak API (blocking)
    tts.speak(args.text, blocking=True)


if __name__ == "__main__":
    main()
