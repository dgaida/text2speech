"""Unit tests for the TTS engines."""

import unittest
from unittest.mock import Mock, patch
import torch
from text2speech.engines import KokoroEngine, ElevenLabsEngine


class TestKokoroEngine(unittest.TestCase):
    """Test cases for KokoroEngine."""

    @patch("text2speech.engines.kokoro.KPipeline")
    def test_init(self, mock_kpipeline: Mock) -> None:
        """Test KokoroEngine initialization."""
        KokoroEngine(lang_code="a")
        mock_kpipeline.assert_called_once_with(lang_code="a")

    @patch("text2speech.engines.kokoro.KPipeline")
    def test_synthesize(self, mock_kpipeline: Mock) -> None:
        """Test KokoroEngine synthesis."""
        mock_instance = mock_kpipeline.return_value
        mock_instance.return_value = [("gs", "ps", torch.randn(24000))]

        engine = KokoroEngine(lang_code="a")
        results = list(engine.synthesize("test", voice="af_heart", speed=1.0))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "gs")
        self.assertEqual(results[0][1], "ps")
        self.assertIsInstance(results[0][2], torch.Tensor)


class TestElevenLabsEngine(unittest.TestCase):
    """Test cases for ElevenLabsEngine."""

    @patch("text2speech.engines.elevenlabs.HAS_ELEVENLABS", True)
    @patch("text2speech.engines.elevenlabs.ElevenLabs")
    def test_init(self, mock_el: Mock) -> None:
        """Test ElevenLabsEngine initialization."""
        ElevenLabsEngine(api_key="sk_test_key")
        mock_el.assert_called_once_with(api_key="sk_test_key")

    @patch("text2speech.engines.elevenlabs.HAS_ELEVENLABS", True)
    @patch("text2speech.engines.elevenlabs.torchaudio.load")
    @patch("text2speech.engines.elevenlabs.ElevenLabs")
    def test_synthesize(self, mock_el: Mock, mock_load: Mock) -> None:
        """Test ElevenLabsEngine synthesis."""
        mock_client = mock_el.return_value
        mock_client.generate.return_value = b"audio_data"
        mock_load.return_value = (torch.randn(1, 24000), 24000)

        engine = ElevenLabsEngine(api_key="sk_test_key")
        results = list(engine.synthesize("test", voice="Brian"))

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0][2], torch.Tensor)
