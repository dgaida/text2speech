# FAQ

Frequently Asked Questions about the text2speech module.

---

## General Questions

### Q: What is text2speech?

**A:** text2speech is a Python module that provides text-to-speech functionality using the Kokoro-82M TTS model. It features a thread-safe audio queue manager to prevent device conflicts and supports asynchronous speech generation.

---

### Q: Why doesn't ElevenLabs work anymore?

**A:** The project has migrated to Kokoro for cost-effectiveness, open-source benefits, and better performance. The Kokoro-82M model delivers comparable quality to much larger models while being Apache 2.0 licensed. ElevenLabs code is retained for backward compatibility but is not actively used unless a valid API key is provided.

---

### Q: What is Kokoro-82M?

**A:** Kokoro is an open-weight TTS model with 82 million parameters that delivers comparable quality to larger models while being significantly faster and more cost-efficient. Despite its compact size, it has achieved top rankings in TTS quality leaderboards and is licensed under Apache 2.0, making it free for both commercial and personal use.

---

## Audio Queue System

### Q: What is the audio queue manager?

**A:** The audio queue manager is a thread-safe system that serializes audio playback to prevent ALSA/PortAudio device conflicts. It manages a priority queue of messages, automatically detects duplicates, and ensures smooth sequential playback.

---

### Q: Should I enable the audio queue?

**A:** Yes, the audio queue is **enabled by default** and recommended for most use cases. It prevents audio device conflicts that can occur when multiple TTS requests happen simultaneously. Only disable it if you're certain your application won't have concurrent audio requests.

**Benefits of the queue:**
- Prevents "device busy" errors
- Priority-based message handling
- Automatic duplicate detection
- Thread-safe operation
- Statistics tracking

---

### Q: How do I disable the queue if needed?

**A:**
```python
tts = Text2Speech(el_api_key="dummy_key", enable_queue=False)
```

---

### Q: What does "messages_skipped_duplicate" mean?

**A:** This statistic shows how many messages were skipped because they were identical to a recently queued message within the duplicate detection window (default: 2 seconds). This prevents repetitive speech when the same message is triggered multiple times quickly.

---

### Q: Can I adjust the queue size?

**A:** Yes, you can customize queue settings:
```python
tts = Text2Speech(
    el_api_key="dummy_key",
    enable_queue=True,
    max_queue_size=100,        # Larger queue
    duplicate_timeout=5.0      # 5 second duplicate window
)
```

---

## Voice and Language Support

### Q: Can I use custom voices?

**A:** Yes, Kokoro supports multiple voice options. You can change voices at runtime:

```python
tts = Text2Speech(el_api_key="dummy_key")
tts.set_voice("am_adam")  # Male voice
tts.set_voice("bf_emma")  # British female voice
```

Available voices include:
- American: `af_heart`, `af_nicole`, `am_adam`, `am_michael`
- British: `bf_emma`, `bf_isabella`, `bm_lewis`, `bm_george`

See the [Configuration Guide](configuration.md) for details.

---

### Q: What languages are supported?

**A:** The current implementation primarily supports:
- American English (`lang_code: "a"`)
- British English (`lang_code: "b"`)

Additional language support is available with Kokoro including Japanese and Mandarin Chinese, but requires additional dependencies:
- Japanese: `pip install misaki[ja]`
- Mandarin: `pip install misaki[zh]`

---

### Q: How do I change the voice speed?

**A:**
```python
tts = Text2Speech(el_api_key="dummy_key")
tts.set_speed(0.8)  # Slower (80% of normal)
tts.set_speed(1.2)  # Faster (120% of normal)
```

Speed range is 0.5 to 2.0, with 1.0 being normal speed.

---

## Performance Questions

### Q: Is GPU acceleration supported?

**A:** Yes, if PyTorch is configured with CUDA support, the Kokoro model will automatically use GPU acceleration. You can enable/disable GPU in the configuration:

```yaml
performance:
  use_gpu: true
```

Or check if GPU is being used:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

---

### Q: How fast is Kokoro compared to other TTS models?

**A:** Kokoro generates speech up to 210× real-time on GPU and 3-11× real-time on CPU—making it perfect for real-time applications and batch processing. Its 82 million parameters make it significantly faster than larger models while maintaining comparable quality.

