# Installation Guide

This guide provides detailed instructions for installing the text2speech module on various platforms.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [Ubuntu/Debian](#ubuntudebian)
  - [macOS](#macos)
  - [Windows](#windows)
- [Python Environment Setup](#python-environment-setup)
- [Dependency Installation](#dependency-installation)
- [GPU Support](#gpu-support)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher (3.9+ recommended)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: ~500MB for model files
- **Audio**: System audio output device

### Recommended Requirements
- **Python**: 3.11
- **RAM**: 8GB for optimal performance
- **GPU**: CUDA-capable GPU for faster inference (optional)
- **OS**: Ubuntu 20.04+, macOS 11+, or Windows 10+

---

## Quick Installation

For most users, these steps are sufficient:

```bash
# Clone the repository
git clone https://github.com/dgaida/text2speech.git
cd text2speech

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Platform-Specific Instructions

### Ubuntu/Debian

#### 1. Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install portaudio (required for sounddevice)
sudo apt-get install -y portaudio19-dev

# Install build essentials (if not already installed)
sudo apt-get install -y build-essential python3-dev

# Optional: Install ALSA utilities for audio configuration
sudo apt-get install -y alsa-utils
```

#### 2. Verify Audio Setup

```bash
# List audio devices
aplay -l

# Test audio output
speaker-test -t wav -c 2
```

#### 3. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install text2speech dependencies
pip install -r requirements.txt
```

#### Common Ubuntu Issues

**Issue: `portaudio.h` not found**
```bash
sudo apt-get install portaudio19-dev
```

**Issue: Permission denied for audio device**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Log out and back in for changes to take effect
```

**Issue: No sound output**
```bash
# Check if sound is muted
amixer get Master

# Set volume
amixer set Master 80%
```

---

### macOS

#### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install System Dependencies

```bash
# Install portaudio
brew install portaudio

# Optional: Install ffmpeg for additional audio format support
brew install ffmpeg
```

#### 3. Install Python

```bash
# Install Python 3.11 (recommended)
brew install python@3.11

# Verify installation
python3.11 --version
```

#### 4. Setup Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Common macOS Issues

**Issue: `portaudio` not found**
```bash
brew reinstall portaudio
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"
pip install --force-reinstall sounddevice
```

**Issue: Permission denied for microphone/audio**
- Go to System Preferences → Security & Privacy → Privacy
- Enable microphone/audio access for Terminal

**Issue: M1/M2 Mac compatibility**
```bash
# Use ARM-native Python
arch -arm64 brew install python@3.11

# Install dependencies
arch -arm64 pip install -r requirements.txt
```

---

### Windows

#### 1. Install Python

Download and install Python from [python.org](https://www.python.org/downloads/):
- Choose "Add Python to PATH" during installation
- Verify installation: Open Command Prompt and run `python --version`

#### 2. Install Visual C++ Build Tools (Required)

Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/):
- Select "Desktop development with C++"
- This is required for compiling some dependencies

#### 3. Install Dependencies

```cmd
REM Clone repository
git clone https://github.com/dgaida/text2speech.git
cd text2speech

REM Create virtual environment
python -m venv venv
venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt
```

#### Common Windows Issues

**Issue: `sounddevice` installation fails**
```cmd
REM Install pre-built wheel
pip install --only-binary :all: sounddevice
```

**Issue: No audio output**
- Check Windows Sound Settings
- Ensure default playback device is set
- Update audio drivers

**Issue: `torch` installation is slow**
```cmd
REM Install PyTorch with pip (CPU version)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Issue: DLL load failed errors**
- Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Restart your computer after installation

---

## Python Environment Setup

### Using venv (Recommended)

```bash
# Create environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create environment
conda create -n text2speech python=3.11

# Activate
conda activate text2speech

# Install dependencies
pip install -r requirements.txt
```

### Using pyenv

```bash
# Install specific Python version
pyenv install 3.11.0
pyenv local 3.11.0

# Create virtual environment
python -m venv venv
source venv/bin/activate
```

---

## Dependency Installation

### Core Dependencies

```bash
# Essential packages
pip install torch torchaudio sounddevice pyyaml kokoro
```

### Development Dependencies

```bash
# For development and testing
pip install -r requirements-dev.txt

# Includes: pytest, ruff, black, mypy, bandit, pre-commit
```

### Optional Dependencies

```bash
# For ElevenLabs support (legacy)
pip install elevenlabs

# For enhanced audio processing
pip install librosa scipy

# For development documentation
pip install sphinx sphinx-rtd-theme
```

---

## GPU Support

### CUDA Support (NVIDIA GPUs)

#### Check CUDA Availability

```bash
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"
```

#### Install PyTorch with CUDA

```bash
# For CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA installation
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

### ROCm Support (AMD GPUs)

```bash
# Install PyTorch with ROCm
pip install torch torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2
```

### Apple Silicon (M1/M2)

```bash
# Install PyTorch with MPS support
pip install torch torchaudio

# Verify MPS availability
python -c "import torch; print(torch.backends.mps.is_available())"
```

---

## Verification

### Test Installation

```bash
# Run basic import test
python -c "from text2speech import Text2Speech; print('✓ Installation successful')"

# List available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

# Test Kokoro
python -c "from kokoro import KPipeline; print('✓ Kokoro available')"
```

### Run Test Suite

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=text2speech --cov-report=term
```

### Test Audio Output

```python
# test_audio.py
from text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key", verbose=True)
thread = tts.call_text2speech_async("Testing audio output")
thread.join()
print("✓ Audio test complete")
```

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'text2speech'`

**Solution**:
```bash
# Make sure you're in the project directory and virtual environment is activated
cd text2speech
source venv/bin/activate
pip install -r requirements.txt
```

### Audio Issues

**Problem**: No audio output

**Solutions**:
1. List available devices:
```python
import sounddevice as sd
print(sd.query_devices())
```

2. Set specific device:
```python
import sounddevice as sd
sd.default.device = [None, 5]  # Replace 5 with your device ID
```

3. Test sounddevice directly:
```python
import sounddevice as sd
import numpy as np
sd.play(np.random.randn(24000), samplerate=24000)
sd.wait()
```

### Performance Issues

**Problem**: Slow TTS generation

**Solutions**:
1. Enable GPU support (see GPU Support section)
2. Reduce text length
3. Check system resources: `htop` (Linux/macOS) or Task Manager (Windows)

**Problem**: High memory usage

**Solutions**:
```python
# Enable memory efficient mode
import torch
torch.cuda.empty_cache()  # If using GPU
```

### Dependency Conflicts

**Problem**: Version conflicts between packages

**Solution**:
```bash
# Create fresh environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
```

### Platform-Specific Issues

#### Linux: ALSA Errors

```bash
# Create/edit ~/.asoundrc
pcm.!default {
    type hw
    card 0
}

ctl.!default {
    type hw
    card 0
}
```

#### macOS: SSL Certificate Errors

```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

#### Windows: Long Path Issues

```cmd
REM Enable long paths in registry
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

---

## Getting Help

If you encounter issues not covered here:

1. Check [existing issues](https://github.com/dgaida/text2speech/issues)
2. Review the [FAQ](faq.md)
3. Create a new issue with:
   - Operating system and version
   - Python version
   - Complete error message
   - Steps to reproduce

---

## Next Steps

After successful installation:

- Read the [Configuration Guide](configuration.md)
- Check the [API Reference](api_reference.md)
- Try the examples in `main.py`
- Review the [README](../README.md)

---

**Last Updated**: December 2025  
**Version**: 0.2.0
