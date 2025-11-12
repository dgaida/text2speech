# text2speech

The **text2speech** module provides **text-to-speech (TTS)** functionality for robotics and other applications. It supports asynchronous text-to-speech generation and robust, safe audio playback.

Although initially designed to use **ElevenLabs**, this implementation now relies on the **Kokoro** model for speech synthesis.

---

## Badges

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://github.com/dgaida/text2speech/actions/workflows/lint.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/lint.yml)
[![Tests](https://github.com/dgaida/text2speech/actions/workflows/tests.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/tests.yml)
[![CodeQL](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Features

- ✅ Asynchronous text-to-speech synthesis
- ✅ Uses **Kokoro** for natural-sounding voices
- ✅ Automatic resampling and volume normalization for playback
- ✅ Safe, thread-based audio playback
- ✅ Support for multiple languages
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

### Basic Usage

```python
from text2speech import Text2Speech

# Initialize the TTS system
tts = Text2Speech(el_api_key="dummy_key", verbose=True)

# Generate and play speech asynchronously
thread = tts.call_text2speech_async("Hello, this is your robot speaking!")
thread.join()  # Wait for speech playback to complete
```

### Multiple Sentences

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

sentences = [
    "This is the first sentence.",
    "Now I'm saying something else.",
    "And finally, this is the last part."
]

for sentence in sentences:
    thread = tts.call_text2speech_async(sentence)
    thread.join()
```

### Multilingual Support

```python
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key")

# English
tts.call_text2speech_async("Welcome to the demonstration.").join()

# German
tts.call_text2speech_async("Willkommen zur Demonstration.").join()

# Spanish
tts.call_text2speech_async("Bienvenido a la demostración.").join()
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

# Test async functionality
pytest tests/test_text2speech.py::TestText2SpeechAsync

# Test audio playback
pytest tests/test_text2speech.py::TestAudioPlayback
```

### Test Coverage

The test suite includes:
- ✅ Initialization tests
- ✅ Asynchronous operation tests
- ✅ Audio generation and playback tests
- ✅ Error handling tests
- ✅ Edge case tests
- ✅ Integration tests

---

## API Reference

### `Text2Speech`

The main class for text-to-speech functionality.

#### Constructor

```python
Text2Speech(el_api_key: str, verbose: bool = False)
```

**Parameters:**
- `el_api_key` (str): API key for ElevenLabs (no longer used, kept for compatibility)
- `verbose` (bool, optional): If True, prints detailed debug information. Defaults to False.

#### Methods

##### `call_text2speech_async(text: str) -> threading.Thread`

Generate speech asynchronously using the Kokoro model.

**Parameters:**
- `text` (str): The text to be spoken

**Returns:**
- `threading.Thread`: The thread handling the asynchronous TTS operation

**Example:**
```python
thread = tts.call_text2speech_async("Hello World")
thread.join()  # Wait for completion
```

##### `verbose() -> bool`

Check whether verbose mode is enabled.

**Returns:**
- `bool`: True if verbose mode is active, otherwise False

---

## Architecture

### Text-to-Speech Pipeline

```
User Input → Text2Speech → Kokoro Model → Audio Tensor →
Resampling → Volume Normalization → Audio Playback
```

### Key Components

1. **Text2Speech**: Main class coordinating TTS operations
2. **Kokoro Pipeline**: Speech synthesis engine
3. **Audio Processing**: Resampling and normalization
4. **Safe Playback**: Thread-safe audio output with error handling

---

## Advanced Configuration

### Custom Audio Device

```python
# In _play_audio_safely, specify a custom device
Text2Speech._play_audio_safely(
    audio_tensor=audio,
    original_sample_rate=24000,
    device=5,  # Custom device ID
    volume=0.8
)
```

### Adjusting Voice and Speed

Modify the `_text2speech_kokoro` method to change voice characteristics:

```python
generator = self._client(
    mytext,
    voice='af_heart',  # Change voice
    speed=1.2,         # Adjust speed (0.5 - 2.0)
    split_pattern=r'\n+'
)
```

### Available Voices

Kokoro supports multiple voices. Common options include:
- `'af_heart'` - American Female (default)
- `'am_adam'` - American Male
- `'bf_emma'` - British Female
- `'bm_lewis'` - British Male

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
2. Reduce text length or split into smaller chunks

---

## System Requirements

- **Python**: 3.8 or higher
- **Operating Systems**: Ubuntu, Windows, macOS
- **Audio**: System with audio output device
- **Memory**: Minimum 2GB RAM recommended
- **Disk Space**: ~500MB for model files

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/dgaida/text2speech.git
cd text2speech

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov ruff black mypy

# Run tests
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Kokoro**: For providing the excellent TTS model
- **PyTorch**: For the deep learning framework
- **sounddevice**: For audio playback capabilities
- **ElevenLabs**: For initial inspiration (legacy support)

---

## Contact

**Daniel Gaida**
Email: daniel.gaida@th-koeln.de
GitHub: [@dgaida](https://github.com/dgaida)

---

## Changelog

### [0.1.0] - 2025-01-XX

#### Added
- Initial release with Kokoro TTS support
- Asynchronous speech generation
- Automatic audio resampling and normalization
- Comprehensive test suite
- Example applications in `main.py`
- CI/CD pipeline with GitHub Actions

#### Changed
- Migrated from ElevenLabs to Kokoro for TTS generation
- Improved error handling and logging

#### Deprecated
- ElevenLabs integration (kept for backward compatibility)

---

## Roadmap

- [ ] Add support for custom voice models
- [ ] Implement audio caching for repeated phrases
- [ ] Add speech rate and pitch control
- [ ] Support for SSML (Speech Synthesis Markup Language)
- [ ] Real-time streaming TTS
- [ ] Voice cloning capabilities
- [ ] Web API endpoint for remote TTS
- [ ] Docker containerization

---

## FAQ

**Q: Why doesn't ElevenLabs work anymore?**
A: The project has migrated to Kokoro for cost-effectiveness. ElevenLabs code is retained for backward compatibility but is not actively used.

**Q: Can I use custom voices?**
A: Yes, Kokoro supports multiple voice options. See the Advanced Configuration section for details.

**Q: Is GPU acceleration supported?**
A: Yes, if PyTorch is configured with CUDA support, the Kokoro model will automatically use GPU acceleration.

**Q: How do I handle long texts?**
A: The system automatically splits long texts at newlines. For very long texts, consider splitting them manually into smaller chunks.

**Q: Can I use this in production?**
A: Yes, but ensure you test thoroughly with your specific hardware and use case. The module includes robust error handling for production use.
