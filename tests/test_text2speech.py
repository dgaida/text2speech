"""Unit tests for the Text2Speech main class."""

import unittest
from unittest.mock import Mock, patch
from text2speech import Text2Speech


class TestText2Speech(unittest.TestCase):
    """Test cases for Text2Speech class."""

    @patch("text2speech.text2speech.KokoroEngine")
    def test_init_defaults_to_kokoro(self, mock_kokoro: Mock) -> None:
        """Test that initialization defaults to Kokoro."""
        tts = Text2Speech(enable_queue=False)
        self.assertIsNotNone(tts._engine)

    def test_init_with_elevenlabs(self) -> None:
        """Test initialization with ElevenLabs API key."""
        with patch("text2speech.text2speech.ElevenLabsEngine"):
            # Configure mock instance to have the right class name if needed,
            # but is_using_elevenlabs now checks for "ElevenLabsEngine" in the string representation.
            # MagicMock instances usually show up as <MagicMock name='ElevenLabsEngine()' id='...'>
            tts = Text2Speech(el_api_key="sk_valid_key_long_enough", enable_queue=False)
            self.assertTrue(tts.is_using_elevenlabs())

    @patch("text2speech.text2speech.KokoroEngine")
    def test_speak_sync(self, mock_kokoro: Mock) -> None:
        """Test synchronous speak call."""
        tts = Text2Speech(enable_queue=False)
        with patch.object(tts, "speak_sync") as mock_speak_sync:
            tts.speak("Hello", blocking=True)
            mock_speak_sync.assert_called_once_with("Hello")

    @patch("text2speech.text2speech.AudioQueueManager")
    @patch("text2speech.text2speech.KokoroEngine")
    def test_speak_queued(self, mock_kokoro: Mock, mock_aqm: Mock) -> None:
        """Test queued speak call."""
        tts = Text2Speech(enable_queue=True)
        tts.speak("Hello", priority=10)
        mock_aqm.return_value.enqueue.assert_called_with("Hello", priority=10)

    @patch("text2speech.text2speech.KokoroEngine")
    def test_setters(self, mock_kokoro: Mock) -> None:
        """Test setting voice, speed and volume."""
        tts = Text2Speech(enable_queue=False)
        tts.set_voice("af_heart")
        self.assertEqual(tts.config.kokoro_voice, "af_heart")

        tts.set_speed(1.5)
        self.assertEqual(tts.config.kokoro_speed, 1.5)

        tts.set_volume(0.5)
        self.assertEqual(tts.config.audio_volume, 0.5)
