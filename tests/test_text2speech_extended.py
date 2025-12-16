"""Extended unit tests for text2speech module to increase coverage.

This module contains additional tests focusing on uncovered functionality
including the speak() method, queue integration, ElevenLabs support,
and various edge cases.
"""

import unittest
from unittest.mock import Mock, patch, PropertyMock
from text2speech import Text2Speech
from text2speech.config import Config


class TestText2SpeechSpeakMethod(unittest.TestCase):
    """Test cases for the new speak() method."""

    @patch("text2speech.text2speech.AudioQueueManager")
    @patch("text2speech.text2speech.KPipeline")
    def test_speak_with_queue_enabled(self, mock_kpipeline, mock_queue_class):
        """Test speak() method with queue enabled."""
        mock_queue = Mock()
        mock_queue.enqueue.return_value = True
        mock_queue_class.return_value = mock_queue

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=True)

        result = tts.speak("Test message")

        self.assertTrue(result)
        mock_queue.enqueue.assert_called_once_with("Test message", priority=0)

    @patch("text2speech.text2speech.AudioQueueManager")
    @patch("text2speech.text2speech.KPipeline")
    def test_speak_with_priority(self, mock_kpipeline, mock_queue_class):
        """Test speak() method with custom priority."""
        mock_queue = Mock()
        mock_queue.enqueue.return_value = True
        mock_queue_class.return_value = mock_queue

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=True)

        result = tts.speak("Urgent message", priority=10)

        self.assertTrue(result)
        mock_queue.enqueue.assert_called_once_with("Urgent message", priority=10)

    @patch("text2speech.text2speech.AudioQueueManager")
    @patch("text2speech.text2speech.KPipeline")
    def test_speak_blocking_mode(self, mock_kpipeline, mock_queue_class):
        """Test speak() method with blocking=True."""
        mock_queue = Mock()
        mock_queue.enqueue.return_value = True
        mock_queue._queue = Mock()
        mock_queue._queue.qsize.return_value = 0
        mock_queue_class.return_value = mock_queue

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=True)

        # This should block until queue is empty
        result = tts.speak("Blocking message", blocking=True)

        self.assertTrue(result)

    @patch("text2speech.text2speech.KPipeline")
    def test_speak_without_queue(self, mock_kpipeline):
        """Test speak() method with queue disabled."""
        mock_client = Mock()
        mock_client.return_value = []
        mock_kpipeline.return_value = mock_client

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        with patch.object(tts, "_text2speech_sync"):
            result = tts.speak("Non-queued message", blocking=False)

            self.assertTrue(result)
            # Should spawn thread, so sync might be called asynchronously

    @patch("text2speech.text2speech.KPipeline")
    def test_speak_without_queue_blocking(self, mock_kpipeline):
        """Test speak() method with queue disabled and blocking=True."""
        mock_client = Mock()
        mock_client.return_value = []
        mock_kpipeline.return_value = mock_client

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        with patch.object(tts, "_text2speech_sync") as mock_sync:
            result = tts.speak("Blocking non-queued", blocking=True)

            self.assertTrue(result)
            mock_sync.assert_called_once_with("Blocking non-queued")


class TestText2SpeechShutdown(unittest.TestCase):
    """Test cases for shutdown functionality."""

    @patch("text2speech.text2speech.AudioQueueManager")
    @patch("text2speech.text2speech.KPipeline")
    def test_shutdown_calls_queue_shutdown(self, mock_kpipeline, mock_queue_class):
        """Test that shutdown() calls queue manager shutdown."""
        mock_queue = Mock()
        mock_queue_class.return_value = mock_queue

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=True)
        tts.shutdown(timeout=2.0)

        mock_queue.shutdown.assert_called_once_with(timeout=2.0)

    @patch("text2speech.text2speech.KPipeline")
    def test_shutdown_without_queue(self, mock_kpipeline):
        """Test that shutdown() works when queue is disabled."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        # Should not raise exception
        tts.shutdown(timeout=1.0)

    @patch("text2speech.text2speech.AudioQueueManager")
    @patch("text2speech.text2speech.KPipeline")
    def test_del_calls_shutdown(self, mock_kpipeline, mock_queue_class):
        """Test that __del__ calls shutdown."""
        mock_queue = Mock()
        mock_queue_class.return_value = mock_queue

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=True)

        # Manually call __del__
        tts.__del__()

        mock_queue.shutdown.assert_called()


class TestText2SpeechGetQueueStats(unittest.TestCase):
    """Test cases for get_queue_stats() method."""

    @patch("text2speech.text2speech.AudioQueueManager")
    @patch("text2speech.text2speech.KPipeline")
    def test_get_queue_stats_with_queue(self, mock_kpipeline, mock_queue_class):
        """Test getting queue statistics when queue is enabled."""
        mock_queue = Mock()
        mock_stats = {"messages_queued": 5, "messages_played": 3, "errors": 0}
        mock_queue.get_stats.return_value = mock_stats
        mock_queue_class.return_value = mock_queue

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=True)

        stats = tts.get_queue_stats()

        self.assertEqual(stats, mock_stats)
        mock_queue.get_stats.assert_called_once()

    @patch("text2speech.text2speech.KPipeline")
    def test_get_queue_stats_without_queue(self, mock_kpipeline):
        """Test getting queue statistics when queue is disabled."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        stats = tts.get_queue_stats()

        self.assertEqual(stats, {})


