# Konfiguration

`text2speech` bietet ein flexibles Konfigurationssystem, das auf YAML-Dateien basiert.

## Konfigurationsdatei laden

Standardmäßig sucht die Bibliothek an folgenden Orten nach einer `config.yaml`:
1. Aktuelles Verzeichnis
2. `~/.text2speech/config.yaml`
3. `~/.config/text2speech/config.yaml`
4. `/etc/text2speech/config.yaml`

Sie können auch explizit einen Pfad angeben:

```python
from text2speech import Text2Speech
tts = Text2Speech(config_path="pfad/zu/meiner_config.yaml")
```

## Beispiel einer `config.yaml`

Hier ist eine vollständige Beispielkonfiguration mit allen wichtigen Optionen:

```yaml
audio:
  output_device: null  # null verwendet das Standardgerät
  default_volume: 0.8  # Lautstärke von 0.0 bis 1.0
  sample_rate: 24000   # Abtastrate (Standard für Kokoro)

tts:
  engine: "kokoro"     # "kokoro" oder "elevenlabs"
  kokoro:
    lang_code: "a"     # 'a' für Amerikanisch, 'b' für Britisch
    voice: "af_heart"  # Standardstimme
    speed: 1.0         # Sprechgeschwindigkeit

logging:
  verbose: false       # Ausführliche Debug-Ausgaben
  log_level: "INFO"    # INFO, DEBUG, WARNING, ERROR

performance:
  use_gpu: true        # CUDA verwenden, falls verfügbar
```

## Audio-Einstellungen

### Ausgabegeräte finden
Um die verfügbaren Geräte und deren IDs zu sehen, können Sie die API nutzen:

```python
from text2speech import Text2Speech
tts = Text2Speech()
devices = tts.get_available_devices()
for d in devices:
    print(f"ID: {d['index']}, Name: {d['name']}")
```

Tragen Sie die gewünschte ID in die `config.yaml` unter `audio.output_device` ein.

## TTS-Einstellungen

### Verfügbare Stimmen (Kokoro)

**Amerikanisches Englisch (`lang_code: "a"`):**
- `af_heart` - Weiblich, warm (Standard)
- `af_nicole` - Weiblich, professionell
- `am_adam` - Männlich, tief
- `am_michael` - Männlich, freundlich

**Britisches Englisch (`lang_code: "b"`):**
- `bf_emma` - Weiblich, elegant
- `bm_lewis` - Männlich, kultiviert

## Konfigurations-Priorität

Die Einstellungen werden in folgender Rangfolge angewendet (höchste Priorität zuerst):
1. Konstruktor-Argumente (z.B. `Text2Speech(verbose=True)`)
2. Explizite Methodenaufrufe (z.B. `tts.set_voice("am_adam")`)
3. Werte aus der geladenen YAML-Datei
4. Interne Standardwerte
