# text2speech Documentation

Welcome to the text2speech module documentation. This module provides text-to-speech functionality using the Kokoro-82M TTS model with thread-safe audio queue management.

---

## Quick Links

- 📖 [Main README](../README.md) - Project overview and quick start
- 🔧 [Installation Guide](installation.md) - Detailed installation instructions
- 📚 [API Reference](api_reference.md) - Complete API documentation
- ⚙️ [Configuration Guide](configuration.md) - Configuration options and examples
- ❓ [FAQ](faq.md) - Frequently asked questions
- 🤝 [Contributing](../CONTRIBUTING.md) - How to contribute

---

## Overview

The text2speech module provides:

- **Thread-safe audio queue** - Prevents device conflicts with serialized playback
- **Kokoro-82M TTS** - High-quality, open-source speech synthesis
- **Priority-based queueing** - Urgent messages play first
- **Automatic duplicate detection** - Prevents repetitive speech
- **YAML configuration** - Easy customization
- **Multiple voices** - American and British English
- **CLI support** - Command-line interface

---

## Documentation Structure

### Getting Started

1. **[Installation Guide](installation.md)**
   - System requirements
   - Platform-specific instructions
   - Dependency installation
   - Verification steps

2. **[Main README](../README.md)**
   - Quick start examples
   - Basic usage patterns
   - Feature overview

### Core Documentation

3. **[API Reference](api_reference.md)**
   - Text2Speech class
   - AudioQueueManager class
   - Config class
   - Complete method documentation
   - Type hints and examples

4. **[Configuration Guide](configuration.md)**
   - YAML configuration files
   - Audio settings
   - TTS settings
   - Queue settings
   - Voice selection
   - Best practices

### Help and Support

5. **[FAQ](faq.md)**
   - Common questions
   - Troubleshooting
   - Performance tips
   - Integration examples

---

## Quick Start

### Installation

```bash
git clone https://github.com/dgaida/text2speech.git
cd text2speech
pip install -r requirements.txt
```

### Basic Usage

```python
from text2speech import Text2Speech

# Initialize (queue enabled by default)
tts = Text2Speech(el_api_key="dummy_key")

# Queue speech
tts.speak("Hello, world!")

# Urgent message
tts.speak("Warning!", priority=10)

# Wait for completion
tts.speak("Important", blocking=True)

# Cleanup
tts.shutdown()
```

### Configuration File

Create `config.yaml`:

```yaml
audio:
  output_device: null
  default_volume: 0.8

tts:
  kokoro:
    voice: "af_heart"
    speed: 1.0

logging:
  verbose: false
  log_level: "INFO"
```

---

## Key Concepts

### Audio Queue Manager

The audio queue manager serializes audio playback to prevent ALSA/PortAudio device conflicts. It provides:

- **Priority Queue**: Urgent messages play first
- **Duplicate Detection**: Skips repeated messages
- **Non-blocking**: Queue and continue execution
- **Statistics**: Monitor queue performance

### Voice Options

**American English:**
- `af_heart` - Female, warm (default)
- `af_nicole` - Female, professional
- `am_adam` - Male, authoritative
- `am_michael` - Male, friendly

**British English:**
- `bf_emma` - Female, elegant
- `bf_isabella` - Female, sophisticated
- `bm_lewis` - Male, refined
- `bm_george` - Male, distinguished

### Configuration Priority

1. Constructor parameters (highest)
2. Runtime changes (`set_voice()`, etc.)
3. Config file
4. Built-in defaults (lowest)

---

## Common Tasks

### Change Voice

```python
tts.set_voice("am_adam")
tts.set_speed(1.2)
tts.set_volume(0.7)
```

### Monitor Queue

```python
stats = tts.get_queue_stats()
print(f"Queued: {stats['messages_queued']}")
print(f"Played: {stats['messages_played']}")
```

### Select Audio Device

```python
from text2speech import Config

config = Config()
config.set("audio.output_device", 3)

tts = Text2Speech(el_api_key="dummy_key", config=config)
```

---

## Examples

### Priority-Based Messaging

```python
tts = Text2Speech(el_api_key="dummy_key")

# Normal priority
tts.speak("Loading data...")

# High priority (plays first)
tts.speak("Error occurred!", priority=10)

tts.shutdown()
```

### Multiple Voices

```python
robot = Text2Speech(el_api_key="dummy_key")
robot.set_voice("am_adam")
robot.speak("I am a robot")

narrator = Text2Speech(el_api_key="dummy_key")
narrator.set_voice("bm_lewis")
narrator.speak("The narrator speaks")

robot.shutdown()
narrator.shutdown()
```

### Blocking Mode

```python
tts = Text2Speech(el_api_key="dummy_key")

tts.speak("Please wait", blocking=True)
print("Speech finished!")

tts.shutdown()
```

---

## Architecture

### Pipeline Overview

```
User Input → Text2Speech → AudioQueueManager → Worker Thread →
Kokoro Model → Audio Tensor → Resampling → Normalization →
Audio Playback
```

### Components

- **Text2Speech**: Main TTS coordinator
- **AudioQueueManager**: Thread-safe priority queue
- **Config**: YAML configuration manager
- **KPipeline**: Kokoro-82M speech synthesis
- **Audio Processing**: Resampling and normalization

---

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=text2speech --cov-report=term

# Specific tests
pytest tests/test_audio_queue.py
pytest tests/test_text2speech.py
pytest tests/test_config.py
```

### Test Coverage

The test suite includes:
- ✅ Initialization tests
- ✅ Audio queue tests
- ✅ Configuration tests
- ✅ TTS functionality tests
- ✅ CLI tests
- ✅ Integration tests

---

## Development

### Code Quality

```bash
# Format
black .

# Lint
ruff check .

# Type check
mypy text2speech

# Security scan
bandit -r text2speech/
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

---

## Troubleshooting

### No Audio Output

1. Check devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`
2. Test sounddevice: See [FAQ](faq.md#no-audio-output)
3. Enable verbose mode: `verbose=True`

### Device Conflicts

Use the audio queue (enabled by default):
```python
tts = Text2Speech(enable_queue=True)
```

### Performance Issues

Enable GPU acceleration:
```yaml
performance:
  use_gpu: true
```

---

## Resources

### External Links

- [Kokoro-82M on Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro GitHub](https://github.com/hexgrad/kokoro)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [sounddevice Documentation](https://python-sounddevice.readthedocs.io/)

### Community

- [GitHub Issues](https://github.com/dgaida/text2speech/issues)
- [GitHub Discussions](https://github.com/dgaida/text2speech/discussions)

---

## License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

Kokoro-82M is licensed under Apache 2.0, allowing free commercial and personal use.

---

## Contact

**Daniel Gaida**  
Email: daniel.gaida@th-koeln.de  
GitHub: [@dgaida](https://github.com/dgaida)

---

## Version History

### v0.2.0 (Current)
- Added AudioQueueManager for thread-safe playback
- Added YAML configuration system
- Added CLI support
- Added priority-based queueing
- Added duplicate detection
- Enhanced logging system

### v0.1.0
- Initial release
- Kokoro TTS support
- Asynchronous speech generation
- Basic audio processing

---

**Last Updated**: December 2025  
**Version**: 0.2.0