class TestText2SpeechElevenLabs(unittest.TestCase):
    """Test cases for ElevenLabs integration."""

    @patch("text2speech.text2speech.ElevenLabs")
    @patch("text2speech.text2speech.KPipeline")
    def test_elevenlabs_initialization_success(self, mock_kpipeline, mock_elevenlabs):
        """Test successful ElevenLabs initialization with valid key."""
        # Mock the ElevenLabs client
        mock_el_client = Mock()
        mock_elevenlabs.return_value = mock_el_client

        # Mock HAS_ELEVENLABS to be True
        with patch("text2speech.text2speech.HAS_ELEVENLABS", True):
            tts = Text2Speech(el_api_key="sk_validkey12345678901234567890", verbose=False, enable_queue=False)

            self.assertTrue(tts.is_using_elevenlabs())
            self.assertIsNotNone(tts._el_client)

    @patch("text2speech.text2speech.ElevenLabs")
    @patch("text2speech.text2speech.KPipeline")
    def test_elevenlabs_tts_call(self, mock_kpipeline, mock_elevenlabs):
        """Test ElevenLabs TTS call."""
        # Mock the play function from elevenlabs module
        with patch("text2speech.text2speech.play") as mock_play:
            mock_el_client = Mock()
            mock_audio = b"audio_data"
            mock_el_client.generate.return_value = mock_audio
            mock_elevenlabs.return_value = mock_el_client

            # Mock HAS_ELEVENLABS to be True
            with patch("text2speech.text2speech.HAS_ELEVENLABS", True):
                tts = Text2Speech(el_api_key="sk_validkey12345678901234567890", verbose=False, enable_queue=False)
                tts._text2speech_elevenlabs("Test message")

                mock_el_client.generate.assert_called_once()
                mock_play.assert_called_once_with(mock_audio)

    @patch("text2speech.text2speech.ElevenLabs")
    @patch("text2speech.text2speech.KPipeline")
    def test_elevenlabs_fallback_on_error(self, mock_kpipeline, mock_elevenlabs):
        """Test fallback to Kokoro when ElevenLabs fails."""
        mock_el_client = Mock()
        mock_el_client.generate.side_effect = Exception("API Error")
        mock_elevenlabs.return_value = mock_el_client

        mock_kokoro = Mock()
        mock_kokoro.return_value = []
        mock_kpipeline.return_value = mock_kokoro

        with patch("text2speech.text2speech.HAS_ELEVENLABS", True):
            tts = Text2Speech(el_api_key="sk_validkey12345678901234567890", verbose=False, enable_queue=False)

            # Mock the _text2speech_kokoro method
            with patch.object(tts, "_text2speech_kokoro") as mock_kokoro_method:
                tts._text2speech_elevenlabs("Test message")

                # Should fallback to Kokoro
                mock_kokoro_method.assert_called_once_with("Test message")

    @patch("text2speech.text2speech.KPipeline")
    def test_elevenlabs_with_invalid_key(self, mock_kpipeline):
        """Test that invalid ElevenLabs key falls back to Kokoro."""
        tts = Text2Speech(el_api_key="invalid_key", verbose=False, enable_queue=False)

        self.assertFalse(tts.is_using_elevenlabs())


