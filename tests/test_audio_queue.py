"""Unit tests for the audio_queue module.

This module contains comprehensive tests for the AudioQueueManager class,
including initialization, queueing, worker thread behavior, and statistics.
"""

import unittest
from unittest.mock import Mock, patch
import threading
import time
import queue
import logging
from text2speech.audio_queue import AudioTask, AudioQueueManager


class TestAudioTask(unittest.TestCase):
    """Test cases for AudioTask dataclass."""

    def test_audio_task_creation(self):
        """Test AudioTask creation with defaults."""
        task = AudioTask(text="Hello world")

        self.assertEqual(task.text, "Hello world")
        self.assertEqual(task.priority, 0)
        self.assertIsNotNone(task.timestamp)
        self.assertIsInstance(task.timestamp, float)

    def test_audio_task_with_priority(self):
        """Test AudioTask creation with custom priority."""
        task = AudioTask(text="Urgent message", priority=10)

        self.assertEqual(task.text, "Urgent message")
        self.assertEqual(task.priority, 10)

    def test_audio_task_with_timestamp(self):
        """Test AudioTask creation with custom timestamp."""
        custom_time = time.time() - 100
        task = AudioTask(text="Old message", timestamp=custom_time)

        self.assertEqual(task.timestamp, custom_time)

    def test_audio_task_comparison_by_priority(self):
        """Test that tasks are compared by priority (higher first)."""
        task_low = AudioTask(text="Low", priority=1)
        task_high = AudioTask(text="High", priority=10)

        # Higher priority should be "less than" (processed first)
        self.assertTrue(task_high < task_low)
        self.assertFalse(task_low < task_high)

    def test_audio_task_comparison_by_timestamp(self):
        """Test that tasks with same priority are compared by timestamp."""
        old_time = time.time() - 100
        new_time = time.time()

        task_old = AudioTask(text="Old", priority=5, timestamp=old_time)
        task_new = AudioTask(text="New", priority=5, timestamp=new_time)

        # Older timestamp should be "less than" (processed first)
        self.assertTrue(task_old < task_new)
        self.assertFalse(task_new < task_old)


class TestAudioQueueManagerInitialization(unittest.TestCase):
    """Test cases for AudioQueueManager initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        self.assertIsNotNone(manager._tts_callable)
        self.assertEqual(manager._max_queue_size, 50)
        self.assertEqual(manager._duplicate_timeout, 2.0)
        self.assertIsNotNone(manager._logger)
        self.assertIsInstance(manager._queue, queue.PriorityQueue)
        self.assertIsNone(manager._worker_thread)
        self.assertFalse(manager._shutdown_event.is_set())

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        mock_tts = Mock()
        custom_logger = logging.getLogger("test")

        manager = AudioQueueManager(mock_tts, max_queue_size=100, duplicate_timeout=5.0, logger=custom_logger)

        self.assertEqual(manager._max_queue_size, 100)
        self.assertEqual(manager._duplicate_timeout, 5.0)
        self.assertEqual(manager._logger, custom_logger)

    def test_statistics_initialized(self):
        """Test that statistics are properly initialized."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        stats = manager.get_stats()
        self.assertEqual(stats["messages_queued"], 0)
        self.assertEqual(stats["messages_played"], 0)
        self.assertEqual(stats["messages_skipped_duplicate"], 0)
        self.assertEqual(stats["messages_skipped_full"], 0)
        self.assertEqual(stats["errors"], 0)


class TestAudioQueueManagerStartStop(unittest.TestCase):
    """Test cases for starting and stopping the manager."""

    def test_start_creates_worker_thread(self):
        """Test that start() creates and starts worker thread."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        manager.start()

        self.assertIsNotNone(manager._worker_thread)
        self.assertTrue(manager._worker_thread.is_alive())
        self.assertTrue(manager.is_running())

        manager.shutdown(timeout=1.0)

    def test_start_when_already_running(self):
        """Test that start() doesn't create duplicate threads."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        manager.start()
        first_thread = manager._worker_thread

        manager.start()  # Should warn and not create new thread

        self.assertEqual(manager._worker_thread, first_thread)

        manager.shutdown(timeout=1.0)

    def test_shutdown_stops_worker_thread(self):
        """Test that shutdown() stops the worker thread."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        manager.start()
        self.assertTrue(manager.is_running())

        manager.shutdown(timeout=2.0)

        self.assertFalse(manager.is_running())
        self.assertTrue(manager._shutdown_event.is_set())

    def test_shutdown_when_not_running(self):
        """Test that shutdown() handles case when not running."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        # Should not raise exception
        manager.shutdown(timeout=1.0)

    def test_shutdown_timeout(self):
        """Test shutdown with timeout on busy worker."""

        def slow_tts(text):
            time.sleep(10)  # Very slow

        manager = AudioQueueManager(slow_tts)
        manager.start()
        manager.enqueue("Slow message")

        # Give worker time to start processing
        time.sleep(0.1)

        # Shutdown with short timeout
        manager.shutdown(timeout=0.5)

        # Worker might still be alive due to timeout
        # Just verify shutdown was attempted
        self.assertTrue(manager._shutdown_event.is_set())


