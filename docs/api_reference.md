# API Reference

Complete API documentation for the text2speech module.

---

## Table of Contents

- [Module Overview](#module-overview)
- [Text2Speech Class](#text2speech-class)
- [Config Class](#config-class)
- [Exceptions](#exceptions)
- [Type Hints](#type-hints)
- [Examples](#examples)

---

## Module Overview

```python
from text2speech import Text2Speech, Config
```

### Package Information

```python
import text2speech

print(text2speech.__version__)  # "0.2.0"
```

---

## Text2Speech Class

Main class for text-to-speech functionality with configurable settings.

### Constructor

```python
Text2Speech(
    el_api_key: Optional[str] = None,
    verbose: Optional[bool] = None,
    config_path: Optional[str] = None,
    config: Optional[Config] = None
)
```

Initialize a Text2Speech instance.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `el_api_key` | `str` or `None` | `None` | API key for ElevenLabs (legacy, not used) |
| `verbose` | `bool` or `None` | `None` | Enable verbose output (overrides config) |
| `config_path` | `str` or `None` | `None` | Path to YAML configuration file |
| `config` | `Config` or `None` | `None` | Pre-loaded Config object |

#### Returns

- `Text2Speech` instance

#### Raises

- `FileNotFoundError`: If `config_path` is specified but file doesn't exist
- `yaml.YAMLError`: If config file contains invalid YAML

#### Example

```python
from text2speech import Text2Speech

# Basic initialization
tts = Text2Speech(el_api_key="dummy_key")

# With verbose mode
tts = Text2Speech(el_api_key="dummy_key", verbose=True)

# With custom config file
tts = Text2Speech(
    el_api_key="dummy_key",
    config_path="/path/to/config.yaml"
)

# With Config object
from text2speech import Config
config = Config()
config.set("audio.default_volume", 0.5)
tts = Text2Speech(el_api_key="dummy_key", config=config)
```

---

### Methods

#### `call_text2speech_async`

```python
def call_text2speech_async(text: str) -> threading.Thread
```

Generate and play speech asynchronously.

##### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Text to convert to speech |

##### Returns

- `threading.Thread`: Thread handling the TTS operation

##### Example

```python
tts = Text2Speech(el_api_key="dummy_key")

# Start async speech
thread = tts.call_text2speech_async("Hello, world!")

# Do other work here...

# Wait for completion
thread.join()
```

##### Notes

- Non-blocking: returns immediately while speech is generated in background
- Thread-safe: multiple calls can be made concurrently
- Automatic audio device management and error handling

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

# Generate speech with new voice
thread = tts.call_text2speech_async("Speaking with new voice")
thread.join()
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

##### Notes

- Automatically resamples to device's native sample rate
- Normalizes amplitude to prevent clipping
- Applies volume scaling
- Handles errors gracefully with logging

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

### Error Handling Example

```python
from text2speech import Text2Speech, Config
import yaml

try:
    # Try to load config
    config = Config("config.yaml")
    tts = Text2Speech(el_api_key="dummy_key", config=config)

    # Try speech generation
    thread = tts.call_text2speech_async("Test")
    thread.join()

except FileNotFoundError as e:
    print(f"Config file not found: {e}")
except yaml.YAMLError as e:
    print(f"Invalid config format: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Type Hints

The module includes complete type hints for better IDE support.

### Imports

```python
from typing import Optional, Any, Dict, List
import threading
import torch
```

### Example with Type Hints

```python
from text2speech import Text2Speech, Config
from typing import Optional
import threading

def generate_speech(
    text: str,
    voice: Optional[str] = None,
    speed: float = 1.0
) -> threading.Thread:
    """Generate speech with optional parameters."""
    tts = Text2Speech(el_api_key="dummy_key")

    if voice:
        tts.set_voice(voice)
    tts.set_speed(speed)

    return tts.call_text2speech_async(text)

# Usage
thread: threading.Thread = generate_speech(
    "Hello",
    voice="am_adam",
    speed=1.2
)
thread.join()
```

---

## Examples

### Basic Usage

```python
from text2speech import Text2Speech

# Initialize
tts = Text2Speech(el_api_key="dummy_key")

# Simple speech
thread = tts.call_text2speech_async("Hello, world!")
thread.join()
```

### With Configuration

```python
from text2speech import Text2Speech, Config

# Create custom config
config = Config()
config.set("tts.kokoro.voice", "bf_emma")
config.set("tts.kokoro.speed", 0.9)
config.set("audio.default_volume", 0.7)

# Use config
tts = Text2Speech(el_api_key="dummy_key", config=config)
thread = tts.call_text2speech_async("Configured speech")
thread.join()
```

### Multiple Sequential Speeches

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

sentences = [
    "First sentence.",
    "Second sentence.",
    "Third sentence."
]

for sentence in sentences:
    thread = tts.call_text2speech_async(sentence)
    thread.join()  # Wait for each to complete
```

### Dynamic Voice Switching

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

# Narrator voice
tts.set_voice("bm_lewis")
tts.call_text2speech_async("The story begins...").join()

# Character 1 voice
tts.set_voice("af_heart")
tts.call_text2speech_async("Hello, my friend!").join()

# Character 2 voice
tts.set_voice("am_adam")
tts.call_text2speech_async("Good to see you!").join()
```

### Audio Device Selection

```python
from text2speech import Text2Speech, Config

# List devices
tts = Text2Speech(el_api_key="dummy_key")
devices = tts.get_available_devices()

for i, device in enumerate(devices):
    if device['max_output_channels'] > 0:
        print(f"{i}: {device['name']}")

# Use specific device
config = Config()
config.set("audio.output_device", 3)  # Select device 3
tts = Text2Speech(el_api_key="dummy_key", config=config)
```

### Error Handling

```python
from text2speech import Text2Speech
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

try:
    tts = Text2Speech(el_api_key="dummy_key", verbose=True)
    thread = tts.call_text2speech_async("Test")
    thread.join()
    print("✓ Speech completed successfully")

except Exception as e:
    print(f"✗ Error: {e}")
```

### Speed and Volume Control

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

# Slow and quiet
tts.set_speed(0.8)
tts.set_volume(0.4)
tts.call_text2speech_async("Slow and quiet speech").join()

# Fast and loud
tts.set_speed(1.3)
tts.set_volume(0.9)
tts.call_text2speech_async("Fast and loud speech").join()
```

### Saving Custom Configuration

```python
from text2speech import Config

# Create and customize config
config = Config()
config.set("audio.output_device", 2)
config.set("audio.default_volume", 0.75)
config.set("tts.kokoro.voice", "am_michael")
config.set("tts.kokoro.speed", 1.1)
config.set("logging.verbose", True)

# Save for future use
config.save_to_file("my_tts_config.yaml")

# Load later
config2 = Config("my_tts_config.yaml")
```

---

## Version History

### v0.2.0 (Current)
- Added `Config` class for YAML configuration
- Added configuration properties
- Added `set_voice`, `set_speed`, `set_volume` methods
- Added `get_available_devices` method
- Improved logging system
- Enhanced error handling

### v0.1.0
- Initial release
- Basic Kokoro TTS support
- Asynchronous speech generation
- Audio resampling and normalization

---

## See Also

- [Configuration Guide](configuration.md) - Detailed configuration options
- [Installation Guide](installation.md) - Setup instructions
- [README](../README.md) - Project overview
- [FAQ](faq.md) - Common questions

---

**Last Updated**: December 2025  
**Version**: 0.2.0
