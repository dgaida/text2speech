# API Reference

Complete API documentation for the text2speech module.

---

## Table of Contents

- [Module Overview](#module-overview)
- [Text2Speech Class](#text2speech-class)
- [AudioQueueManager Class](#audioqueumanager-class)
- [Config Class](#config-class)
- [Exceptions](#exceptions)
- [Type Hints](#type-hints)
- [Examples](#examples)

---

## Module Overview

```python
from text2speech import Text2Speech, Config, AudioQueueManager
```

### Package Information

```python
import text2speech

print(text2speech.__version__)  # "0.2.0"
```

---

## Text2Speech Class

Main class for text-to-speech functionality with configurable settings and audio queue management.

### Constructor

```python
Text2Speech(
    el_api_key: Optional[str] = None,
    verbose: Optional[bool] = None,
    config_path: Optional[str] = None,
    config: Optional[Config] = None,
    enable_queue: bool = True,
    max_queue_size: int = 50,
    duplicate_timeout: float = 2.0
)
```

Initialize a Text2Speech instance.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `el_api_key` | `str` or `None` | `None` | API key for ElevenLabs (legacy, optional) |
| `verbose` | `bool` or `None` | `None` | Enable verbose output (overrides config) |
| `config_path` | `str` or `None` | `None` | Path to YAML configuration file |
| `config` | `Config` or `None` | `None` | Pre-loaded Config object |
| `enable_queue` | `bool` | `True` | Enable audio queue manager |
| `max_queue_size` | `int` | `50` | Maximum queued messages |
| `duplicate_timeout` | `float` | `2.0` | Skip duplicates within this window (seconds) |

#### Returns

- `Text2Speech` instance

#### Raises

- `FileNotFoundError`: If `config_path` is specified but file doesn't exist
- `yaml.YAMLError`: If config file contains invalid YAML

#### Example

```python
from text2speech import Text2Speech

# Basic initialization with queue
tts = Text2Speech(el_api_key="dummy_key")

# With verbose mode
tts = Text2Speech(el_api_key="dummy_key", verbose=True)

# Custom queue settings
tts = Text2Speech(
    el_api_key="dummy_key",
    enable_queue=True,
    max_queue_size=100,
    duplicate_timeout=5.0
)

# With custom config file
tts = Text2Speech(
    el_api_key="dummy_key",
    config_path="/path/to/config.yaml"
)

# Cleanup when done
tts.shutdown()
```

---

### Methods

#### `speak`

```python
def speak(text: str, priority: int = 0, blocking: bool = False) -> bool
```

Queue text for speech synthesis (NEW unified API).

##### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | - | Text to convert to speech |
| `priority` | `int` | `0` | Priority level (0-100, higher = more urgent) |
| `blocking` | `bool` | `False` | If True, wait for speech to complete |

##### Returns

- `bool`: `True` if successfully queued/spoken, `False` otherwise

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

# Queue message (non-blocking)
tts.speak("Hello, world!")

# High-priority message
tts.speak("Warning!", priority=10)

# Wait for completion
tts.speak("Important message", blocking=True)

tts.shutdown()
```

##### Notes

- Non-blocking by default: returns immediately while speech is queued
- Thread-safe: multiple calls can be made concurrently
- Automatic duplicate detection within timeout window
- Priority queue ensures urgent messages play first

---

#### `call_text2speech_async`

```python
def call_text2speech_async(text: str) -> threading.Thread
```

Generate and play speech asynchronously (legacy method).

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Text to convert to speech |

##### Returns

- `threading.Thread`: Thread handling the TTS operation

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key", enable_queue=False)

# Start async speech
thread = tts.call_text2speech_async("Hello, world!")

# Do other work here...

# Wait for completion
thread.join()
```

##### Notes

- Legacy method: consider using `speak()` instead
- Works with or without queue enabled
- Thread-safe audio playback with error handling

---

#### `call_text2speech`

```python
def call_text2speech(text: str) -> None
```

Synchronous TTS call (blocks until complete).

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Text to convert to speech |

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

# Synchronous call (blocks)
tts.call_text2speech("Wait for me")

print("Speech finished!")
tts.shutdown()
```

---

#### `shutdown`

```python
def shutdown(timeout: float = 5.0) -> None
```

Shutdown the TTS system cleanly.

##### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | `float` | `5.0` | Maximum seconds to wait for queue to empty |

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

tts.speak("Message 1")
tts.speak("Message 2")

# Clean shutdown (waits for queue to empty)
tts.shutdown(timeout=10.0)
```

##### Notes

- Waits for queued messages to finish playing
- Automatically called by `__del__` destructor
- Safe to call multiple times

---

#### `get_queue_stats`

```python
def get_queue_stats() -> dict
```

Get audio queue statistics.

##### Returns

- `dict`: Statistics dictionary with keys:
  - `messages_queued`: Total messages queued
  - `messages_played`: Total messages played
  - `messages_skipped_duplicate`: Duplicates skipped
  - `messages_skipped_full`: Messages rejected (queue full)
  - `errors`: Total errors encountered

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

tts.speak("Test 1")
tts.speak("Test 2")

stats = tts.get_queue_stats()
print(stats)
# {
#     'messages_queued': 2,
#     'messages_played': 1,
#     'messages_skipped_duplicate': 0,
#     'messages_skipped_full': 0,
#     'errors': 0
# }

tts.shutdown()
```

##### Notes

- Returns empty dict `{}` if queue is disabled
- Updated in real-time as messages are processed

---

#### `verbose`

```python
def verbose() -> bool
```

Check if verbose mode is enabled.

##### Returns

- `bool`: `True` if verbose mode is active, `False` otherwise

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key", verbose=True)

if tts.verbose():
    print("Debug information will be shown")
```

---

#### `set_voice`

```python
def set_voice(voice: str) -> None
```

Change the voice for speech generation.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `voice` | `str` | Voice identifier (e.g., 'af_heart', 'am_adam') |

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

# Change to male voice
tts.set_voice("am_adam")
tts.speak("Speaking with new voice")

tts.shutdown()
```

##### Available Voices

**American English**:
- `af_heart` - Female, warm
- `af_nicole` - Female, professional
- `am_adam` - Male, authoritative
- `am_michael` - Male, friendly

**British English**:
- `bf_emma` - Female, elegant
- `bf_isabella` - Female, sophisticated
- `bm_lewis` - Male, refined
- `bm_george` - Male, distinguished

---

#### `set_speed`

```python
def set_speed(speed: float) -> None
```

Adjust speech speed.

##### Parameters

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `speed` | `float` | 0.5-2.0 | Speech rate multiplier |

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

# Slow speech (80% of normal)
tts.set_speed(0.8)

# Fast speech (120% of normal)
tts.set_speed(1.2)

tts.shutdown()
```

##### Notes

- Values < 0.5 or > 2.0 are rejected with a warning
- Default speed is 1.0 (normal)
- Affects all subsequent speech generation

---

#### `set_volume`

```python
def set_volume(volume: float) -> None
```

Set playback volume.

##### Parameters

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `volume` | `float` | 0.0-1.0 | Volume multiplier |

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

# Quiet (40% volume)
tts.set_volume(0.4)

# Loud (90% volume)
tts.set_volume(0.9)

tts.shutdown()
```

##### Notes

- 0.0 = muted, 1.0 = maximum safe volume
- Values outside range are rejected with a warning
- Default volume is 0.8

---

#### `get_available_devices`

```python
def get_available_devices() -> list
```

Get list of available audio output devices.

##### Returns

- `list`: List of device information dictionaries

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

devices = tts.get_available_devices()
for i, device in enumerate(devices):
    print(f"{i}: {device['name']}")

tts.shutdown()
```

##### Output Format

```python
[
    {
        'name': 'Built-in Audio',
        'max_output_channels': 2,
        'default_samplerate': 44100.0,
        ...
    },
    ...
]
```

---

#### `is_using_elevenlabs`

```python
def is_using_elevenlabs() -> bool
```

Check if currently using ElevenLabs API.

##### Returns

- `bool`: `True` if using ElevenLabs, `False` if using Kokoro

##### Example

```python
tts = Text2Speech(el_api_key="sk_validkey123")

if tts.is_using_elevenlabs():
    print("Using ElevenLabs TTS")
else:
    print("Using Kokoro TTS")
```

---

### Static Methods

#### `_play_audio_safely`

```python
@staticmethod
def _play_audio_safely(
    audio_tensor: torch.Tensor,
    original_sample_rate: int = 24000,
    device: Optional[int] = None,
    volume: float = 0.8
) -> None
```

Play audio with automatic resampling and volume normalization.

##### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_tensor` | `torch.Tensor` | - | 1D audio waveform tensor |
| `original_sample_rate` | `int` | `24000` | Original sample rate in Hz |
| `device` | `int` or `None` | `None` | Output device ID (None = default) |
| `volume` | `float` | `0.8` | Volume multiplier (0.0-1.0) |

##### Example

```python
import torch
from text2speech import Text2Speech

# Generate some audio
audio = torch.randn(24000)  # 1 second at 24kHz

# Play safely
Text2Speech._play_audio_safely(
    audio,
    original_sample_rate=24000,
    device=None,
    volume=0.8
)
```

---

## AudioQueueManager Class

Thread-safe audio queue manager for serialized playback.

### Constructor

```python
AudioQueueManager(
    tts_callable: Callable[[str], None],
    max_queue_size: int = 50,
    duplicate_timeout: float = 2.0,
    logger: Optional[logging.Logger] = None
)
```

Initialize the audio queue manager.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tts_callable` | `Callable` | - | Synchronous TTS function |
| `max_queue_size` | `int` | `50` | Maximum queued messages |
| `duplicate_timeout` | `float` | `2.0` | Skip duplicates within window (seconds) |
| `logger` | `Logger` or `None` | `None` | Optional logger instance |

#### Example

```python
from text2speech.audio_queue import AudioQueueManager

def my_tts(text):
    print(f"Speaking: {text}")

manager = AudioQueueManager(my_tts)
manager.start()

manager.enqueue("Hello")
manager.enqueue("World")

manager.shutdown()
```

---

### Methods

#### `start`

```python
def start() -> None
```

Start the worker thread.

---

#### `shutdown`

```python
def shutdown(timeout: float = 5.0) -> None
```

Stop the worker thread and wait for completion.

---

#### `enqueue`

```python
def enqueue(text: str, priority: int = 0) -> bool
```

Queue a message for audio playback (non-blocking).

##### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | - | Message to speak |
| `priority` | `int` | `0` | Priority (higher = more urgent) |

##### Returns

- `bool`: `True` if queued successfully, `False` if skipped/failed

---

#### `clear_queue`

```python
def clear_queue() -> None
```

Clear all pending messages from queue.

---

#### `get_stats`

```python
def get_stats() -> dict
```

Get playback statistics.

---

#### `is_running`

```python
def is_running() -> bool
```

Check if worker thread is active.

---

## Config Class

Configuration management for text2speech settings.

### Constructor

```python
Config(config_path: Optional[str] = None)
```

Initialize configuration manager.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_path` | `str` or `None` | `None` | Path to config file (None = search defaults) |

#### Example

```python
from text2speech import Config

# Load from default locations
config = Config()

# Load specific file
config = Config("/path/to/config.yaml")
```

---

### Methods

#### `get`

```python
def get(key_path: str, default: Any = None) -> Any
```

Retrieve configuration value using dot notation.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `key_path` | `str` | Dot-separated path (e.g., 'audio.volume') |
| `default` | `Any` | Value to return if key not found |

##### Returns

- Configuration value or `default` if not found

##### Example

```python
config = Config()

volume = config.get("audio.default_volume")  # 0.8
device = config.get("audio.output_device", 0)  # 0 (default)
```

---

#### `set`

```python
def set(key_path: str, value: Any) -> None
```

Set configuration value using dot notation.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `key_path` | `str` | Dot-separated path |
| `value` | `Any` | Value to set |

##### Example

```python
config = Config()

config.set("audio.default_volume", 0.5)
config.set("tts.kokoro.voice", "am_adam")
config.set("logging.verbose", True)
```

---

#### `load_from_file`

```python
def load_from_file(config_path: str) -> None
```

Load configuration from YAML file.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `config_path` | `str` | Path to YAML file |

##### Raises

- `FileNotFoundError`: If file doesn't exist
- `yaml.YAMLError`: If file contains invalid YAML

##### Example

```python
config = Config()
config.load_from_file("custom_config.yaml")
```

---

#### `save_to_file`

```python
def save_to_file(config_path: str) -> None
```

Save current configuration to YAML file.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `config_path` | `str` | Path where to save |

##### Example

```python
config = Config()
config.set("audio.default_volume", 0.7)
config.save_to_file("my_config.yaml")
```

---

#### `to_dict`

```python
def to_dict() -> Dict[str, Any]
```

Get complete configuration as dictionary.

##### Returns

- `Dict[str, Any]`: Full configuration dictionary

##### Example

```python
config = Config()
full_config = config.to_dict()

import json
print(json.dumps(full_config, indent=2))
```

---

### Properties

Configuration properties provide convenient access to common settings.

#### Audio Properties

```python
config.audio_output_device -> Optional[int]
config.audio_volume -> float
config.sample_rate -> int
```

#### TTS Properties

```python
config.tts_engine -> str
config.kokoro_lang_code -> str
config.kokoro_voice -> str
config.kokoro_speed -> float
config.kokoro_split_pattern -> str
```

#### Logging Properties

```python
config.verbose -> bool
```

#### Performance Properties

```python
config.use_gpu -> bool
```

#### Example

```python
config = Config()

print(f"Voice: {config.kokoro_voice}")
print(f"Speed: {config.kokoro_speed}")
print(f"Volume: {config.audio_volume}")
```

---

## Exceptions

### Standard Exceptions

The module uses standard Python exceptions:

| Exception | When Raised | Example |
|-----------|-------------|---------|
| `FileNotFoundError` | Config file not found | Invalid `config_path` |
| `yaml.YAMLError` | Invalid YAML syntax | Malformed config file |
| `ValueError` | Invalid parameter value | Speed outside 0.5-2.0 |
| `ImportError` | Missing dependency | Kokoro or sounddevice not installed |
| `queue.Full` | Queue at capacity | Too many messages queued |

---

## Type Hints

The module includes complete type hints for better IDE support.

### Imports

```python
from typing import Optional, Any, Dict, List, Callable
import threading
import torch
import logging
```

---

## Examples

### Basic Usage

```python
from text2speech import Text2Speech

# Initialize
tts = Text2Speech(el_api_key="dummy_key")

# Simple speech
tts.speak("Hello, world!")

# Cleanup
tts.shutdown()
```

### With Priority Queue

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

# Normal priority
tts.speak("Loading data...")

# High priority (plays first)
tts.speak("Error occurred!", priority=10)

# Low priority
tts.speak("Background task complete", priority=1)

tts.shutdown()
```

### Blocking Mode

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

# Wait for completion
tts.speak("Please wait", blocking=True)
print("Speech finished!")

tts.shutdown()
```

### Queue Statistics

```python
from text2speech import Text2Speech
import time

tts = Text2Speech(el_api_key="dummy_key")

# Queue messages
for i in range(5):
    tts.speak(f"Message {i}")

# Wait a bit
time.sleep(2)

# Check stats
stats = tts.get_queue_stats()
print(f"Queued: {stats['messages_queued']}")
print(f"Played: {stats['messages_played']}")

tts.shutdown()
```

## See Also

- [Configuration Guide](configuration.md) - Detailed configuration options
- [Installation Guide](installation.md) - Setup instructions
- [README](../README.md) - Project overview
- [FAQ](faq.md) - Common questions

---

**Last Updated**: December 2025  
**Version**: 0.2.0
