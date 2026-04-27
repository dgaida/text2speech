# text2speech

[![Lint](https://github.com/dgaida/text2speech/actions/workflows/lint.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/lint.yml)
[![Tests](https://github.com/dgaida/text2speech/actions/workflows/tests.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/tests.yml)
[![CodeQL](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/codeql.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Version](https://img.shields.io/badge/version-0.2.1-blue)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://dgaida.github.io/text2speech/)

Professionelle Text-to-Speech-Bibliothek mit Unterstützung für Kokoro und ElevenLabs.

## Übersicht

**text2speech** bietet eine robuste und einfach zu bedienende Sprachsynthese für Python-Projekte. Es zeichnet sich durch ein thread-sicheres Audio-Queue-Management aus, das Hardware-Konflikte verhindert.

### Hauptmerkmale

- ✅ **Thread-sichere Audio-Queue** - Verhindert ALSA/PortAudio-Konflikte.
- ✅ **Hochwertige Synthese** - Verwendet Kokoro-82M (lokal) oder ElevenLabs (Cloud).
- ✅ **Prioritätsbasierte Steuerung** - Dringende Nachrichten werden bevorzugt behandelt.
- ✅ **Konfigurationssystem** - Einfache Anpassung über YAML.
- ✅ **Kommandozeilenschnittstelle** - Direkte Nutzung über das Terminal.

## Schnellstart

```python
from text2speech import Text2Speech

with Text2Speech() as tts:
    tts.speak("Hallo, Welt!")
```

## Dokumentation

Die vollständige Dokumentation finden Sie auf [GitHub Pages](https://dgaida.github.io/text2speech/).

- [Installation](https://dgaida.github.io/text2speech/latest/installation/)
- [Erste Schritte](https://dgaida.github.io/text2speech/latest/getting-started/)
- [Konfiguration](https://dgaida.github.io/text2speech/latest/configuration/)
- [API-Referenz](https://dgaida.github.io/text2speech/latest/api/core/)

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.
