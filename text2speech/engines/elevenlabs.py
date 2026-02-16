"""ElevenLabs TTS engine implementation."""

import io
from typing import Iterator, Tuple, Optional, Any, cast
import torch
import torchaudio  # type: ignore[import-untyped]

try:
    from elevenlabs.client import ElevenLabs

    HAS_ELEVENLABS = True
except ImportError:
    HAS_ELEVENLABS = False
    ElevenLabs = Any  # type: ignore[assignment, misc]


class ElevenLabsEngine:
    """TTS engine using ElevenLabs API."""

    def __init__(self, api_key: str, model: str = "eleven_multilingual_v2"):
        """Initialize ElevenLabs engine.

        Args:
            api_key (str): ElevenLabs API key.
            model (str): Model identifier.

        Raises:
            ImportError: If elevenlabs package is not installed.
        """
        if not HAS_ELEVENLABS or ElevenLabs is None:
            raise ImportError("elevenlabs package is not installed")
        self.client = ElevenLabs(api_key=api_key)
        self.model = model

    def synthesize(
        self, text: str, voice: Optional[str] = None, speed: float = 1.0
    ) -> Iterator[Tuple[Optional[str], Optional[str], torch.Tensor]]:
        """Synthesize speech using ElevenLabs.

        Args:
            text (str): Text to synthesize.
            voice (Optional[str]): Voice identifier.
            speed (float): Speech speed multiplier (currently ignored for ElevenLabs).

        Yields:
            Iterator[Tuple[Optional[str], Optional[str], torch.Tensor]]:
                Tuples of (graphemes, phonemes, audio_tensor).
        """
        client: Any = self.client
        audio_generator = client.generate(text=text, voice=voice or "Brian", model=self.model)

        if isinstance(audio_generator, bytes):
            audio_tensor = self._bytes_to_tensor(audio_generator)
            yield None, None, audio_tensor
        else:
            # Collect bytes from generator
            audio_bytes = b"".join(audio_generator)
            audio_tensor = self._bytes_to_tensor(audio_bytes)
            yield None, None, audio_tensor

    def _bytes_to_tensor(self, audio_bytes: bytes) -> torch.Tensor:
        """Convert audio bytes to torch Tensor.

        Args:
            audio_bytes (bytes): Raw audio data (typically MP3).

        Returns:
            torch.Tensor: 1D torch Tensor of audio waveform.
        """
        buffer = io.BytesIO(audio_bytes)
        try:
            waveform, _ = torchaudio.load(buffer)
            # Convert to mono if multi-channel
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            return cast(torch.Tensor, waveform.squeeze(0))
        except Exception as e:
            # If torchaudio fails (e.g. missing codec), this will raise
            raise RuntimeError(f"Failed to decode ElevenLabs audio: {e}")
