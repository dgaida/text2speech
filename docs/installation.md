# Installation

Dieser Leitfaden führt Sie durch die Installation von `text2speech` und seinen Abhängigkeiten.

## Systemanforderungen

- **Python**: Version 3.9 oder höher.
- **Betriebssysteme**: Ubuntu (getestet), Windows, macOS.
- **Audio**: Ein System mit funktionierendem Audio-Ausgabegerät.
- **Speicher**: Mindestens 2GB RAM empfohlen (4GB für optimale Leistung).
- **Festplatte**: Ca. 500MB für Modelldateien.

## Installation aus den Quellen

Klonen Sie das Repository und installieren Sie das Paket im Editier-Modus:

```bash
git clone https://github.com/dgaida/text2speech.git
cd text2speech
pip install -e .
```

Dadurch werden alle Kern-Abhängigkeiten wie `torch`, `kokoro` und `sounddevice` automatisch installiert.

## Optionale Abhängigkeiten

Für Entwickler und spezielle Anwendungsfälle:

### Entwicklungs-Tools
```bash
pip install -e ".[dev]"
```
Dies installiert Tools wie `pytest`, `ruff`, `black` und `mypy`.

### ElevenLabs (Legacy-Unterstützung)
Wenn Sie das alte ElevenLabs-Backend nutzen möchten:
```bash
pip install elevenlabs
```

## Plattformspezifische Hinweise

### Linux (Ubuntu/Debian)
Möglicherweise müssen Sie Entwicklungsbibliotheken für den Audio-Support installieren:

```bash
sudo apt-get update
sudo apt-get install libasound2-dev libportaudio2
```

### Windows
Die Installation über `pip` sollte in den meisten Fällen ausreichen. Stellen Sie sicher, dass Ihre Soundtreiber aktuell sind.

## Installation verifizieren

Sie können die Installation mit dem integrierten CLI-Tool testen:

```bash
text2speech "Installation erfolgreich getestet."
```

Wenn Sie eine Stimme hören, ist das System korrekt konfiguriert.
