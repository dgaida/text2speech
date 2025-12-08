import argparse

from .text2speech import Text2Speech


def main():
    """Command-line interface for text2speech."""
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("--voice", help="Voice to use")
    parser.add_argument("--config", help="Config file path")
    args = parser.parse_args()

    tts = Text2Speech(config_path=args.config)
    if args.voice:
        tts.set_voice(args.voice)
    tts.call_text2speech_async(args.text).join()
