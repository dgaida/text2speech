"""Unit tests for the CLI module.

This module contains comprehensive tests for the command-line interface,
including argument parsing, Text2Speech integration, and error handling.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import argparse
from io import StringIO


class TestCLIArgumentParsing(unittest.TestCase):
    """Test cases for CLI argument parsing."""

    @patch("text2speech.cli.Text2Speech")
    def test_basic_text_argument(self, mock_tts_class):
        """Test parsing basic text argument."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "Hello world"]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Verify Text2Speech was initialized
        mock_tts_class.assert_called_once_with(config_path=None)

        # Verify text was spoken
        mock_tts.speak.assert_called_once_with("Hello world", blocking=True)

    @patch("text2speech.cli.Text2Speech")
    def test_voice_argument(self, mock_tts_class):
        """Test parsing --voice argument."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "Hello", "--voice", "am_adam"]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Verify voice was set
        mock_tts.set_voice.assert_called_once_with("am_adam")

        # Verify text was spoken
        mock_tts.speak.assert_called_once_with("Hello", blocking=True)

    @patch("text2speech.cli.Text2Speech")
    def test_config_argument(self, mock_tts_class):
        """Test parsing --config argument."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "Hello", "--config", "/path/to/config.yaml"]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Verify Text2Speech was initialized with config path
        mock_tts_class.assert_called_once_with(config_path="/path/to/config.yaml")

    @patch("text2speech.cli.Text2Speech")
    def test_all_arguments_combined(self, mock_tts_class):
        """Test parsing all arguments together."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "Test message", "--voice", "bf_emma", "--config", "/custom/config.yaml"]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Verify all settings
        mock_tts_class.assert_called_once_with(config_path="/custom/config.yaml")
        mock_tts.set_voice.assert_called_once_with("bf_emma")
        mock_tts.speak.assert_called_once_with("Test message", blocking=True)


class TestCLIExecution(unittest.TestCase):
    """Test cases for CLI execution flow."""

    @patch("text2speech.cli.Text2Speech")
    def test_successful_execution(self, mock_tts_class):
        """Test successful CLI execution."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "Success test"]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

    @patch("text2speech.cli.Text2Speech")
    def test_voice_not_set_when_not_provided(self, mock_tts_class):
        """Test that set_voice is not called when --voice not provided."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "No voice arg"]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Verify set_voice was not called
        mock_tts.set_voice.assert_not_called()


class TestCLIErrorHandling(unittest.TestCase):
    """Test cases for CLI error handling."""

    def test_missing_text_argument(self):
        """Test that missing text argument raises error."""
        test_args = ["text2speech"]

        with patch.object(sys, "argv", test_args):
            with patch("sys.stderr", new_callable=StringIO):
                with self.assertRaises(SystemExit):
                    from text2speech.cli import main
                    main()

    @patch("text2speech.cli.Text2Speech")
    def test_tts_initialization_error(self, mock_tts_class):
        """Test handling of Text2Speech initialization error."""
        mock_tts_class.side_effect = Exception("Initialization failed")

        test_args = ["text2speech", "Test"]

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(Exception):
                from text2speech.cli import main
                main()

    @patch("text2speech.cli.Text2Speech")
    def test_tts_call_error(self, mock_tts_class):
        """Test handling of TTS call error."""
        mock_tts = Mock()
        mock_tts.speak.side_effect = Exception("TTS failed")
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "Test"]

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(Exception):
                from text2speech.cli import main
                main()


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI."""

    @patch("text2speech.cli.Text2Speech")
    def test_complete_workflow_with_voice(self, mock_tts_class):
        """Test complete workflow with voice setting."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "Complete workflow test", "--voice", "am_michael", "--config", "test_config.yaml"]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Verify complete call chain
        mock_tts_class.assert_called_once()
        mock_tts.set_voice.assert_called_once()
        mock_tts.speak.assert_called_once()


    @patch("text2speech.cli.Text2Speech")
    def test_long_text_message(self, mock_tts_class):
        """Test CLI with long text message."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        long_text = "This is a very long message. " * 50
        test_args = ["text2speech", long_text]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Verify long text was passed
        mock_tts.speak.assert_called_once_with(long_text, blocking=True)

    @patch("text2speech.cli.Text2Speech")
    def test_special_characters_in_text(self, mock_tts_class):
        """Test CLI with special characters in text."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        special_text = "Hello! How are you? I'm great. #winning"
        test_args = ["text2speech", special_text]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        mock_tts.speak.assert_called_once_with(special_text, blocking=True)

    @patch("text2speech.cli.Text2Speech")
    def test_unicode_text(self, mock_tts_class):
        """Test CLI with unicode text."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        unicode_text = "Hello 世界 🌍"
        test_args = ["text2speech", unicode_text]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        mock_tts.speak.assert_called_once_with(unicode_text, blocking=True)


class TestCLIEdgeCases(unittest.TestCase):
    """Test cases for edge cases."""

    @patch("text2speech.cli.Text2Speech")
    def test_empty_text_string(self, mock_tts_class):
        """Test CLI with empty text string."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", ""]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        # Should still call TTS even with empty string
        mock_tts.speak.assert_called_once_with("", blocking=True)

    @patch("text2speech.cli.Text2Speech")
    def test_whitespace_only_text(self, mock_tts_class):
        """Test CLI with whitespace-only text."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        test_args = ["text2speech", "   "]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        mock_tts.speak.assert_called_once_with("   ", blocking=True)

    @patch("text2speech.cli.Text2Speech")
    def test_multiline_text(self, mock_tts_class):
        """Test CLI with multiline text."""
        mock_tts = Mock()
        mock_tts.speak.return_value = True
        mock_tts_class.return_value = mock_tts

        multiline_text = "Line 1\nLine 2\nLine 3"
        test_args = ["text2speech", multiline_text]

        with patch.object(sys, "argv", test_args):
            from text2speech.cli import main
            main()

        mock_tts.speak.assert_called_once_with(multiline_text, blocking=True)


if __name__ == "__main__":
    unittest.main()