class TestAudioQueueManagerEnqueue(unittest.TestCase):
    """Test cases for enqueueing messages."""

    def test_enqueue_valid_message(self):
        """Test enqueueing a valid message."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        result = manager.enqueue("Hello world")

        self.assertTrue(result)
        stats = manager.get_stats()
        self.assertEqual(stats["messages_queued"], 1)

    def test_enqueue_with_priority(self):
        """Test enqueueing with custom priority."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        result = manager.enqueue("Urgent", priority=10)

        self.assertTrue(result)

    def test_enqueue_empty_text_rejected(self):
        """Test that empty text is rejected."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        self.assertFalse(manager.enqueue(""))
        self.assertFalse(manager.enqueue("   "))

        stats = manager.get_stats()
        self.assertEqual(stats["messages_queued"], 0)

    def test_enqueue_duplicate_detection(self):
        """Test that duplicate messages are detected."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts, duplicate_timeout=1.0)

        # First message should succeed
        self.assertTrue(manager.enqueue("Duplicate test"))

        # Immediate duplicate should be rejected
        self.assertFalse(manager.enqueue("Duplicate test"))

        stats = manager.get_stats()
        self.assertEqual(stats["messages_queued"], 1)
        self.assertEqual(stats["messages_skipped_duplicate"], 1)

    def test_enqueue_duplicate_after_timeout(self):
        """Test that duplicates are allowed after timeout."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts, duplicate_timeout=0.2)

        # First message
        self.assertTrue(manager.enqueue("Timeout test"))

        # Wait for timeout
        time.sleep(0.3)

        # Should be allowed now
        self.assertTrue(manager.enqueue("Timeout test"))

        stats = manager.get_stats()
        self.assertEqual(stats["messages_queued"], 2)

    def test_enqueue_queue_full(self):
        """Test behavior when queue is full."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts, max_queue_size=2)

        # Fill the queue
        self.assertTrue(manager.enqueue("Message 1"))
        self.assertTrue(manager.enqueue("Message 2"))

        # Next message should fail (queue full)
        self.assertFalse(manager.enqueue("Message 3"))

        stats = manager.get_stats()
        self.assertEqual(stats["messages_queued"], 2)
        self.assertEqual(stats["messages_skipped_full"], 1)


class TestAudioQueueManagerPlayback(unittest.TestCase):
    """Test cases for audio playback."""

    def test_worker_processes_messages(self):
        """Test that worker processes queued messages."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)
        manager.start()

        manager.enqueue("Test message")

        # Wait for processing
        time.sleep(0.3)

        mock_tts.assert_called_once_with("Test message")

        stats = manager.get_stats()
        self.assertEqual(stats["messages_played"], 1)

        manager.shutdown(timeout=1.0)

    def test_worker_processes_priority_order(self):
        """Test that messages are processed in priority order."""
        processed_order = []

        def record_tts(text):
            processed_order.append(text)

        manager = AudioQueueManager(record_tts)
        manager.start()

        # Queue messages with different priorities
        manager.enqueue("Low priority", priority=1)
        manager.enqueue("High priority", priority=10)
        manager.enqueue("Medium priority", priority=5)

        # Wait for all to process
        time.sleep(0.5)

        # High priority should be first
        self.assertEqual(processed_order[0], "High priority")

        manager.shutdown(timeout=1.0)

    def test_worker_handles_tts_error(self):
        """Test that worker handles TTS errors gracefully."""

        def failing_tts(text):
            raise Exception("TTS failed")

        manager = AudioQueueManager(failing_tts)
        manager.start()

        manager.enqueue("Will fail")

        # Wait for processing
        time.sleep(0.3)

        # Should not crash, error should be logged
        stats = manager.get_stats()
        self.assertEqual(stats["errors"], 1)

        manager.shutdown(timeout=1.0)

    def test_multiple_messages_sequential(self):
        """Test that multiple messages are processed sequentially."""
        call_count = []

        def counting_tts(text):
            call_count.append(text)
            time.sleep(0.1)  # Simulate processing time

        manager = AudioQueueManager(counting_tts)
        manager.start()

        manager.enqueue("Message 1")
        manager.enqueue("Message 2")
        manager.enqueue("Message 3")

        # Wait for all to process
        time.sleep(0.6)

        self.assertEqual(len(call_count), 3)
        self.assertEqual(call_count, ["Message 1", "Message 2", "Message 3"])

        manager.shutdown(timeout=1.0)


class TestAudioQueueManagerClearQueue(unittest.TestCase):
    """Test cases for clearing the queue."""

    def test_clear_queue_removes_all(self):
        """Test that clear_queue removes all pending messages."""
        mock_tts = Mock(side_effect=lambda text: time.sleep(0.5))  # Slow TTS
        manager = AudioQueueManager(mock_tts)
        manager.start()

        # Queue several messages
        manager.enqueue("Message 1")
        manager.enqueue("Message 2")
        manager.enqueue("Message 3")

        # Give first message time to start processing
        time.sleep(0.1)

        # Clear remaining queue
        manager.clear_queue()

        # Wait and verify only first message was processed
        time.sleep(0.7)

        # Should have called TTS only once (first message already started)
        self.assertEqual(mock_tts.call_count, 1)

        manager.shutdown(timeout=1.0)

    def test_clear_empty_queue(self):
        """Test clearing an already empty queue."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        # Should not raise exception
        manager.clear_queue()


