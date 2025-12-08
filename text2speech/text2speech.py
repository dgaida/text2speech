"""Text-to-speech module with configurable settings."""

from typing import Optional
import logging

try:
    from elevenlabs import play

    # from elevenlabs.client import ElevenLabs
except ImportError as e:
    print("error importing elevenlabs:", e)

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


class Text2Speech:
    """Text-to-Speech (TTS) class with configurable settings.

    This class provides text-to-speech functionality using the Kokoro model with
    configuration support via YAML files. Supports asynchronous speech synthesis
    and safe audio playback with dynamic resampling.
    """

    def __init__(
        self,
        el_api_key: Optional[str] = None,
        verbose: Optional[bool] = None,
        config_path: Optional[str] = None,
        config: Optional[Config] = None,
    ) -> None:
        """Initialize the Text2Speech instance.

        Args:
            el_api_key (str, optional): API key for ElevenLabs (legacy, not used).
            verbose (bool, optional): If True, prints debug info. Overrides config if set.
            config_path (str, optional): Path to config.yaml file.
            config (Config, optional): Pre-loaded Config object. Takes precedence over config_path.
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

        # Initialize TTS client
        self._client = None
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
        """Initialize the TTS engine based on configuration."""
        engine = self.config.tts_engine

        if engine == "kokoro":
            if HAS_KOKORO:
                lang_code = self.config.kokoro_lang_code
                self._client = KPipeline(lang_code=lang_code)
                self.logger.info(f"Initialized Kokoro TTS with lang_code: {lang_code}")
            else:
                self.logger.error("Kokoro not available - TTS functionality disabled")
                self._client = None

        elif engine == "elevenlabs":
            self.logger.warning("ElevenLabs is deprecated and no longer supported")
            # Fall back to Kokoro
            if HAS_KOKORO:
                self._client = KPipeline(lang_code=self.config.kokoro_lang_code)
                self.logger.info("Falling back to Kokoro TTS")

        else:
            self.logger.error(f"Unknown TTS engine: {engine}")
            self._client = None

    def call_text2speech_async(self, text: str) -> threading.Thread:
        """Call text-to-speech asynchronously using the configured TTS engine.

        Args:
            text (str): The text to be spoken.

        Returns:
            threading.Thread: The thread handling the asynchronous TTS operation.
        """
        thread = threading.Thread(target=self._text2speech_kokoro, args=(text,))
        thread.start()
        return thread

    def _text2speech(self, mytext: str) -> None:
        """Legacy ElevenLabs TTS method (deprecated).

        Args:
            mytext (str): The text to be synthesized and played.
        """
        if self._client is not None:
            try:
                audio = self._client.generate(
                    text=mytext,
                    voice=self.config.get("tts.elevenlabs.voice", "Brian"),
                    model=self.config.get("tts.elevenlabs.model", "eleven_multilingual_v2"),
                )
                play(audio)
            except Exception as e:
                self.logger.error(f"Error with ElevenLabs: {e}")

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

            self.logger.debug(f"Generating speech: voice={voice}, speed={speed}")

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
