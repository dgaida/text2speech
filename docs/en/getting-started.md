# Getting Started

In this guide, you will learn how to quickly integrate the `text2speech` module into your project.

## Basic Usage

The simplest way to use `text2speech` is via the `Text2Speech` class. By default, the audio queue is enabled, allowing for non-blocking execution.

```python
from text2speech import Text2Speech

# Initialize the TTS system
tts = Text2Speech()

# Queue messages (non-blocking)
tts.speak("Hello, I am ready for action!")
tts.speak("This message will play after the first one.")

# Shut down the system properly
tts.shutdown()
```

## Priorities and Blocking

You can control the priority of messages and decide whether the call should wait until the speech has been output.

```python
# A high-priority message
tts.speak("Warning: Critical error!", priority=10)

# Blocking call (waits until the message has finished speaking)
tts.speak("Please wait for this announcement.", blocking=True)
print("Message finished!")
```

## Adjusting Voices and Volume

You can change the voice, speed, and volume at runtime.

```python
# Change voice to a male speaker
tts.set_voice("am_adam")

# Increase speed (0.5 to 2.0)
tts.set_speed(1.2)

# Adjust volume (0.0 to 1.0)
tts.set_volume(0.9)

tts.speak("I am now speaking with a different voice.")
```

## Usage as a Context Manager

For automatic resource management, using it as a context manager is recommended.

```python
from text2speech import Text2Speech

with Text2Speech() as tts:
    tts.speak("Automatic shutdown after this block.")
```

## Command Line Interface (CLI)

You can also use the library directly from the terminal:

```bash
text2speech "Hello from the command line" --voice af_nicole
```
