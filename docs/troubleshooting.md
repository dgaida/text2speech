# Troubleshooting

## No Audio Output

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

## ALSA/PortAudio Errors

If you see "device busy" errors:

```python
# Use the queue system (enabled by default)
tts = Text2Speech(el_api_key="dummy_key", enable_queue=True)
```

The queue manager serializes audio playback to prevent conflicts.

## Import Errors

If you encounter import errors:

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Verify installation
python -c "import kokoro; import torch; import sounddevice"
```

## Performance Issues

For slow performance:

1. Ensure PyTorch is using GPU acceleration (if available)
2. Enable GPU in config:
```yaml
performance:
  use_gpu: true
```