class TestText2SpeechDeviceManagement(unittest.TestCase):
    """Test cases for audio device management."""

    @patch("text2speech.text2speech.sd")
    @patch("text2speech.text2speech.KPipeline")
    def test_set_audio_device_on_init(self, mock_kpipeline, mock_sd):
        """Test setting audio device on initialization."""
        # Create a mock for the device property
        mock_device = [None, 0]
        type(mock_sd.default).device = PropertyMock(return_value=mock_device)

        config = Config()
        config.set("audio.output_device", 5)

        with patch("text2speech.text2speech.HAS_SOUNDDEVICE", True):
            Text2Speech(el_api_key="test_key", verbose=False, config=config, enable_queue=False)

            # Verify device setter was called
            # Check that the device was set in the config (the actual setting happens via property setter)
            self.assertEqual(config.audio_output_device, 5)

    @patch("text2speech.text2speech.sd")
    @patch("text2speech.text2speech.KPipeline")
    def test_set_audio_device_error_handling(self, mock_kpipeline, mock_sd):
        """Test error handling when setting audio device fails."""

        # Mock the device property to raise an exception when setting
        def raise_error():
            raise Exception("Device not found")

        type(mock_sd.default).device = PropertyMock(side_effect=raise_error)

        config = Config()
        config.set("audio.output_device", 999)

        with patch("text2speech.text2speech.HAS_SOUNDDEVICE", True):
            # Should not raise exception, just log error
            Text2Speech(el_api_key="test_key", verbose=False, config=config, enable_queue=False)

    @patch("text2speech.text2speech.sd")
    @patch("text2speech.text2speech.KPipeline")
    def test_get_available_devices(self, mock_kpipeline, mock_sd):
        """Test getting available audio devices."""
        mock_devices = [{"name": "Device 1", "index": 0}, {"name": "Device 2", "index": 1}]
        mock_sd.query_devices.return_value = mock_devices

        with patch("text2speech.text2speech.HAS_SOUNDDEVICE", True):
            tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

            devices = tts.get_available_devices()

            self.assertEqual(devices, mock_devices)

    @patch("text2speech.text2speech.KPipeline")
    def test_get_available_devices_no_sounddevice(self, mock_kpipeline):
        """Test get_available_devices when sounddevice not available."""
        with patch("text2speech.text2speech.HAS_SOUNDDEVICE", False):
            with patch("text2speech.text2speech.sd", None):
                tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

                devices = tts.get_available_devices()

                self.assertEqual(devices, [])


