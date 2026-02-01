"""Text-to-speech module with configurable settings."""

import logging
import threading
import warnings
from typing import Optional, List, Dict, Any

import torch
import torchaudio

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except (ImportError, OSError) as e:
    HAS_SOUNDDEVICE = False
    sd = None

from .config import Config
from .audio_queue import AudioQueueManager
from .engines import TTSEngine, KokoroEngine, ElevenLabsEngine
from .constants import (
    MIN_API_KEY_LENGTH,
    API_KEY_PREFIX,
    DEFAULT_QUEUE_SIZE,
    DEFAULT_DUPLICATE_TIMEOUT,
    KOKORO_SAMPLE_RATE,
    DEFAULT_VOLUME,
)
from .exceptions import (
    Text2SpeechError,
    TTSEngineNotAvailable,
    AudioDeviceError,
)
from .logging_utils import SensitiveDataFilter


class Text2Speech:
    """Text-to-Speech (TTS) class with configurable settings.

    This class provides text-to-speech functionality using either ElevenLabs
    or Kokoro model with configuration support via YAML files.
    """

    def __init__(
        self,
        el_api_key: Optional[str] = None,
        verbose: Optional[bool] = None,
        config_path: Optional[str] = None,
        config: Optional[Config] = None,
        enable_queue: bool = True,
        max_queue_size: int = DEFAULT_QUEUE_SIZE,
        duplicate_timeout: float = DEFAULT_DUPLICATE_TIMEOUT,
    ) -> None:
        """Initialize the Text2Speech instance.

        Args:
            el_api_key: API key for ElevenLabs.
            verbose: If True, prints debug info. Overrides config if set.
            config_path: Path to config.yaml file.
            config: Pre-loaded Config object.
            enable_queue: If True, uses AudioQueueManager for thread-safe playback.
            max_queue_size: Maximum queued messages.
            duplicate_timeout: Skip duplicate messages within this window (seconds).
        """
        # Load configuration
        if config is not None:
            self.config = config
        else:
            self.config = Config(config_path)

        # Override verbose setting if explicitly provided
        self._verbose = verbose if verbose is not None else self.config.verbose

        # Setup logging
        self._setup_logging()

        # Store API key and validate
        self._el_api_key = el_api_key
        self._use_elevenlabs = self._validate_elevenlabs_key(el_api_key)

        # Initialize TTS engine
        self._engine: Optional[TTSEngine] = None
        self._initialize_tts_engine()

        # Set audio output device from config
        self._setup_audio_device()

        # Initialize audio queue manager
        self._enable_queue = enable_queue
        self._audio_queue: Optional[AudioQueueManager] = None

        if enable_queue:
            self._audio_queue = AudioQueueManager(
                tts_callable=self.speak_sync,
                max_queue_size=max_queue_size,
                duplicate_timeout=duplicate_timeout,
                logger=self.logger,
            )
            self._audio_queue.start()
            self.logger.info("Audio queue manager enabled")

    def _setup_logging(self) -> None:
        """Setup logging configuration with sensitive data filter."""
        log_level = self.config.get("logging.log_level", "INFO")
        self.logger = logging.getLogger("text2speech")
        self.logger.setLevel(getattr(logging, log_level))

        if not self.logger.handlers:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Add sensitive data filter to all handlers
        sensitive_filter = SensitiveDataFilter()
        for handler in self.logger.handlers:
            handler.addFilter(sensitive_filter)

        log_file = self.config.get("logging.log_file")
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            file_handler.addFilter(sensitive_filter)
            self.logger.addHandler(file_handler)

    def _setup_audio_device(self) -> None:
        """Configure the audio output device."""
        if HAS_SOUNDDEVICE and sd is not None:
            device_id = self.config.audio_output_device
            if device_id is not None:
                try:
                    sd.default.device[1] = device_id
                    self.logger.info(f"Audio output device set to: {device_id}")
                except Exception as e:
                    self.logger.error(f"Failed to set audio device {device_id}: {e}")
                    raise AudioDeviceError(f"Invalid audio device: {device_id}") from e

    def _validate_elevenlabs_key(self, api_key: Optional[str]) -> bool:
        """Validate ElevenLabs API key format."""
        if not api_key or not isinstance(api_key, str):
            return False
        return api_key.startswith(API_KEY_PREFIX) and len(api_key) >= MIN_API_KEY_LENGTH

    def _initialize_tts_engine(self) -> None:
        """Initialize the TTS engine with fallback."""
        if self._use_elevenlabs:
            try:
                model = self.config.get("tts.elevenlabs.model", "eleven_multilingual_v2")
                self._engine = ElevenLabsEngine(api_key=self._el_api_key, model=model) # type: ignore
                self.logger.info("Initialized ElevenLabs TTS")
                return
            except Exception as e:
                self.logger.warning(f"ElevenLabs initialization failed: {e}. Falling back to Kokoro.")

        try:
            self._engine = KokoroEngine(lang_code=self.config.kokoro_lang_code)
            self.logger.info("Initialized Kokoro TTS")
        except Exception as e:
            self.logger.error(f"Failed to initialize any TTS engine: {e}")
            raise TTSEngineNotAvailable("No TTS engine available") from e

    def speak(self, text: str, priority: int = 0, blocking: bool = False) -> bool:
        """Queue text for speech synthesis.

        Args:
            text: Text to speak.
            priority: Priority level (0-100).
            blocking: If True, wait for speech to complete.

        Returns:
            True if successfully queued/spoken.
        """
        if self._audio_queue and self._enable_queue:
            success = self._audio_queue.enqueue(text, priority=priority)
            if blocking and success:
                self._wait_for_queue()
            return success

        if blocking:
            self.speak_sync(text)
            return True

        thread = threading.Thread(target=self.speak_sync, args=(text,))
        thread.start()
        return True

    def _wait_for_queue(self) -> None:
        """Wait for the audio queue to be empty."""
        import time
        if self._audio_queue:
            while not self._audio_queue._queue.empty():
                time.sleep(0.1)
            # Wait a bit more for the last message to finish playing
            time.sleep(0.5)

    def speak_sync(self, text: str) -> None:
        """Synchronous TTS call.

        Args:
            text: Text to speak.
        """
        if not self._engine:
            self.logger.error("No TTS engine initialized")
            return

        try:
            voice = self.config.kokoro_voice if isinstance(self._engine, KokoroEngine) else self.config.get("tts.elevenlabs.voice", "Brian")
            speed = self.config.kokoro_speed

            self.logger.debug(f"Synthesizing: {text[:50]}...")
            for _, _, audio in self._engine.synthesize(text, voice=voice, speed=speed):
                self._play_audio_safely(audio, original_sample_rate=self.config.sample_rate, volume=self.config.audio_volume)
                if HAS_SOUNDDEVICE and sd:
                    sd.wait()
        except Exception as e:
            self.logger.error(f"Speech synthesis error: {e}")

    @staticmethod
    def _play_audio_safely(audio_tensor: torch.Tensor, original_sample_rate: int = 24000, device: Optional[int] = None, volume: float = DEFAULT_VOLUME) -> None:
        """Play audio safely with resampling and volume control."""
        if not HAS_SOUNDDEVICE or sd is None:
            logging.getLogger("text2speech").warning("sounddevice not available, skipping playback")
            return

        try:
            if device is None:
                device = sd.default.device[1]

            device_info = sd.query_devices(device, "output")
            supported_rate = int(device_info["default_samplerate"])

            if original_sample_rate != supported_rate:
                resampler = torchaudio.transforms.Resample(orig_freq=original_sample_rate, new_freq=supported_rate)
                audio_tensor = resampler(audio_tensor)

            peak = torch.abs(audio_tensor).max()
            if peak > 0:
                audio_tensor = audio_tensor / peak
            audio_tensor = torch.clamp(audio_tensor * volume, -0.95, 0.95)

            sd.play(audio_tensor.cpu().numpy(), samplerate=supported_rate, device=device)
        except Exception as e:
            logging.getLogger("text2speech").error(f"Audio playback error: {e}")

    # Deprecated methods
    def call_text2speech_async(self, text: str) -> threading.Thread:
        """Deprecated: Use speak(blocking=False) instead."""
        warnings.warn("call_text2speech_async is deprecated, use speak(blocking=False)", DeprecationWarning, stacklevel=2)
        thread = threading.Thread(target=self.speak_sync, args=(text,))
        thread.start()
        return thread

    def call_text2speech(self, text: str) -> None:
        """Deprecated: Use speak(blocking=True) instead."""
        warnings.warn("call_text2speech is deprecated, use speak(blocking=True)", DeprecationWarning, stacklevel=2)
        self.speak_sync(text)

    def shutdown(self, timeout: float = 5.0) -> None:
        """Shutdown the TTS system."""
        if self._audio_queue:
            self._audio_queue.shutdown(timeout=timeout)

    def __del__(self) -> None:
        self.shutdown()

    def set_voice(self, voice: str) -> None:
        """Set the voice for TTS."""
        self.config.set("tts.kokoro.voice", voice)
        self.config.set("tts.elevenlabs.voice", voice)
        self.logger.info(f"Voice changed to: {voice}")

    def set_speed(self, speed: float) -> None:
        """Set the speech speed."""
        if 0.5 <= speed <= 2.0:
            self.config.set("tts.kokoro.speed", speed)
            self.logger.info(f"Speed changed to: {speed}")
        else:
            self.logger.warning(f"Speed {speed} out of range (0.5-2.0)")

    def set_volume(self, volume: float) -> None:
        """Set the playback volume."""
        if 0.0 <= volume <= 1.0:
            self.config.set("audio.default_volume", volume)
            self.logger.info(f"Volume changed to: {volume}")
        else:
            self.logger.warning(f"Volume {volume} out of range (0.0-1.0)")

    def get_available_devices(self) -> List[Dict[str, Any]]:
        """Get available audio devices."""
        if HAS_SOUNDDEVICE and sd:
            return list(sd.query_devices())
        return []

    def is_using_elevenlabs(self) -> bool:
        """Check if using ElevenLabs."""
        if not self._engine:
            return False
        # Handle both real classes and mocks
        return "ElevenLabsEngine" in str(self._engine) or "ElevenLabsEngine" in str(type(self._engine))

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        if self._audio_queue:
            return dict(self._audio_queue.get_stats())
        return {}