class TestAudioQueueManagerStatistics(unittest.TestCase):
    """Test cases for statistics tracking."""

    def test_get_stats_returns_copy(self):
        """Test that get_stats returns a copy of stats."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)

        stats1 = manager.get_stats()
        stats1["messages_queued"] = 999

        stats2 = manager.get_stats()

        # Original should not be modified
        self.assertEqual(stats2["messages_queued"], 0)

    def test_statistics_accuracy(self):
        """Test that statistics are accurately tracked."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts, duplicate_timeout=1.0)
        manager.start()

        # Queue some messages
        manager.enqueue("Message 1")
        manager.enqueue("Message 2")
        manager.enqueue("Message 1")  # Duplicate

        # Wait for processing
        time.sleep(0.4)

        stats = manager.get_stats()

        self.assertEqual(stats["messages_queued"], 2)
        self.assertEqual(stats["messages_skipped_duplicate"], 1)
        self.assertEqual(stats["messages_played"], 2)

        manager.shutdown(timeout=1.0)


class TestAudioQueueManagerRecentMessages(unittest.TestCase):
    """Test cases for recent messages tracking."""

    def test_recent_messages_cleanup(self):
        """Test that old messages are cleaned up."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts, duplicate_timeout=0.2)

        # Add many messages to trigger cleanup
        for i in range(150):
            manager.enqueue(f"Message {i}")

        # Check that recent_messages dict is kept small
        self.assertLessEqual(len(manager._recent_messages), 100)

    def test_is_duplicate_check(self):
        """Test duplicate detection logic."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts, duplicate_timeout=1.0)

        manager._track_message("Test message")

        # Should be duplicate within timeout
        self.assertTrue(manager._is_duplicate("Test message"))

        # Different message should not be duplicate
        self.assertFalse(manager._is_duplicate("Other message"))


class TestAudioQueueManagerLogging(unittest.TestCase):
    """Test cases for logging functionality."""

    @patch("text2speech.audio_queue.logging.getLogger")
    def test_uses_provided_logger(self, mock_get_logger):
        """Test that provided logger is used."""
        mock_tts = Mock()
        custom_logger = Mock(spec=logging.Logger)

        manager = AudioQueueManager(mock_tts, logger=custom_logger)

        self.assertEqual(manager._logger, custom_logger)

    @patch("text2speech.audio_queue.logging.getLogger")
    def test_creates_logger_if_none(self, mock_get_logger):
        """Test that logger is created if none provided."""
        mock_tts = Mock()

        AudioQueueManager(mock_tts)

        mock_get_logger.assert_called_once()

    def test_log_statistics_on_shutdown(self):
        """Test that statistics are logged on shutdown."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)
        manager.start()

        with patch.object(manager._logger, "info") as mock_info:
            manager.shutdown(timeout=1.0)

            # Should have logged statistics
            self.assertTrue(any("Stats" in str(call) for call in mock_info.call_args_list))


class TestAudioQueueManagerEdgeCases(unittest.TestCase):
    """Test cases for edge cases and boundary conditions."""

    def test_worker_thread_name(self):
        """Test that worker thread has proper name."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)
        manager.start()

        self.assertEqual(manager._worker_thread.name, "AudioQueueWorker")

        manager.shutdown(timeout=1.0)

    def test_worker_thread_is_daemon(self):
        """Test that worker thread is daemon."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)
        manager.start()

        self.assertTrue(manager._worker_thread.daemon)

        manager.shutdown(timeout=1.0)

    def test_concurrent_enqueue(self):
        """Test concurrent enqueueing from multiple threads."""
        mock_tts = Mock()
        manager = AudioQueueManager(mock_tts)
        manager.start()

        def enqueue_many():
            for i in range(10):
                manager.enqueue(f"Thread message {i}")

        threads = [threading.Thread(target=enqueue_many) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = manager.get_stats()
        # Should have queued 30 messages total (or some may be duplicates)
        self.assertGreater(stats["messages_queued"], 0)

        manager.shutdown(timeout=2.0)

    def test_zero_priority_messages(self):
        """Test that zero priority messages work correctly."""
        processed = []

        def record_tts(text):
            processed.append(text)

        manager = AudioQueueManager(record_tts)
        manager.start()

        manager.enqueue("Zero priority", priority=0)

        time.sleep(0.3)

        self.assertEqual(processed, ["Zero priority"])

        manager.shutdown(timeout=1.0)


if __name__ == "__main__":
    unittest.main()
