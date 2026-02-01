"""Property-based tests for text2speech."""

import unittest
from unittest.mock import patch
from hypothesis import given, strategies as st
from text2speech import Text2Speech


class TestText2SpeechProperties(unittest.TestCase):
    """Property-based tests for Text2Speech."""

    @given(st.text(min_size=0, max_size=1000))
    def test_speak_handles_any_text(self, text: str) -> None:
        """Test that speak() handles arbitrary text safely."""
        # Use a real Config but mock the engine and queue
        with patch("text2speech.text2speech.KokoroEngine"):
            tts = Text2Speech(enable_queue=False)
            with patch.object(tts, "speak_sync"):
                # Should not raise exception
                result = tts.speak(text, blocking=False)
                self.assertIsInstance(result, bool)

    @given(st.integers(min_value=0, max_value=100))
    def test_speak_handles_priorities(self, priority: int) -> None:
        """Test that speak() handles various priority levels."""
        with patch("text2speech.text2speech.KokoroEngine"):
            tts = Text2Speech(enable_queue=True)
            with patch.object(tts._audio_queue, "enqueue", return_value=True) as mock_enqueue:
                tts.speak("test", priority=priority)
                mock_enqueue.assert_called_with("test", priority=priority)
