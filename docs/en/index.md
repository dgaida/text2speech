# text2speech Documentation

Welcome to the text2speech module documentation. This module provides text-to-speech (TTS) functionality using the Kokoro-82M model with advanced, thread-safe audio queue management.

---

## Overview

The **text2speech** module is designed to provide robust and easy-to-use speech synthesis for robotics applications and other Python projects.

### Key Features

- ✅ **Thread-safe audio queue** - Prevents ALSA/PortAudio conflicts via serialized playback.  
- ✅ **High-quality synthesis** - Uses the Kokoro-82M model for natural-sounding voices.  
- ✅ **Priority-based control** - Urgent messages interrupt normal messages.  
- ✅ **Duplicate detection** - Avoids repetition of identical messages within short intervals.  
- ✅ **Flexible configuration system** - YAML-based settings for audio, voices, and performance.  
- ✅ **Multilingual** - Support for various accents and languages.  

---

## Quick Access

| Section | Description |
|---------|-------------|
| [🚀 Getting Started](getting-started.md) | Quick introduction to usage |
| [📦 Installation](installation.md) | System requirements and setup |
| [⚙️ Configuration](configuration.md) | Customizing the library |
| [📚 API Reference](api/core.md) | Detailed technical documentation |
| [🏗️ Architecture](architecture/index.md) | Insights into internal workings |

---

## Metrics & Status

[![Interrogate](assets/interrogate.svg)](metrics.md)
[![Tests](https://github.com/dgaida/text2speech/actions/workflows/tests.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/tests.yml)

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/dgaida/text2speech/blob/master/LICENSE) file for more details.
