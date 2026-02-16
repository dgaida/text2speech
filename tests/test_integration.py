"""Integration tests for text2speech."""

import unittest
import pytest
import torch
from unittest.mock import patch
from text2speech import Text2Speech


@pytest.mark.integration
class TestText2SpeechIntegration(unittest.TestCase):
    """Integration tests for Text2Speech."""

    @patch("text2speech.text2speech.HAS_SOUNDDEVICE", True)
    @patch("text2speech.text2speech.sd")
    @patch("text2speech.engines.kokoro.KPipeline")
    def test_complete_kokoro_flow(self, mock_kpipeline, mock_sd):
        """Test complete flow from speak() to sounddevice.play() with Kokoro."""
        # Setup mocks
        mock_pipeline_instance = mock_kpipeline.return_value
        mock_pipeline_instance.return_value = [(None, None, torch.randn(24000))]

        mock_sd.default.device = [0, 1]
        mock_sd.query_devices.return_value = {"default_samplerate": 24000}

        # Initialize TTS
        tts = Text2Speech(enable_queue=False)

        # Speak
        tts.speak("Hello integration test", blocking=True)

        # Verify sounddevice was called
        mock_sd.play.assert_called()
