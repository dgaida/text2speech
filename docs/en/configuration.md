# Configuration

`text2speech` offers a flexible configuration system based on YAML files.

## Loading a Configuration File

By default, the library searches for a `config.yaml` in the following locations:
1. Current directory
2. `~/.text2speech/config.yaml`
3. `~/.config/text2speech/config.yaml`
4. `/etc/text2speech/config.yaml`

You can also explicitly provide a path:

```python
from text2speech import Text2Speech
tts = Text2Speech(config_path="path/to/my_config.yaml")
```

## Example `config.yaml`

Here is a complete example configuration with all major options:

```yaml
audio:
  output_device: null  # null uses the default device
  default_volume: 0.8  # Volume from 0.0 to 1.0
  sample_rate: 24000   # Sample rate (default for Kokoro)

tts:
  engine: "kokoro"     # "kokoro" or "elevenlabs"
  kokoro:
    lang_code: "a"     # 'a' for American, 'b' for British
    voice: "af_heart"  # Default voice
    speed: 1.0         # Speech speed

logging:
  verbose: false       # Detailed debug output
  log_level: "INFO"    # INFO, DEBUG, WARNING, ERROR

performance:
  use_gpu: true        # Use CUDA if available
```

## Audio Settings

### Finding Output Devices
To see available devices and their IDs, you can use the API:

```python
from text2speech import Text2Speech
tts = Text2Speech()
devices = tts.get_available_devices()
for d in devices:
    print(f"ID: {d['index']}, Name: {d['name']}")
```

Enter the desired ID into the `config.yaml` under `audio.output_device`.

## TTS Settings

### Available Voices (Kokoro)

**American English (`lang_code: "a"`):**
- `af_heart` - Female, warm (default)
- `af_nicole` - Female, professional
- `am_adam` - Male, deep
- `am_michael` - Male, friendly

**British English (`lang_code: "b"`):**
- `bf_emma` - Female, elegant
- `bm_lewis` - Male, refined

## Configuration Priority

Settings are applied in the following order of precedence (highest priority first):
1. Constructor arguments (e.g., `Text2Speech(verbose=True)`)
2. Explicit method calls (e.g., `tts.set_voice("am_adam")`)
3. Values from the loaded YAML file
4. Internal defaults
