"""Text-to-speech module with configurable settings."""

from typing import Optional
import logging

try:
    from elevenlabs import play
    from elevenlabs.client import ElevenLabs

    HAS_ELEVENLABS = True
except ImportError as e:
    print("Warning: elevenlabs not available:", e)
    HAS_ELEVENLABS = False
    ElevenLabs = None

try:
    from kokoro import KPipeline

    HAS_KOKORO = True
except ImportError as e:
    print(f"Warning: kokoro not available ({e}). TTS will not work.")
    HAS_KOKORO = False
    KPipeline = None

import torchaudio
import torch

try:
    import sounddevice as sd

    HAS_SOUNDDEVICE = True
except (ImportError, OSError) as e:
    print(f"Warning: sounddevice not available ({e}). Audio playback will not work.")
    HAS_SOUNDDEVICE = False
    sd = None

import threading

from .config import Config
from .audio_queue import AudioQueueManager


class Text2Speech:
    """Text-to-Speech (TTS) class with configurable settings.

    This class provides text-to-speech functionality using either ElevenLabs
    (when a valid API key is provided) or Kokoro model (as fallback) with
    configuration support via YAML files. Supports asynchronous speech synthesis
    and safe audio playback with dynamic resampling.

    Features thread-safe audio playback via AudioQueueManager to prevent
    ALSA/PortAudio device conflicts.
    """

    def __init__(
        self,
        el_api_key: Optional[str] = None,
        verbose: Optional[bool] = None,
        config_path: Optional[str] = None,
        config: Optional[Config] = None,
        enable_queue: bool = True,  # NEW: Enable audio queue by default
        max_queue_size: int = 50,
        duplicate_timeout: float = 2.0,
    ) -> None:
        """Initialize the Text2Speech instance.

        Args:
            el_api_key (str, optional): API key for ElevenLabs. If valid, ElevenLabs will be used.
            verbose (bool, optional): If True, prints debug info. Overrides config if set.
            config_path (str, optional): Path to config.yaml file.
            config (Config, optional): Pre-loaded Config object. Takes precedence over config_path.
            enable_queue: If True, uses AudioQueueManager for thread-safe playback.
            max_queue_size: Maximum queued messages (only if enable_queue=True).
            duplicate_timeout: Skip duplicate messages within this window (seconds).
        """
        # Load configuration
        if config is not None:
            self.config = config
        else:
            self.config = Config(config_path)

        # Override verbose setting if explicitly provided
        if verbose is not None:
            self._verbose = verbose
        else:
            self._verbose = self.config.verbose

        # Setup logging
        self._setup_logging()

        # Store API key and validate
        self._el_api_key = el_api_key
        self._use_elevenlabs = self._validate_elevenlabs_key(el_api_key)

        # Initialize TTS client
        self._client = None
        self._el_client = None
        self._initialize_tts_engine()

        # Set audio output device from config
        if HAS_SOUNDDEVICE and sd is not None:
            device_id = self.config.audio_output_device
            if device_id is not None:
                try:
                    sd.default.device[1] = device_id
                    self.logger.info(f"Audio output device set to: {device_id}")
                except Exception as e:
                    self.logger.error(f"Failed to set audio device {device_id}: {e}")

        # ✅ NEW: Initialize audio queue manager
        self._enable_queue = enable_queue
        self._audio_queue = None

        if enable_queue:
            self._audio_queue = AudioQueueManager(
                tts_callable=self._text2speech_sync,  # Synchronous TTS function
                max_queue_size=max_queue_size,
                duplicate_timeout=duplicate_timeout,
                logger=self.logger,
            )
            self._audio_queue.start()
            self.logger.info("Audio queue manager enabled")
        else:
            self.logger.info("Audio queue manager disabled (using legacy threading)")

    def __del__(self):
        """Cleanup on deletion."""
        self.shutdown()

    def shutdown(self, timeout: float = 5.0):
        """
        Shutdown the TTS system cleanly.

        Args:
            timeout: Maximum seconds to wait for queue to empty
        """
        if self._audio_queue is not None:
            self._audio_queue.shutdown(timeout=timeout)

    def _validate_elevenlabs_key(self, api_key: Optional[str]) -> bool:
        """Validate ElevenLabs API key format.

        Args:
            api_key (str, optional): The API key to validate.

        Returns:
            bool: True if the key appears valid, False otherwise.
        """
        if api_key is None:
            return False

        if not isinstance(api_key, str):
            return False

        # ElevenLabs API keys typically start with "sk_" and have a minimum length
        # They're usually around 32-64 characters long
        if api_key.startswith("sk_") and len(api_key) >= 10:
            return True

        # Some legacy keys might not start with sk_ but are still valid
        # If it's a reasonably long string, we'll try to use it
        if len(api_key) >= 32:
            self.logger.warning("API key format unusual but will attempt to use it")
            return True

        return False

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = self.config.get("logging.log_level", "INFO")

        # Create logger
        self.logger = logging.getLogger("text2speech")
        self.logger.setLevel(getattr(logging, log_level))

        # Console handler
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, log_level))
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # File handler if specified
            log_file = self.config.get("logging.log_file")
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(getattr(logging, log_level))
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

    def _initialize_tts_engine(self) -> None:
        """Initialize the TTS engine based on configuration and API key."""

        # If valid ElevenLabs API key provided, use ElevenLabs
        if self._use_elevenlabs and HAS_ELEVENLABS:
            try:
                self._el_client = ElevenLabs(api_key=self._el_api_key)
                self.logger.info("Initialized ElevenLabs TTS")
                # Also initialize Kokoro as fallback
                if HAS_KOKORO:
                    self._client = KPipeline(lang_code=self.config.kokoro_lang_code)
                    self.logger.info("Kokoro TTS initialized as fallback")
                return
            except Exception as e:
                self.logger.error(f"Failed to initialize ElevenLabs: {e}")
                self.logger.info("Falling back to Kokoro TTS")
                self._use_elevenlabs = False
                self._el_client = None

        # Otherwise use Kokoro (default)
        engine = self.config.tts_engine

        if engine == "kokoro" or not self._use_elevenlabs:
            if HAS_KOKORO:
                lang_code = self.config.kokoro_lang_code
                self._client = KPipeline(lang_code=lang_code)
                self.logger.info(f"Initialized Kokoro TTS with lang_code: {lang_code}")
            else:
                self.logger.error("Kokoro not available - TTS functionality disabled")
                self._client = None

        elif engine == "elevenlabs":
            if not self._use_elevenlabs:
                self.logger.warning("ElevenLabs requested but no valid API key provided")
                # Fall back to Kokoro
                if HAS_KOKORO:
                    self._client = KPipeline(lang_code=self.config.kokoro_lang_code)
                    self.logger.info("Falling back to Kokoro TTS")
        else:
            self.logger.error(f"Unknown TTS engine: {engine}")
            self._client = None

    def speak(self, text: str, priority: int = 0, blocking: bool = False) -> bool:
        """
        Queue text for speech synthesis (NEW unified API).

        Args:
            text: Text to speak
            priority: Priority level (0-100, higher = more urgent)
            blocking: If True, wait for speech to complete

        Returns:
            True if successfully queued/spoken, False otherwise
        """
        if self._enable_queue:
            # Use queue manager (non-blocking by default)
            success = self._audio_queue.enqueue(text, priority=priority)

            # If blocking requested, wait for queue to empty
            if blocking and success:
                # Wait for this message to be processed
                # (simplified - doesn't track specific message)
                import time

                time.sleep(0.1)
                while self._audio_queue._queue.qsize() > 0:
                    time.sleep(0.1)

            return success
        else:
            # Legacy behavior: spawn thread
            if blocking:
                self._text2speech_sync(text)
                return True
            else:
                thread = threading.Thread(target=self._text2speech_sync, args=(text,))
                thread.start()
                return True

    def call_text2speech_async(self, text: str) -> threading.Thread:
        """Call text-to-speech asynchronously using the configured TTS engine.

        Args:
            text (str): The text to be spoken.

        Returns:
            threading.Thread: The thread handling the asynchronous TTS operation.
        """
        # Use ElevenLabs if available and initialized
        if self._use_elevenlabs and self._el_client is not None:
            thread = threading.Thread(target=self._text2speech_elevenlabs, args=(text,))
        else:
            thread = threading.Thread(target=self._text2speech_kokoro, args=(text,))

        thread.start()
        return thread

    def call_text2speech(self, text: str):
        """
        Synchronous TTS call (blocks until complete).

        Args:
            text: Text to speak
        """
        self._text2speech_sync(text)

    def _text2speech_sync(self, text: str) -> None:
        """
        Synchronous TTS execution (blocks until complete).

        This is the actual TTS function that gets called by the queue manager.

        Args:
            text: Text to synthesize
        """
        # Use ElevenLabs if available and initialized
        if self._use_elevenlabs and self._el_client is not None:
            self._text2speech_elevenlabs(text)
        else:
            self._text2speech_kokoro(text)

    def _text2speech_elevenlabs(self, mytext: str) -> None:
        """Perform TTS using ElevenLabs API.

        Args:
            mytext (str): The text to be synthesized and played.
        """
        if self._el_client is None:
            self.logger.error("ElevenLabs client not initialized")
            return

        try:
            voice = self.config.get("tts.elevenlabs.voice", "Brian")
            model = self.config.get("tts.elevenlabs.model", "eleven_multilingual_v2")

            self.logger.debug(f"Generating speech with ElevenLabs: voice={voice}, model={model}")

            audio = self._el_client.generate(
                text=mytext,
                voice=voice,
                model=model,
            )
            play(audio)
        except Exception as e:
            self.logger.error(f"Error with ElevenLabs: {e}")
            # Fallback to Kokoro if available
            if self._client is not None:
                self.logger.info("Falling back to Kokoro for this request")
                self._text2speech_kokoro(mytext)

    def _text2speech_kokoro(self, mytext: str) -> None:
        """Perform TTS using the Kokoro model with configured settings.

        Args:
            mytext (str): Text to convert to speech.
        """
        if self._client is None:
            self.logger.error("TTS client not initialized")
            return

        try:
            voice = self.config.kokoro_voice
            speed = self.config.kokoro_speed
            split_pattern = self.config.kokoro_split_pattern

            self.logger.debug(f"Generating speech with Kokoro: voice={voice}, speed={speed}")

            generator = self._client(mytext, voice=voice, speed=speed, split_pattern=split_pattern)

            for _, _, audio in generator:
                Text2Speech._play_audio_safely(
                    audio, original_sample_rate=self.config.sample_rate, volume=self.config.audio_volume
                )
                if HAS_SOUNDDEVICE and sd:
                    sd.wait()

        except Exception as e:
            self.logger.error(f"Error with Kokoro: {e}")

    @staticmethod
    def _play_audio_safely(
        audio_tensor: torch.Tensor, original_sample_rate: int = 24000, device: Optional[int] = None, volume: float = 0.8
    ) -> None:
        """Play audio safely by checking supported sample rate and adjusting volume.

        Args:
            audio_tensor (torch.Tensor): The 1D audio waveform tensor.
            original_sample_rate (int, optional): Original sample rate of the audio. Defaults to 24000.
            device (Optional[int], optional): Output device index. Defaults to system default.
            volume (float, optional): Playback volume multiplier (0.0–1.0). Defaults to 0.8.
        """
        if not HAS_SOUNDDEVICE or sd is None:
            print("⚠️ sounddevice not available, skipping audio playback")
            return

        try:
            if device is None:
                device = sd.default.device[1]  # Default output device

            device_info = sd.query_devices(device, "output")
            supported_rate = int(device_info["default_samplerate"])

            if original_sample_rate != supported_rate:
                resampler = torchaudio.transforms.Resample(orig_freq=original_sample_rate, new_freq=supported_rate)
                audio_tensor = resampler(audio_tensor)

            # Normalize and scale volume
            peak = torch.abs(audio_tensor).max()
            if peak > 0:
                audio_tensor = audio_tensor / peak
            audio_tensor = torch.clamp(audio_tensor * volume, -0.95, 0.95)

            # Convert to numpy and play
            audio_np = audio_tensor.cpu().numpy()
            sd.play(audio_np, samplerate=supported_rate, device=device)

        except Exception as e:
            print(f"❌ Error during safe audio playback: {e}")

    def verbose(self) -> bool:
        """Check whether verbose mode is enabled.

        Returns:
            bool: True if verbose mode is active, otherwise False.
        """
        return self._verbose

    def set_voice(self, voice: str) -> None:
        """Set the voice for Kokoro TTS.

        Args:
            voice (str): Voice identifier (e.g., 'af_heart', 'am_adam').
        """
        self.config.set("tts.kokoro.voice", voice)
        self.logger.info(f"Voice changed to: {voice}")

    def set_speed(self, speed: float) -> None:
        """Set the speech speed for Kokoro TTS.

        Args:
            speed (float): Speech speed multiplier (0.5 to 2.0).
        """
        if 0.5 <= speed <= 2.0:
            self.config.set("tts.kokoro.speed", speed)
            self.logger.info(f"Speed changed to: {speed}")
        else:
            self.logger.warning(f"Speed {speed} out of range (0.5-2.0)")

    def set_volume(self, volume: float) -> None:
        """Set the default playback volume.

        Args:
            volume (float): Volume multiplier (0.0 to 1.0).
        """
        if 0.0 <= volume <= 1.0:
            self.config.set("audio.default_volume", volume)
            self.logger.info(f"Volume changed to: {volume}")
        else:
            self.logger.warning(f"Volume {volume} out of range (0.0-1.0)")

    def get_available_devices(self) -> list:
        """Get list of available audio output devices.

        Returns:
            list: List of audio device information.
        """
        if HAS_SOUNDDEVICE and sd:
            return sd.query_devices()
        return []

    def is_using_elevenlabs(self) -> bool:
        """Check if currently using ElevenLabs.

        Returns:
            bool: True if using ElevenLabs, False if using Kokoro.
        """
        return self._use_elevenlabs and self._el_client is not None

    def get_queue_stats(self) -> dict:
        """Get audio queue statistics (only if queue enabled)."""
        if self._audio_queue is not None:
            return self._audio_queue.get_stats()
        return {}
