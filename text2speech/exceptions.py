"""Custom exceptions for text2speech."""

class Text2SpeechError(Exception):
    """Base exception for text2speech errors."""
    pass

class TTSEngineNotAvailable(Text2SpeechError):
    """Raised when no TTS engine is available."""
    pass

class AudioDeviceError(Text2SpeechError):
    """Raised when audio device configuration fails."""
    pass

class InvalidConfigurationError(Text2SpeechError):
    """Raised when configuration is invalid."""
    pass
