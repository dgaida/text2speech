# Installation

This guide will walk you through installing `text2speech` and its dependencies.

## System Requirements

- **Python**: Version 3.9 or higher.
- **Operating Systems**: Ubuntu (tested), Windows, macOS.
- **Audio**: A system with a working audio output device.
- **Memory**: Minimum 2GB RAM recommended (4GB for optimal performance).
- **Disk Space**: Approx. 500MB for model files.

## Installation from Source

Clone the repository and install the package in editable mode:

```bash
git clone https://github.com/dgaida/text2speech.git
cd text2speech
pip install -e .
```

This will automatically install all core dependencies such as `torch`, `kokoro`, and `sounddevice`.

## Optional Dependencies

For developers and special use cases:

### Development Tools
```bash
pip install -e ".[dev]"
```
This installs tools like `pytest`, `ruff`, `black`, and `mypy`.

### ElevenLabs (Legacy Support)
If you wish to use the old ElevenLabs backend:
```bash
pip install elevenlabs
```

## Platform-Specific Notes

### Linux (Ubuntu/Debian)
You may need to install development libraries for audio support:

```bash
sudo apt-get update
sudo apt-get install libasound2-dev libportaudio2
```

### Windows
Installation via `pip` should be sufficient in most cases. Ensure your sound drivers are up to date.

## Verifying the Installation

You can test the installation using the integrated CLI tool:

```bash
text2speech "Installation tested successfully."
```

If you hear a voice, the system is correctly configured.
