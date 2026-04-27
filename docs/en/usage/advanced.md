# Advanced Usage

This section covers complex scenarios such as audio queue management, priorities, and using multiple instances.

## Priority Control

Urgent messages can overtake other messages in the queue.

```python
from text2speech import Text2Speech

tts = Text2Speech()

# Normal messages
tts.speak("Message 1")
tts.speak("Message 2")

# High-priority message (will play next)
tts.speak("Warning: Low battery!", priority=10)

tts.shutdown()
```

## Audio Queue Statistics

You can monitor the status of the queue to see how many messages have been processed.

```python
stats = tts.get_queue_stats()
print(stats)
# {
#     'messages_queued': 3,
#     'messages_played': 1,
#     'messages_skipped_duplicate': 0,
#     'messages_skipped_full': 0,
#     'errors': 0
# }
```

## Duplicate Detection

The `AudioQueueManager` can automatically skip identical messages within a time window to avoid redundancy.

```python
from text2speech import Text2Speech

tts = Text2Speech(
    duplicate_timeout=5.0  # 5-second duplicate detection window
)

tts.speak("System ready")
tts.speak("System ready")  # Will be skipped if within 5 seconds
```

## Multiple TTS Instances

You can use different instances with different configurations, e.g., for different roles or speakers.

```python
from text2speech import Text2Speech

# Robot voice
robot_tts = Text2Speech()
robot_tts.set_voice("am_adam")
robot_tts.set_speed(1.1)

# Narrator voice
narrator_tts = Text2Speech()
narrator_tts.set_voice("bf_emma")

robot_tts.speak("I am a robot.")
narrator_tts.speak("The narrator begins the story.")

robot_tts.shutdown()
narrator_tts.shutdown()
```

## Legacy Mode (Without Queue)

For applications that require the old threading model:

```python
# Disable the queue
tts = Text2Speech(enable_queue=False)

# Starts a separate thread for playback
thread = tts.call_text2speech_async("Hello world")
thread.join()
```

## Running Examples

In the `examples/` directory, you will find `demo.py`, which demonstrates various scenarios:

```bash
# Run all examples sequentially
python examples/demo.py

# Interactive mode
python examples/demo.py --interactive
```
