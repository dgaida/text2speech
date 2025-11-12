"""Example application demonstrating text2speech functionality.

This module provides several examples of how to use the Text2Speech class
for various text-to-speech scenarios including simple text, multilingual
content, and multiple utterances.
"""

import argparse
import time
from text2speech import Text2Speech


def example_simple_greeting(tts: Text2Speech) -> None:
    """Demonstrate a simple greeting using TTS.

    Args:
        tts: An initialized Text2Speech instance.
    """
    print("\n=== Example 1: Simple Greeting ===")
    text = "Hello! I am a robot with text-to-speech capabilities."
    print(f"Speaking: '{text}'")
    thread = tts.call_text2speech_async(text)
    thread.join()
    print("✓ Speech completed")


def example_multiple_sentences(tts: Text2Speech) -> None:
    """Demonstrate speaking multiple sentences sequentially.

    Args:
        tts: An initialized Text2Speech instance.
    """
    print("\n=== Example 2: Multiple Sentences ===")
    sentences = ["This is the first sentence.", "Now I'm saying something else.", "And finally, this is the last part."]

    for i, sentence in enumerate(sentences, 1):
        print(f"Speaking sentence {i}: '{sentence}'")
        thread = tts.call_text2speech_async(sentence)
        thread.join()
        time.sleep(0.5)  # Small pause between sentences

    print("✓ All sentences completed")


def example_multilingual(tts: Text2Speech) -> None:
    """Demonstrate multilingual text-to-speech capabilities.

    Args:
        tts: An initialized Text2Speech instance.
    """
    print("\n=== Example 3: Multilingual Content ===")
    texts = [
        ("English", "Welcome to the multilingual demonstration."),
        ("German", "Willkommen zur mehrsprachigen Demonstration."),
        ("Spanish", "Bienvenido a la demostración multilingüe."),
    ]

    for language, text in texts:
        print(f"Speaking in {language}: '{text}'")
        thread = tts.call_text2speech_async(text)
        thread.join()
        time.sleep(0.5)

    print("✓ Multilingual demonstration completed")


def example_long_text(tts: Text2Speech) -> None:
    """Demonstrate speaking longer text passages.

    Args:
        tts: An initialized Text2Speech instance.
    """
    print("\n=== Example 4: Long Text ===")
    text = """
    The text-to-speech module provides robust audio output capabilities.
    It uses the Kokoro model for natural-sounding speech synthesis.
    The system supports asynchronous operation and automatic audio resampling.
    This makes it ideal for robotics applications and interactive systems.
    """
    print(f"Speaking long text (length: {len(text)} characters)")
    thread = tts.call_text2speech_async(text)
    thread.join()
    print("✓ Long text completed")


def example_interactive_mode(tts: Text2Speech) -> None:
    """Run an interactive mode where users can input text to be spoken.

    Args:
        tts: An initialized Text2Speech instance.
    """
    print("\n=== Example 5: Interactive Mode ===")
    print("Enter text to be spoken (or 'quit' to exit)")

    while True:
        user_input = input("\n> ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Exiting interactive mode...")
            break

        if not user_input:
            print("Please enter some text.")
            continue

        print(f"Speaking: '{user_input}'")
        thread = tts.call_text2speech_async(user_input)
        thread.join()


def run_all_examples(verbose: bool = False) -> None:
    """Run all example demonstrations.

    Args:
        verbose: If True, enables verbose output from the TTS system.
    """
    print("=" * 60)
    print("Text2Speech Examples")
    print("=" * 60)

    # Initialize TTS (API key is not used anymore but required for compatibility)
    tts = Text2Speech(el_api_key="dummy_key", verbose=verbose)

    # Run examples
    example_simple_greeting(tts)
    example_multiple_sentences(tts)
    example_multilingual(tts)
    example_long_text(tts)

    # Optionally run interactive mode
    response = input("\nRun interactive mode? (y/n): ").strip().lower()
    if response == "y":
        example_interactive_mode(tts)

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


def main() -> None:
    """Main entry point for the example application."""
    parser = argparse.ArgumentParser(
        description="Text2Speech Example Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run all examples
  python main.py --verbose          # Run with verbose output
  python main.py --example 1        # Run specific example
  python main.py --interactive      # Run interactive mode only
        """,
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--example", "-e", type=int, choices=[1, 2, 3, 4, 5], help="Run a specific example (1-5)")

    parser.add_argument("--interactive", "-i", action="store_true", help="Run interactive mode only")

    args = parser.parse_args()

    # Initialize TTS
    tts = Text2Speech(el_api_key="dummy_key", verbose=args.verbose)

    # Run specific example or all examples
    if args.interactive:
        example_interactive_mode(tts)
    elif args.example:
        examples = {
            1: example_simple_greeting,
            2: example_multiple_sentences,
            3: example_multilingual,
            4: example_long_text,
            5: example_interactive_mode,
        }
        examples[args.example](tts)
    else:
        run_all_examples(verbose=args.verbose)


if __name__ == "__main__":
    main()
