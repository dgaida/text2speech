# text2speech

The **text2speech** module provides **text-to-speech (TTS)** functionality for robotics and other applications. It supports asynchronous text-to-speech generation and robust, safe audio playback.

Although initially designed to use **ElevenLabs**, this implementation now relies on the **Kokoro** model for speech synthesis.

---

## Badges

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://github.com/dgaida/text2speech/actions/workflows/lint.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/lint.yml)
[![CodeQL](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Features

- ✅ Asynchronous text-to-speech synthesis
- ✅ Uses **Kokoro** for natural-sounding voices
- ✅ Automatic resampling and volume normalization for playback
- ✅ Safe, thread-based audio playback
- ⚙️ Legacy ElevenLabs integration retained for backward compatibility (disabled by default)

---

## Installation

Ensure dependencies are installed:

```bash
pip install kokoro torch torchaudio sounddevice
```

If you want optional support for ElevenLabs (legacy mode):

```bash
pip install elevenlabs
```

---

## Usage Example

```python
from robot_environment.text2speech import Text2Speech

tts = Text2Speech(el_api_key="dummy_key", verbose=True)
thread = tts.call_text2speech_async("Hello, this is your robot speaking!")
thread.join()  # Wait for speech playback to complete
```

---

## Class Overview

### `Text2Speech`

**Methods:**
- `__init__(el_api_key: str, verbose: bool = False)` – Initialize the TTS system.
- `call_text2speech_async(text: str)` – Generate speech asynchronously.
- `_text2speech(mytext: str)` – (Legacy) ElevenLabs-based TTS.
- `_text2speech_kokoro(mytext: str)` – Kokoro-based TTS synthesis.
- `_play_audio_safely(audio_tensor: torch.Tensor, ...)` – Safely play audio with automatic resampling.
- `verbose() -> bool` – Returns whether verbose mode is active.

---

## Notes

- The ElevenLabs API client is no longer actively used, but the code remains for reference.
- Default voice and speed can be adjusted in `_text2speech_kokoro()`.
- This module assumes **sounddevice** has access to a valid audio output device.

---

## License


