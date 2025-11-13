
# API Reference

## `Text2Speech`

The main class for text-to-speech functionality.

### Constructor

```python
Text2Speech(el_api_key: str, verbose: bool = False)
```

**Parameters:**
- `el_api_key` (str): API key for ElevenLabs (no longer used, kept for compatibility)
- `verbose` (bool, optional): If True, prints detailed debug information. Defaults to False.

### Methods

#### `call_text2speech_async(text: str) -> threading.Thread`

Generate speech asynchronously using the Kokoro model.

**Parameters:**
- `text` (str): The text to be spoken

**Returns:**
- `threading.Thread`: The thread handling the asynchronous TTS operation

**Example:**
```python
thread = tts.call_text2speech_async("Hello World")
thread.join()  # Wait for completion
```

#### `verbose() -> bool`

Check whether verbose mode is enabled.

**Returns:**
- `bool`: True if verbose mode is active, otherwise False
