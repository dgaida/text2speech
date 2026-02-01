"""Base engine interface for text2speech."""

from typing import Protocol, Iterator, Tuple, Optional, runtime_checkable
import torch


@runtime_checkable
class TTSEngine(Protocol):
    """Protocol for TTS engine implementations."""

    def synthesize(
        self, text: str, voice: Optional[str] = None, speed: float = 1.0
    ) -> Iterator[Tuple[Optional[str], Optional[str], torch.Tensor]]:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice: Voice identifier
            speed: Speech speed multiplier

        Yields:
            Tuples of (graphemes, phonemes, audio_tensor)
        """
        ...