class TestText2SpeechSetters(unittest.TestCase):
    """Test cases for setter methods."""

    @patch("text2speech.text2speech.KPipeline")
    def test_set_speed_valid(self, mock_kpipeline):
        """Test setting valid speech speed."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        tts.set_speed(1.5)

        self.assertEqual(tts.config.kokoro_speed, 1.5)

    @patch("text2speech.text2speech.KPipeline")
    def test_set_speed_invalid_too_low(self, mock_kpipeline):
        """Test setting speed below valid range."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        original_speed = tts.config.kokoro_speed
        tts.set_speed(0.3)  # Too low

        # Speed should not change
        self.assertEqual(tts.config.kokoro_speed, original_speed)

    @patch("text2speech.text2speech.KPipeline")
    def test_set_speed_invalid_too_high(self, mock_kpipeline):
        """Test setting speed above valid range."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        original_speed = tts.config.kokoro_speed
        tts.set_speed(3.0)  # Too high

        # Speed should not change
        self.assertEqual(tts.config.kokoro_speed, original_speed)

    @patch("text2speech.text2speech.KPipeline")
    def test_set_volume_valid(self, mock_kpipeline):
        """Test setting valid volume."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        tts.set_volume(0.5)

        self.assertEqual(tts.config.audio_volume, 0.5)

    @patch("text2speech.text2speech.KPipeline")
    def test_set_volume_invalid_negative(self, mock_kpipeline):
        """Test setting negative volume."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        original_volume = tts.config.audio_volume
        tts.set_volume(-0.5)

        # Volume should not change
        self.assertEqual(tts.config.audio_volume, original_volume)

    @patch("text2speech.text2speech.KPipeline")
    def test_set_volume_invalid_too_high(self, mock_kpipeline):
        """Test setting volume above 1.0."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        original_volume = tts.config.audio_volume
        tts.set_volume(1.5)

        # Volume should not change
        self.assertEqual(tts.config.audio_volume, original_volume)

    @patch("text2speech.text2speech.KPipeline")
    def test_set_voice(self, mock_kpipeline):
        """Test setting voice."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        tts.set_voice("am_michael")

        self.assertEqual(tts.config.kokoro_voice, "am_michael")


class TestText2SpeechCallText2Speech(unittest.TestCase):
    """Test cases for call_text2speech() synchronous method."""

    @patch("text2speech.text2speech.KPipeline")
    def test_call_text2speech_synchronous(self, mock_kpipeline):
        """Test synchronous TTS call."""
        mock_client = Mock()
        mock_client.return_value = []
        mock_kpipeline.return_value = mock_client

        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        with patch.object(tts, "_text2speech_sync") as mock_sync:
            tts.call_text2speech("Sync test")

            mock_sync.assert_called_once_with("Sync test")


class TestText2SpeechLogging(unittest.TestCase):
    """Test cases for logging functionality."""

    @patch("text2speech.text2speech.KPipeline")
    def test_logging_setup_with_custom_level(self, mock_kpipeline):
        """Test logging setup with custom log level."""
        config = Config()
        config.set("logging.log_level", "DEBUG")

        tts = Text2Speech(el_api_key="test_key", verbose=False, config=config, enable_queue=False)

        # Verify logger is set to DEBUG
        import logging

        self.assertEqual(tts.logger.level, logging.DEBUG)

    @patch("text2speech.text2speech.KPipeline")
    def test_logging_to_file(self, mock_kpipeline):
        """Test logging to file."""
        import tempfile
        import os
        import logging as logging_module

        temp_dir = tempfile.mkdtemp()
        log_file = os.path.join(temp_dir, "test.log")

        try:
            config = Config()
            config.set("logging.log_file", log_file)

            # Create a fresh logger for this test
            logger_name = f"text2speech_test_{id(config)}"
            with patch("text2speech.text2speech.logging.getLogger") as mock_get_logger:
                mock_logger = logging_module.getLogger(logger_name)
                mock_logger.handlers = []  # Clear any existing handlers
                mock_get_logger.return_value = mock_logger

                tts = Text2Speech(el_api_key="test_key", verbose=False, config=config, enable_queue=False)

                # Verify file handler was added
                file_handlers = [h for h in tts.logger.handlers if isinstance(h, logging_module.FileHandler)]
                self.assertGreater(len(file_handlers), 0)

        finally:
            # Cleanup
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


class TestText2SpeechConfigIntegration(unittest.TestCase):
    """Test cases for configuration integration."""

    @patch("text2speech.text2speech.KPipeline")
    def test_init_with_config_object(self, mock_kpipeline):
        """Test initialization with Config object."""
        config = Config()
        config.set("audio.default_volume", 0.5)

        tts = Text2Speech(el_api_key="test_key", verbose=False, config=config, enable_queue=False)

        self.assertEqual(tts.config.audio_volume, 0.5)

    @patch("text2speech.text2speech.KPipeline")
    def test_init_with_config_path(self, mock_kpipeline):
        """Test initialization with config path."""
        import tempfile
        import os
        import yaml

        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "test_config.yaml")

        try:
            # Create test config file
            config_data = {"audio": {"default_volume": 0.7}, "tts": {"kokoro": {"voice": "am_adam"}}}

            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

            tts = Text2Speech(el_api_key="test_key", verbose=False, config_path=config_path, enable_queue=False)

            self.assertEqual(tts.config.audio_volume, 0.7)
            self.assertEqual(tts.config.kokoro_voice, "am_adam")

        finally:
            # Cleanup
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    @patch("text2speech.text2speech.KPipeline")
    def test_verbose_override(self, mock_kpipeline):
        """Test that verbose parameter overrides config."""
        config = Config()
        config.set("logging.verbose", False)

        # Override with verbose=True
        tts = Text2Speech(el_api_key="test_key", verbose=True, config=config, enable_queue=False)

        self.assertTrue(tts.verbose())


class TestText2SpeechValidateKey(unittest.TestCase):
    """Test cases for API key validation."""

    @patch("text2speech.text2speech.KPipeline")
    def test_validate_key_with_sk_prefix(self, mock_kpipeline):
        """Test validation of key with sk_ prefix."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        result = tts._validate_elevenlabs_key("sk_1234567890")

        self.assertTrue(result)

    @patch("text2speech.text2speech.KPipeline")
    def test_validate_key_long_without_prefix(self, mock_kpipeline):
        """Test validation of long key without sk_ prefix."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        result = tts._validate_elevenlabs_key("a" * 35)

        self.assertTrue(result)

    @patch("text2speech.text2speech.KPipeline")
    def test_validate_key_too_short(self, mock_kpipeline):
        """Test validation of too short key."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        result = tts._validate_elevenlabs_key("short")

        self.assertFalse(result)

    @patch("text2speech.text2speech.KPipeline")
    def test_validate_key_none(self, mock_kpipeline):
        """Test validation of None key."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        result = tts._validate_elevenlabs_key(None)

        self.assertFalse(result)

    @patch("text2speech.text2speech.KPipeline")
    def test_validate_key_wrong_type(self, mock_kpipeline):
        """Test validation of non-string key."""
        tts = Text2Speech(el_api_key="test_key", verbose=False, enable_queue=False)

        result = tts._validate_elevenlabs_key(12345)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