---

### Q: Can I run this without a GPU?

**A:** Yes, Kokoro runs well on CPU. While GPU acceleration provides better performance, CPU execution is still quite fast (3-11× real-time) for most use cases.

---

## Usage Questions

### Q: How do I handle long texts?

**A:** The system automatically splits long texts at newlines. For very long texts, consider splitting them manually into smaller chunks:

```python
tts = Text2Speech(el_api_key="dummy_key")

long_text = "..." # Your long text
paragraphs = long_text.split('\n\n')

for paragraph in paragraphs:
    tts.speak(paragraph)

tts.shutdown()
```

---

### Q: How do I wait for speech to complete?

**A:** Use blocking mode:
```python
tts = Text2Speech(el_api_key="dummy_key")
tts.speak("Please wait for me", blocking=True)
print("Speech finished!")
```

Or with the legacy API:
```python
thread = tts.call_text2speech_async("Text")
thread.join()  # Wait for completion
```

---

### Q: Can I use this in production?

**A:** Yes, but ensure you test thoroughly with your specific hardware and use case. The module includes:
- Robust error handling for production use
- Comprehensive logging system
- Thread-safe audio queue
- Configurable settings via YAML

Best practices for production:
- Enable the audio queue
- Configure appropriate logging
- Set reasonable queue sizes
- Monitor queue statistics
- Test on target hardware

---

### Q: How do I integrate this with my application?

**A:** Basic integration:

```python
from text2speech import Text2Speech

class MyApplication:
    def __init__(self):
        self.tts = Text2Speech(
            el_api_key="dummy_key",
            config_path="my_app_config.yaml"
        )

    def announce(self, message, urgent=False):
        priority = 10 if urgent else 0
        self.tts.speak(message, priority=priority)

    def shutdown(self):
        self.tts.shutdown()

# Usage
app = MyApplication()
app.announce("Application started")
app.announce("Critical error!", urgent=True)
app.shutdown()
```

---

## Configuration Questions

### Q: Where should I put my config file?

**A:** The module searches for config files in this order:
1. `./config.yaml` (current directory)
2. `~/.text2speech/config.yaml` (user home)
3. `~/.config/text2speech/config.yaml` (XDG config)
4. `/etc/text2speech/config.yaml` (system-wide, Linux)

Or specify explicitly:
```python
tts = Text2Speech(config_path="/path/to/my/config.yaml")
```

---

### Q: Can I change settings at runtime?

**A:** Yes, many settings can be changed at runtime:

```python
tts = Text2Speech(el_api_key="dummy_key")

# Change voice
tts.set_voice("am_michael")

# Change speed
tts.set_speed(1.2)

# Change volume
tts.set_volume(0.7)
```

Configuration file settings provide defaults, but runtime changes take precedence.

---

### Q: How do I select a specific audio output device?

**A:** First, list available devices:
```python
import sounddevice as sd
devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"{i}: {device['name']}")
```

Then configure the device:
```yaml
audio:
  output_device: 3  # Replace with your device ID
```

Or programmatically:
```python
config = Config()
config.set("audio.output_device", 3)
tts = Text2Speech(el_api_key="dummy_key", config=config)
```

---

## Troubleshooting

### Q: I'm getting "device busy" errors. What should I do?

