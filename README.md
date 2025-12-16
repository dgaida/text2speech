# text2speech

The **text2speech** module provides **text-to-speech (TTS)** functionality for robotics and other applications. It supports asynchronous text-to-speech generation, thread-safe audio queueing, and robust audio playback.

Although initially designed to use **ElevenLabs**, this implementation now relies on the **Kokoro** model for speech synthesis, featuring an advanced audio queue manager for conflict-free playback.

---

## Badges

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/dgaida/text2speech/branch/master/graph/badge.svg)](https://codecov.io/gh/dgaida/text2speech)
[![Code Quality](https://github.com/dgaida/text2speech/actions/workflows/lint.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/lint.yml)
[![Tests](https://github.com/dgaida/text2speech/actions/workflows/tests.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/tests.yml)
[![CodeQL](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Features

- ✅ **Thread-safe audio queue** - Prevents ALSA/PortAudio conflicts with serialized playback
- ✅ Asynchronous text-to-speech synthesis
- ✅ Uses **Kokoro-82M** for natural-sounding voices (Apache 2.0 licensed)
- ✅ Priority-based message queueing
- ✅ Automatic duplicate message detection
- ✅ YAML-based configuration system
- ✅ Automatic resampling and volume normalization for playback
- ✅ Safe, thread-based audio playback
- ✅ Support for multiple languages and voices
- ✅ Command-line interface
- ✅ Comprehensive test suite with >90% coverage
- ⚙️ Legacy ElevenLabs integration retained for backward compatibility (disabled by default)

---

## Installation

### From Source

Clone the repository and install dependencies:

```bash
git clone https://github.com/dgaida/text2speech.git
cd text2speech
pip install -r requirements.txt
```

### Optional Dependencies

For development and testing:

```bash
pip install pytest pytest-cov ruff black mypy bandit
```

If you want optional support for ElevenLabs (legacy mode):

```bash
pip install elevenlabs
```

---

## Quick Start

### Basic Usage with Queue (Recommended)

```python
from text2speech import Text2Speech

# Initialize the TTS system (queue enabled by default)
tts = Text2Speech(el_api_key="dummy_key", verbose=True)

# Queue messages for playback (non-blocking)
tts.speak("Hello, this is your robot speaking!")
tts.speak("This message will play after the first one.")

# High-priority urgent message
tts.speak("Warning: Low battery!", priority=10)

# Cleanup when done
tts.shutdown()
```

### Blocking Mode (Wait for Completion)

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

# Wait for speech to complete before continuing
tts.speak("Please wait for this message.", blocking=True)
print("Message finished!")

tts.shutdown()
```

### Legacy Async Mode (Without Queue)

```python
from text2speech import Text2Speech

# Disable queue for legacy threading behavior
tts = Text2Speech(el_api_key="dummy_key", enable_queue=False)

# Generate and play speech asynchronously
thread = tts.call_text2speech_async("Hello, world!")
thread.join()  # Wait for speech playback to complete
```

### Configuration File

Create a `config.yaml` file:

```yaml
audio:
  output_device: null  # null = system default
  default_volume: 0.8
  sample_rate: 24000

tts:
  engine: "kokoro"
  kokoro:
    lang_code: "a"  # 'a' = American, 'b' = British
    voice: "af_heart"  # See voice options below
    speed: 1.0

logging:
  verbose: false
  log_level: "INFO"

performance:
  use_gpu: true
```

Then use it:

```python
from text2speech import Text2Speech

tts = Text2Speech(config_path="config.yaml")
tts.speak("Configured speech!")
tts.shutdown()
```

### Command-Line Interface

```bash
# Basic usage
text2speech "Hello, world!"

# With custom voice
text2speech "Hello" --voice am_adam

# With custom config
text2speech "Hello" --config my_config.yaml
```

---

## Available Voices

### American English (`lang_code: "a"`)
- `af_heart` - Female, warm and clear (default)
- `af_nicole` - Female, professional
- `am_adam` - Male, deep and authoritative
- `am_michael` - Male, friendly

### British English (`lang_code: "b"`)
- `bf_emma` - Female, elegant
- `bf_isabella` - Female, sophisticated
- `bm_lewis` - Male, refined
- `bm_george` - Male, distinguished

### Voice Selection

```python
tts = Text2Speech(el_api_key="dummy_key")

# Change voice at runtime
tts.set_voice("am_adam")
tts.speak("Speaking with Adam's voice")

# Adjust speed (0.5 to 2.0)
tts.set_speed(1.2)

# Adjust volume (0.0 to 1.0)
tts.set_volume(0.7)

tts.shutdown()
```

---

## Audio Queue Features

The audio queue manager prevents ALSA/PortAudio device conflicts by serializing audio playback.

### Key Features

- **Priority Queue**: Urgent messages play first
- **Duplicate Detection**: Skips repeated messages within timeout window
- **Non-blocking**: Queue messages and continue execution
- **Statistics Tracking**: Monitor queue performance
- **Automatic Cleanup**: Graceful shutdown handling

### Queue Statistics

```python
tts = Text2Speech(el_api_key="dummy_key")

# Queue several messages
tts.speak("Message 1")
tts.speak("Message 2")
tts.speak("Urgent!", priority=10)

# Check statistics
stats = tts.get_queue_stats()
print(stats)
# {
#     'messages_queued': 3,
#     'messages_played': 1,
#     'messages_skipped_duplicate': 0,
#     'messages_skipped_full': 0,
#     'errors': 0
# }

tts.shutdown()
```

### Custom Queue Settings

```python
from text2speech import Text2Speech

tts = Text2Speech(
    el_api_key="dummy_key",
    enable_queue=True,
    max_queue_size=100,  # Larger queue
    duplicate_timeout=5.0  # 5 second duplicate detection window
)

tts.speak("Custom queue settings")
tts.shutdown()
```

---

## Running Examples

The `main.py` file contains several example use cases:

```bash
# Run all examples
python main.py

# Run with verbose output
python main.py --verbose

# Run a specific example (1-5)
python main.py --example 3

# Run interactive mode
python main.py --interactive
```

### Available Examples

1. **Simple Greeting** - Basic TTS demonstration
2. **Multiple Sentences** - Sequential speech generation
3. **Multilingual** - Speaking in different languages
4. **Long Text** - Handling longer passages
5. **Interactive Mode** - User input to speech

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=text2speech --cov-report=term --cov-report=html
```

### Run Specific Test Classes

```bash
# Test initialization
pytest tests/test_text2speech.py::TestText2SpeechInitialization

# Test audio queue
pytest tests/test_audio_queue.py::TestAudioQueueManager

# Test configuration
pytest tests/test_config.py::TestConfigDefaults
```

### Test Coverage

The test suite includes:
- ✅ Initialization tests
- ✅ Asynchronous operation tests
- ✅ Audio queue management tests
- ✅ Configuration system tests
- ✅ Audio generation and playback tests
- ✅ Command-line interface tests
- ✅ Error handling tests
- ✅ Edge case tests
- ✅ Integration tests

---

## Architecture

### Text-to-Speech Pipeline with Queue

```
User Input → Text2Speech → AudioQueueManager → Worker Thread →
Kokoro Model → Audio Tensor → Resampling → Volume Normalization →
Audio Playback
```

### Key Components

1. **Text2Speech**: Main class coordinating TTS operations
2. **AudioQueueManager**: Thread-safe priority queue for audio playback
3. **Config**: YAML-based configuration management
4. **Kokoro Pipeline**: Speech synthesis engine (82M parameters)
5. **Audio Processing**: Resampling and normalization
6. **Safe Playback**: Thread-safe audio output with error handling

---

## Advanced Usage

### Multiple TTS Instances

```python
from text2speech import Text2Speech

# Robot voice
robot_tts = Text2Speech(el_api_key="dummy_key")
robot_tts.set_voice("am_adam")
robot_tts.set_speed(1.1)

# Narrator voice
narrator_tts = Text2Speech(el_api_key="dummy_key")
narrator_tts.set_voice("bm_lewis")
narrator_tts.set_speed(0.95)

robot_tts.speak("I am a robot.")
narrator_tts.speak("The narrator speaks.")

robot_tts.shutdown()
narrator_tts.shutdown()
```

### Context Manager Support

```python
from text2speech import Text2Speech

with Text2Speech(el_api_key="dummy_key") as tts:
    tts.speak("Automatic cleanup!")
    # Shutdown called automatically
```

### Adjusting Voice and Speed

Modify the `_text2speech_kokoro` method to change voice characteristics:

```python
tts.set_voice('af_heart')  # Change voice
tts.set_speed(1.2)         # Adjust speed (0.5 - 2.0)
tts.set_volume(0.8)        # Adjust volume (0.0 - 1.0)
```

---

## Development

### Code Quality Tools

The project uses several tools to maintain code quality:

```bash
# Format code with Black
black .

# Lint with Ruff
ruff check .

# Type checking with mypy
mypy text2speech --ignore-missing-imports

# Security scanning with Bandit
bandit -r text2speech/
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
pip install pre-commit
pre-commit install
```

### CI/CD Pipeline

The project includes GitHub Actions workflows for:
- 🔍 Code quality checks (Ruff, Black, mypy)
- 🧪 Automated testing across multiple Python versions and OS
- 🔒 Security scanning (CodeQL, Bandit)
- 📦 Dependency review
- 🚀 Automated releases

---

## Troubleshooting

### No Audio Output

If you don't hear any audio:

1. Check your default audio device:
```python
import sounddevice as sd
print(sd.query_devices())
```

2. Verify sounddevice can play audio:
```python
import sounddevice as sd
import numpy as np
sd.play(np.random.randn(24000), samplerate=24000)
sd.wait()
```

3. Set specific device in config:
```yaml
audio:
  output_device: 2  # Replace with your device ID
```

### ALSA/PortAudio Errors

If you see "device busy" errors:

```python
# Use the queue system (enabled by default)
tts = Text2Speech(el_api_key="dummy_key", enable_queue=True)
```

The queue manager serializes audio playback to prevent conflicts.

### Import Errors

If you encounter import errors:

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Verify installation
python -c "import kokoro; import torch; import sounddevice"
```

### Performance Issues

For slow performance:

1. Ensure PyTorch is using GPU acceleration (if available)
2. Enable GPU in config:
```yaml
performance:
  use_gpu: true
```

---

## System Requirements

- **Python**: 3.9 or higher
- **Operating Systems**: Ubuntu, Windows, macOS
- **Audio**: System with audio output device
- **Memory**: Minimum 2GB RAM recommended, 4GB for optimal performance
- **Disk Space**: ~500MB for model files
- **GPU** (optional): CUDA-capable GPU for faster inference

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Kokoro-82M**: For providing the excellent open-source TTS model (Apache 2.0)
- **PyTorch**: For the deep learning framework
- **sounddevice**: For audio playback capabilities
- **ElevenLabs**: For initial inspiration (legacy support)

---

## Contact

**Daniel Gaida**  
Email: daniel.gaida@th-koeln.de  
GitHub: [@dgaida](https://github.com/dgaida)

---

## Roadmap

- [x] Audio queue manager for conflict-free playback
- [x] YAML configuration system
- [x] Command-line interface
- [ ] Add support for custom voice models
- [ ] Implement audio caching for repeated phrases
- [ ] Support for SSML (Speech Synthesis Markup Language)
- [ ] Real-time streaming TTS
- [ ] Voice cloning capabilities
- [ ] Web API endpoint for remote TTS
- [ ] Docker containerization
- [ ] Plugin system for custom audio processors
