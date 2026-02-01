"""Kokoro TTS engine implementation."""

from typing import Iterator, Tuple, Optional
import torch

try:
    from kokoro import KPipeline  # type: ignore[import-untyped]

    HAS_KOKORO = True
except ImportError:
    HAS_KOKORO = False
    KPipeline = None


class KokoroEngine:
    """TTS engine using the Kokoro model."""

    def __init__(self, lang_code: str = "a"):
        """
        Initialize Kokoro engine.

        Args:
            lang_code: Language code for the pipeline.

        Raises:
            ImportError: If kokoro package is not installed.
        """
        if not HAS_KOKORO or KPipeline is None:
            raise ImportError("kokoro package is not installed")
        try:
            self.pipeline = KPipeline(lang_code=lang_code)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Kokoro pipeline: {e}")

    def synthesize(
        self, text: str, voice: Optional[str] = None, speed: float = 1.0
    ) -> Iterator[Tuple[Optional[str], Optional[str], torch.Tensor]]:
        """
        Synthesize speech using Kokoro.

        Args:
            text: Text to synthesize.
            voice: Voice identifier.
            speed: Speech speed multiplier.

        Yields:
            Tuples of (graphemes, phonemes, audio_tensor).
        """
        # Kokoro pipeline returns a generator
        generator = self.pipeline(text, voice=voice, speed=speed)
        for gs, ps, audio in generator:
            if not isinstance(audio, torch.Tensor):
                audio = torch.from_numpy(audio)
            yield gs, ps, audio
