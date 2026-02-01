"""Unit tests for audio functionality."""

import unittest
import threading
from unittest.mock import Mock, patch
import torch
import numpy as np
import time
from text2speech.audio_queue import AudioTask, AudioQueueManager
from text2speech.text2speech import Text2Speech

class TestAudioTask(unittest.TestCase):
    """Test cases for AudioTask dataclass."""

    def test_audio_task_creation(self):
        """Test AudioTask creation with defaults."""
        task = AudioTask(text="Hello world")
        self.assertEqual(task.text, "Hello world")
        self.assertEqual(task.priority, 0)
        self.assertIsNotNone(task.timestamp)

    def test_audio_task_comparison_by_priority(self):
        """Test that tasks are compared by priority (higher first)."""
        task_low = AudioTask(text="Low", priority=1)
        task_high = AudioTask(text="High", priority=10)
        self.assertTrue(task_high < task_low)

class TestAudioPlayback(unittest.TestCase):
    """Test cases for audio playback safety."""

    @patch("text2speech.text2speech.HAS_SOUNDDEVICE", True)
    @patch("text2speech.text2speech.sd")
    def test_play_audio_safely(self, mock_sd: Mock) -> None:
        """Test that _play_audio_safely calls sounddevice correctly."""
        mock_sd.default.device = [0, 1]
        mock_sd.query_devices.return_value = {"default_samplerate": 24000}

        audio = torch.randn(24000)
        Text2Speech._play_audio_safely(audio, original_sample_rate=24000, volume=0.8)

        mock_sd.play.assert_called_once()
        args, kwargs = mock_sd.play.call_args
        self.assertIsInstance(args[0], np.ndarray)
        self.assertEqual(kwargs["samplerate"], 24000)

class TestAudioQueueManager(unittest.TestCase):
    """Test cases for AudioQueueManager."""

    def test_enqueue(self):
        """Test enqueuing messages."""
        mock_tts = Mock()
        manager = AudioQueueManager(tts_callable=mock_tts)

        success = manager.enqueue("Test message", priority=5)
        self.assertTrue(success)
        self.assertEqual(manager.get_stats()["messages_queued"], 1)

    def test_is_duplicate(self):
        """Test duplicate detection."""
        mock_tts = Mock()
        manager = AudioQueueManager(tts_callable=mock_tts, duplicate_timeout=10.0)

        manager.enqueue("Message", priority=0)
        is_dup = manager.enqueue("Message", priority=0)

        self.assertFalse(is_dup)
        self.assertEqual(manager.get_stats()["messages_skipped_duplicate"], 1)

    def test_worker_processes_messages(self):
        """Test that worker processes queued messages."""
        processing_started = threading.Event()
        processing_done = threading.Event()

        def controlled_tts(text):
            processing_started.set()
            processing_done.wait(timeout=2.0)

        manager = AudioQueueManager(tts_callable=controlled_tts)
        manager.start()
        manager.enqueue("Test message")

        # Wait for specific events, not arbitrary time
        self.assertTrue(processing_started.wait(timeout=2.0))
        processing_done.set()

        # Wait for message to be marked as played
        timeout = time.time() + 2.0
        while manager.get_stats()["messages_played"] == 0 and time.time() < timeout:
            time.sleep(0.1)

        self.assertEqual(manager.get_stats()["messages_played"], 1)
        manager.shutdown()
