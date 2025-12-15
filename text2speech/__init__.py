"""
Text-to-speech module.

Provides audio output capabilities using Kokoro TTS with configurable settings.
"""

from .text2speech import Text2Speech
from .config import Config
from .audio_queue import AudioQueueManager

__version__ = "0.2.0"

__all__ = [
    "Text2Speech",
    "Config",
    "AudioQueueManager",
]