**A:** This typically happens when multiple audio requests conflict. Enable the audio queue (it's enabled by default):

```python
tts = Text2Speech(el_api_key="dummy_key", enable_queue=True)
```

The queue serializes audio playback to prevent conflicts.

---

### Q: No audio is playing. How do I debug this?

**A:** Follow these steps:

1. **Check if sounddevice is working:**
```python
import sounddevice as sd
import numpy as np
sd.play(np.random.randn(24000), samplerate=24000)
sd.wait()
```

2. **List available devices:**
```python
import sounddevice as sd
print(sd.query_devices())
```

3. **Enable verbose mode:**
```python
tts = Text2Speech(el_api_key="dummy_key", verbose=True)
```

4. **Check queue statistics:**
```python
stats = tts.get_queue_stats()
print(stats)
```

---

### Q: How do I report a bug?

**A:** Please report bugs on GitHub:
1. Check [existing issues](https://github.com/dgaida/text2speech/issues)
2. Create a new issue with:
   - Operating system and version
   - Python version
   - Complete error message
   - Minimal code to reproduce
   - Queue statistics (if relevant)

---

## Advanced Questions

### Q: Can I run multiple TTS instances simultaneously?

**A:** Yes, each instance manages its own queue:

```python
robot_tts = Text2Speech(el_api_key="dummy_key")
robot_tts.set_voice("am_adam")

narrator_tts = Text2Speech(el_api_key="dummy_key")
narrator_tts.set_voice("bm_lewis")

robot_tts.speak("Robot speaking")
narrator_tts.speak("Narrator speaking")

robot_tts.shutdown()
narrator_tts.shutdown()
```

However, be aware that both instances may use the same audio device, which could cause conflicts if queues are disabled.

---

### Q: How do I implement priority-based messaging?

**A:**
```python
tts = Text2Speech(el_api_key="dummy_key")

# Normal messages
tts.speak("Loading data...", priority=0)
tts.speak("Processing...", priority=0)

# Urgent message (plays first)
tts.speak("Error detected!", priority=10)

# Lower priority background info
tts.speak("Background task complete", priority=1)

tts.shutdown()
```

Messages with higher priority values are played before lower priority messages.

---

### Q: Can I get notifications when speech completes?

**A:** Use blocking mode or thread.join():

```python
# Blocking mode
tts.speak("Please wait", blocking=True)
print("Speech complete!")

# Or with legacy API
thread = tts.call_text2speech_async("Text")
thread.join()
print("Speech complete!")
```

For more complex scenarios, consider implementing a callback system around the queue manager.

---

### Q: How do I implement voice cloning?

**A:** Voice cloning is not currently supported in Kokoro-82M. The available voices are pre-trained and optimized for quality. Future versions may support custom voice training.

---

### Q: Can I use this for real-time streaming?

**A:** The current implementation generates complete utterances before playback. Real-time streaming TTS is on the roadmap but not yet implemented.

---

## Integration Questions

### Q: Can I use this with a web framework like Flask or FastAPI?

**A:** Yes, but be careful with the audio queue in multi-worker setups:

```python
from flask import Flask
from text2speech import Text2Speech

app = Flask(__name__)
tts = Text2Speech(el_api_key="dummy_key", enable_queue=True)

@app.route('/speak/<text>')
def speak(text):
    tts.speak(text)
    return {"status": "queued"}

@app.route('/stats')
def stats():
    return tts.get_queue_stats()
```

For production, consider running TTS in a separate service.

---

### Q: How do I use this with ROS (Robot Operating System)?

**A:** Create a ROS node wrapper:

```python
import rospy
from std_msgs.msg import String
from text2speech import Text2Speech

class TTSNode:
    def __init__(self):
        self.tts = Text2Speech(el_api_key="dummy_key")
        rospy.Subscriber("/speech/say", String, self.callback)

    def callback(self, msg):
        self.tts.speak(msg.data)

    def shutdown(self):
        self.tts.shutdown()

if __name__ == '__main__':
    rospy.init_node('tts_node')
    node = TTSNode()
    rospy.on_shutdown(node.shutdown)
    rospy.spin()
```

---

## Licensing and Legal

### Q: Is this free to use commercially?

**A:** Yes, the text2speech module is MIT licensed, and Kokoro-82M is Apache 2.0 licensed. Both allow commercial use without restrictions.

---

### Q: Do I need to credit Kokoro or text2speech?

**A:** While not required, attribution is appreciated. See the [LICENSE](../LICENSE) file for details.

---

## Getting More Help

### Q: Where can I find more examples?

**A:** Check these resources:
- `main.py` - Example applications
- `examples/` directory - Additional examples
- [API Reference](api_reference.md) - Complete API documentation
- [Configuration Guide](configuration.md) - Detailed configuration options

---

### Q: How do I contribute to the project?

**A:** See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Setting up development environment
- Running tests
- Submitting pull requests
- Code quality standards

---

### Q: Is there a Discord or community forum?

**A:** Currently, the best place for discussions is the [GitHub Issues](https://github.com/dgaida/text2speech/issues) page. For general questions, open a discussion issue.

---

**Last Updated**: December 2025  
**Version**: 0.2.0
