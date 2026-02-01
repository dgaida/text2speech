# Migration Guide

## Upgrading to v0.2.0

### Audio Queue (Breaking Change)

The audio queue is now **enabled by default**. This ensures thread-safe audio playback and prevents device conflicts.

```python
# Old code (still works but may spawn many threads)
tts = Text2Speech(el_api_key="key", enable_queue=False)
tts.call_text2speech_async("text")

# New recommended approach
tts = Text2Speech(el_api_key="key")
tts.speak("text")

# If you need to wait for speech to complete
tts.speak("text", blocking=True)
```

### Deprecated Methods

The following methods are deprecated and will be removed in a future major version:

- `call_text2speech_async(text)` → Use `speak(text, blocking=False)`
- `call_text2speech(text)` → Use `speak(text, blocking=True)`

### New Features

- **Unified Engine Interface**: Both Kokoro and ElevenLabs engines now share a common interface and benefit from the same audio playback safety features (resampling, volume control).
- **Sensitive Data Filtering**: Logs now automatically redact ElevenLabs API keys.
- **Improved Error Handling**: New custom exceptions (`TTSEngineNotAvailable`, `AudioDeviceError`) provide better diagnostic information.
