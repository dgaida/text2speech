# Basic Usage

Learn how to use `text2speech` for simple tasks.

## Simple Speech Output with Queue (Recommended)

By default, the audio queue is enabled, allowing for non-blocking execution.

```python
from text2speech import Text2Speech

# Initialize the TTS system (queue enabled by default)
tts = Text2Speech(verbose=True)

# Queue messages for playback (non-blocking)
tts.speak("Hello, this is your robot speaking!")
tts.speak("This message will play after the first one.")

# Cleanup when done
tts.shutdown()
```

## Blocking Mode

You can force the program to wait until the speech has been output.

```python
from text2speech import Text2Speech

tts = Text2Speech()

# Wait for speech to complete before continuing
tts.speak("Please wait for this message.", blocking=True)
print("Message finished!")

tts.shutdown()
```

## Usage as a Context Manager

For automatic resource management, using it as a context manager is recommended.

```python
from text2speech import Text2Speech

with Text2Speech() as tts:
    tts.speak("Automatic cleanup!")
    # Shutdown called automatically
```

## Command Line Interface (CLI)

The library provides a simple CLI tool for quick tests or integration into shell scripts.

```bash
# Basic usage
text2speech "Hello, world!"

# With custom voice
text2speech "Hello" --voice am_adam

# With custom config
text2speech "Hello" --config my_config.yaml
```

## Runtime Adjustments

You can change the voice, speed, and volume at any time.

```python
tts = Text2Speech()

# Change voice at runtime
tts.set_voice("am_adam")
tts.speak("Speaking with Adam's voice")

# Adjust speed (0.5 to 2.0)
tts.set_speed(1.2)

# Adjust volume (0.0 to 1.0)
tts.set_volume(0.7)

tts.shutdown()
```
