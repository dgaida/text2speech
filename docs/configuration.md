# Configuration Guide

This guide explains how to configure the text2speech module for different use cases.

---

## Table of Contents

- [Overview](#overview)
- [Configuration Files](#configuration-files)
- [Configuration Options](#configuration-options)
  - [Audio Settings](#audio-settings)
  - [TTS Settings](#tts-settings)
  - [Logging Settings](#logging-settings)
  - [Performance Settings](#performance-settings)
- [Queue Settings](#queue-settings)
- [Usage Examples](#usage-examples)
- [Advanced Configuration](#advanced-configuration)
- [Audio Device Selection](#audio-device-selection)
- [Voice Selection](#voice-selection)
- [Best Practices](#best-practices)

---

## Overview

The text2speech module uses YAML configuration files to manage settings. Configuration can be:
- Loaded from default locations
- Specified via file path
- Modified programmatically at runtime
- Overridden by constructor parameters

### Configuration Priority

1. **Constructor parameters** (highest priority) - e.g., `enable_queue=True`
2. **Programmatic overrides** - e.g., `tts.set_voice("am_adam")`
3. **Specified config file** (`config_path` parameter)
4. **Default search locations**
5. **Built-in defaults** (lowest priority)

---

## Configuration Files

### Default Search Locations

The module searches for `config.yaml` in the following order:

1. `./config.yaml` (current directory)
2. `./config.yml`
3. `~/.text2speech/config.yaml` (user home)
4. `~/.config/text2speech/config.yaml` (XDG config)
5. `/etc/text2speech/config.yaml` (system-wide, Linux only)

### Creating a Configuration File

```bash
# Copy the example config
cp config.yaml ~/.text2speech/config.yaml

# Edit with your preferred editor
nano ~/.text2speech/config.yaml
```

---

## Configuration Options

### Audio Settings

Controls audio output behavior.

```yaml
audio:
  # Output device ID (null = system default)
  # Run: python -c "import sounddevice as sd; print(sd.query_devices())"
  output_device: null

  # Default volume (0.0 to 1.0)
  default_volume: 0.8

  # Sample rate (24000 is Kokoro's native rate)
  sample_rate: 24000
```

#### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `output_device` | int/null | `null` | Device ID | Specific audio device or system default |
| `default_volume` | float | `0.8` | 0.0-1.0 | Playback volume multiplier |
| `sample_rate` | int | `24000` | 8000-48000 | Audio sample rate in Hz |

#### Examples

**Using specific audio device**:
```yaml
audio:
  output_device: 3  # Use device ID 3
  default_volume: 0.9
```

**High-quality audio output**:
```yaml
audio:
  sample_rate: 48000
  default_volume: 0.85
```

**Low volume for background use**:
```yaml
audio:
  default_volume: 0.4
```

---

### TTS Settings

Configure the text-to-speech engine and voice parameters.

```yaml
tts:
  # Primary TTS engine: "kokoro" or "elevenlabs"
  engine: "kokoro"

  kokoro:
    # Language code
    # 'a' = American English
    # 'b' = British English
    # 'j' = Japanese (requires: pip install misaki[ja])
    # 'z' = Mandarin Chinese (requires: pip install misaki[zh])
    lang_code: "a"

    # Voice selection
    # American: af_heart, af_nicole, am_adam, am_michael
    # British: bf_emma, bf_isabella, bm_lewis, bm_george
    voice: "af_heart"

    # Speech speed (0.5 to 2.0)
    speed: 1.0

    # Pattern to split text (regex)
    split_pattern: "\\n+"

  # ElevenLabs settings (legacy, deprecated)
  elevenlabs:
    voice: "Brian"
    model: "eleven_multilingual_v2"
```

#### Kokoro Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `lang_code` | string | `"a"` | a, b, j, z | Language variant |
| `voice` | string | `"af_heart"` | See below | Voice identifier |
| `speed` | float | `1.0` | 0.5-2.0 | Speech rate multiplier |
| `split_pattern` | string | `"\\n+"` | Regex | Text splitting pattern |

#### Available Voices

**American English (`lang_code: "a"`)**:
- `af_heart` - Female, warm and clear (default)
- `af_nicole` - Female, professional
- `am_adam` - Male, deep and authoritative
- `am_michael` - Male, friendly

**British English (`lang_code: "b"`)**:
- `bf_emma` - Female, elegant
- `bf_isabella` - Female, sophisticated
- `bm_lewis` - Male, refined
- `bm_george` - Male, distinguished

#### Examples

**Fast speech for announcements**:
```yaml
tts:
  engine: "kokoro"
  kokoro:
    lang_code: "a"
    voice: "am_adam"
    speed: 1.3
```

**Slow, clear speech for accessibility**:
```yaml
tts:
  engine: "kokoro"
  kokoro:
    voice: "af_nicole"
    speed: 0.8
```

**British English narrator**:
```yaml
tts:
  engine: "kokoro"
  kokoro:
    lang_code: "b"
    voice: "bm_lewis"
    speed: 1.0
```

---

### Logging Settings

Control debug output and logging behavior.

```yaml
logging:
  # Enable verbose output
  verbose: false

  # Log file path (null = no file logging)
  log_file: null

  # Log level: "DEBUG", "INFO", "WARNING", "ERROR"
  log_level: "INFO"
```

#### Parameters

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `verbose` | bool | `false` | true/false | Print detailed debug info |
| `log_file` | string/null | `null` | File path | Log to file if specified |
| `log_level` | string | `"INFO"` | DEBUG, INFO, WARNING, ERROR | Logging threshold |

#### Examples

**Development debugging**:
```yaml
logging:
  verbose: true
  log_file: "/tmp/text2speech.log"
  log_level: "DEBUG"
```

**Production use (quiet)**:
```yaml
logging:
  verbose: false
  log_file: "/var/log/text2speech.log"
  log_level: "WARNING"
```

**No logging**:
```yaml
logging:
  verbose: false
  log_file: null
  log_level: "ERROR"
```

---

### Performance Settings

Optimize performance for your hardware.

```yaml
performance:
  # Use GPU if available
  use_gpu: true

  # Number of threads for audio processing
  num_threads: 1
```

#### Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `use_gpu` | bool | `true` | true/false | Enable CUDA/MPS acceleration |
| `num_threads` | int | `1` | 1-8 | Audio processing threads |

#### Examples

**CPU-only mode**:
```yaml
performance:
  use_gpu: false
  num_threads: 2
```

**GPU acceleration**:
```yaml
performance:
  use_gpu: true
  num_threads: 1
```

---

## Queue Settings

Configure audio queue behavior (set via constructor, not config file).

### Constructor Parameters

```python
Text2Speech(
    enable_queue=True,          # Enable queue manager
    max_queue_size=50,          # Maximum queued messages
    duplicate_timeout=2.0       # Skip duplicates within window (seconds)
)
```

### Examples

**Disable queue (legacy mode)**:
```python
tts = Text2Speech(el_api_key="dummy_key", enable_queue=False)
```

**Large queue for busy applications**:
```python
tts = Text2Speech(
    el_api_key="dummy_key",
    enable_queue=True,
    max_queue_size=200,
    duplicate_timeout=5.0
)
```

**Strict duplicate detection**:
```python
tts = Text2Speech(
    el_api_key="dummy_key",
    duplicate_timeout=10.0  # 10 second window
)
```

---

## Usage Examples

### Basic Usage with Config

```python
from text2speech import Text2Speech

# Load default config
tts = Text2Speech(el_api_key="dummy_key")

# Load specific config file
tts = Text2Speech(
    el_api_key="dummy_key",
    config_path="/path/to/config.yaml"
)

# Override verbose setting
tts = Text2Speech(
    el_api_key="dummy_key",
    verbose=True
)

tts.speak("Hello!")
tts.shutdown()
```

### Programmatic Configuration

```python
from text2speech import Text2Speech, Config

# Create custom config
config = Config()
config.set("audio.default_volume", 0.5)
config.set("tts.kokoro.voice", "am_adam")
config.set("tts.kokoro.speed", 1.2)

# Use custom config
tts = Text2Speech(el_api_key="dummy_key", config=config)
tts.speak("Configured speech")
tts.shutdown()
```

### Runtime Configuration Changes

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

# Change voice
tts.set_voice("bf_emma")

# Adjust speed
tts.set_speed(1.5)

# Change volume
tts.set_volume(0.6)

# Generate speech with new settings
tts.speak("Hello with new settings")

tts.shutdown()
```

### Saving Configuration

```python
from text2speech import Config

# Load and modify config
config = Config()
config.set("audio.output_device", 3)
config.set("tts.kokoro.voice", "am_michael")

# Save to file
config.save_to_file("my_config.yaml")
```

---

## Advanced Configuration

### Multiple Configurations

**config_robot.yaml**:
```yaml
audio:
  output_device: 2
  default_volume: 0.9
tts:
  kokoro:
    voice: "am_adam"
    speed: 1.1
```

**config_presentation.yaml**:
```yaml
audio:
  default_volume: 0.7
tts:
  kokoro:
    voice: "bf_emma"
    speed: 0.9
```

**Usage**:
```python
# Robot voice
tts_robot = Text2Speech(
    el_api_key="dummy_key",
    config_path="config_robot.yaml"
)

# Presentation voice
tts_presentation = Text2Speech(
    el_api_key="dummy_key",
    config_path="config_presentation.yaml"
)

tts_robot.speak("Robot speaking")
tts_presentation.speak("Presentation mode")

tts_robot.shutdown()
tts_presentation.shutdown()
```

### Environment-Specific Configs

```python
import os
from text2speech import Text2Speech

# Select config based on environment
env = os.getenv("ENVIRONMENT", "development")
config_path = f"config_{env}.yaml"

tts = Text2Speech(
    el_api_key="dummy_key",
    config_path=config_path
)

tts.speak("Environment-specific config")
tts.shutdown()
```

### Conditional Configuration

```python
from text2speech import Config, Text2Speech
import torch

# Configure based on hardware
config = Config()

if torch.cuda.is_available():
    config.set("performance.use_gpu", True)
    print("Using GPU acceleration")
else:
    config.set("performance.use_gpu", False)
    config.set("performance.num_threads", 2)
    print("Using CPU with 2 threads")

tts = Text2Speech(el_api_key="dummy_key", config=config)
tts.speak("Hardware-optimized config")
tts.shutdown()
```

---

## Audio Device Selection

### Listing Available Devices

```python
import sounddevice as sd

# List all devices
devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"{i}: {device['name']} (out: {device['max_output_channels']})")
```

Example output:
```
0: Built-in Audio (out: 2)
1: USB Headphones (out: 2)
2: HDMI Audio (out: 8)
3: Bluetooth Speaker (out: 2)
```

### Selecting a Device

**Via configuration file**:
```yaml
audio:
  output_device: 1  # USB Headphones
```

**Programmatically**:
```python
from text2speech import Text2Speech, Config

config = Config()
config.set("audio.output_device", 1)

tts = Text2Speech(el_api_key="dummy_key", config=config)
tts.speak("Using USB headphones")
tts.shutdown()
```

**At runtime**:
```python
import sounddevice as sd

# Set default device
sd.default.device[1] = 1  # Output device index
```

### Device-Specific Settings

```yaml
# High-end DAC with 192kHz support
audio:
  output_device: 5
  sample_rate: 48000
  default_volume: 0.7

# Bluetooth speaker (may have latency)
audio:
  output_device: 3
  sample_rate: 24000
  default_volume: 0.9
```

---

## Voice Selection

### Choosing the Right Voice

**Considerations**:
- **Use case**: Professional vs casual, narration vs conversation
- **Audience**: Age group, preferences
- **Content**: Technical, storytelling, announcements
- **Gender preference**: Male, female, or neutral

### Voice Characteristics

| Voice | Gender | Style | Best For |
|-------|--------|-------|----------|
| `af_heart` | Female | Warm, clear | General use, friendly tone |
| `af_nicole` | Female | Professional | Business, presentations |
| `am_adam` | Male | Authoritative | Announcements, narration |
| `am_michael` | Male | Friendly | Casual conversation |
| `bf_emma` | Female | Elegant | Formal content, literature |
| `bf_isabella` | Female | Sophisticated | Professional, refined |
| `bm_lewis` | Male | Refined | Narration, audiobooks |
| `bm_george` | Male | Distinguished | Formal announcements |

### Voice Testing Script

```python
from text2speech import Text2Speech

voices = [
    "af_heart", "af_nicole",
    "am_adam", "am_michael",
    "bf_emma", "bf_isabella",
    "bm_lewis", "bm_george"
]

tts = Text2Speech(el_api_key="dummy_key")
test_text = "This is a voice sample for comparison."

for voice in voices:
    print(f"\nTesting voice: {voice}")
    tts.set_voice(voice)
    tts.speak(test_text, blocking=True)

tts.shutdown()
```

---

## Best Practices

### 1. Configuration Management

✅ **Do**:
- Keep configuration files in version control
- Use environment-specific configs
- Document custom settings
- Test configuration changes
- Use queue system for multi-threaded applications

❌ **Don't**:
- Hardcode settings in application code
- Use extreme values (volume > 1.0, speed > 2.0)
- Ignore default settings without reason
- Disable queue without understanding implications

### 2. Audio Quality

✅ **Recommendations**:
```yaml
audio:
  sample_rate: 24000  # Native Kokoro rate
  default_volume: 0.8  # Safe default
```

### 3. Performance Optimization

**For real-time applications**:
```yaml
performance:
  use_gpu: true
  num_threads: 1

tts:
  kokoro:
    speed: 1.0
```

**For batch processing**:
```yaml
performance:
  use_gpu: true
  num_threads: 2
```

### 4. Queue Configuration

**For high-traffic applications**:
```python
tts = Text2Speech(
    el_api_key="dummy_key",
    enable_queue=True,
    max_queue_size=200,
    duplicate_timeout=5.0
)
```

**For simple applications**:
```python
tts = Text2Speech(
    el_api_key="dummy_key",
    enable_queue=True,  # Still recommended
    max_queue_size=50,
    duplicate_timeout=2.0
)
```

### 5. Logging Strategy

**Development**:
```yaml
logging:
  verbose: true
  log_level: "DEBUG"
  log_file: "dev.log"
```

**Production**:
```yaml
logging:
  verbose: false
  log_level: "WARNING"
  log_file: "/var/log/text2speech.log"
```

### 6. Voice Selection

- **Test multiple voices** for your use case
- **Consider accent** (American vs British)
- **Match tone to content** (formal vs casual)
- **Adjust speed** based on audience (0.8-1.2 typically)

---

## Configuration Examples by Use Case

### Robotics Application

```yaml
audio:
  output_device: null
  default_volume: 0.9
  sample_rate: 24000

tts:
  engine: "kokoro"
  kokoro:
    lang_code: "a"
    voice: "am_adam"
    speed: 1.1

logging:
  verbose: false
  log_level: "INFO"

performance:
  use_gpu: true
  num_threads: 1
```

```python
tts = Text2Speech(
    el_api_key="dummy_key",
    config_path="robot_config.yaml",
    enable_queue=True,
    max_queue_size=100,
    duplicate_timeout=3.0
)
```

### Accessibility Tool

```yaml
audio:
  default_volume: 0.85
  sample_rate: 24000

tts:
  kokoro:
    voice: "af_nicole"
    speed: 0.85  # Slower for clarity

logging:
  verbose: true
  log_level: "INFO"
```

```python
tts = Text2Speech(
    el_api_key="dummy_key",
    config_path="accessibility_config.yaml",
    enable_queue=True
)
```

### Audiobook Narration

```yaml
audio:
  output_device: 5  # High-quality DAC
  default_volume: 0.75
  sample_rate: 48000

tts:
  kokoro:
    lang_code: "b"
    voice: "bm_lewis"
    speed: 0.95

performance:
  use_gpu: true
```

### Interactive Kiosk

```yaml
audio:
  output_device: 2
  default_volume: 0.95
  sample_rate: 24000

tts:
  kokoro:
    voice: "af_heart"
    speed: 1.0

logging:
  verbose: false
  log_level: "WARNING"
  log_file: "/var/log/kiosk_tts.log"
```

```python
tts = Text2Speech(
    el_api_key="dummy_key",
    config_path="kiosk_config.yaml",
    enable_queue=True,
    max_queue_size=30,
    duplicate_timeout=5.0
)
```

---

## Troubleshooting Configuration

### Config Not Loading

```python
from text2speech import Config

# Debug config loading
config = Config()
print("Config location:", config._find_config_file())
print("Full config:", config.to_dict())
```

### Invalid Configuration

```python
try:
    config = Config("/path/to/config.yaml")
except Exception as e:
    print(f"Config error: {e}")
```

### Testing Configuration

```python
from text2speech import Text2Speech, Config

# Load and test config
config = Config("test_config.yaml")
print("Audio device:", config.audio_output_device)
print("Voice:", config.kokoro_voice)
print("Speed:", config.kokoro_speed)

# Test with TTS
tts = Text2Speech(el_api_key="dummy_key", config=config)
tts.speak("Configuration test", blocking=True)
tts.shutdown()
```

---

## Next Steps

- Review the [API Reference](api_reference.md)
- Check the [Installation Guide](installation.md)
- Read the [FAQ](faq.md)
- Explore examples in `main.py`

---

**Last Updated**: December 2025  
**Version**: 0.2.0
