# text2speech/audio_queue.py
"""
Thread-safe audio queue manager for text2speech module.

Prevents ALSA/PortAudio device conflicts by serializing audio playback.
"""

import threading
import queue
import logging
import time
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class AudioTask:
    """Represents a single TTS task."""

    text: str
    priority: int = 0  # Higher = more urgent
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def __lt__(self, other):
        """Compare tasks by priority (for PriorityQueue)."""
        # Inverted priority (higher priority value = processed first)
        if self.priority != other.priority:
            return self.priority > other.priority
        # If same priority, older message first
        return self.timestamp < other.timestamp


class AudioQueueManager:
    """
    Thread-safe audio queue manager that serializes TTS playback.

    Features:
    - Single worker thread for sequential audio playback
    - Priority queue for urgent messages
    - Automatic cleanup on shutdown
    - Skip duplicate messages within timeout
    - Non-blocking queueing

    Example:
        from text2speech.audio_queue import AudioQueueManager

        def my_tts_function(text):
            # Your TTS code here
            pass

        manager = AudioQueueManager(my_tts_function)
        manager.start()

        # Queue audio (non-blocking)
        manager.enqueue("Hello world", priority=5)
        manager.enqueue("High priority!", priority=10)

        # Cleanup when done
        manager.shutdown()
    """

    def __init__(
        self,
        tts_callable: Callable[[str], None],
        max_queue_size: int = 50,
        duplicate_timeout: float = 2.0,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the audio queue manager.

        Args:
            tts_callable: Synchronous function that performs TTS (blocks until done)
            max_queue_size: Maximum queued messages (older discarded if full)
            duplicate_timeout: Skip duplicate messages within this window (seconds)
            logger: Optional logger instance (creates one if None)
        """
        self._tts_callable = tts_callable
        self._max_queue_size = max_queue_size
        self._duplicate_timeout = duplicate_timeout

        # Logging
        self._logger = logger or logging.getLogger(__name__)

        # Priority queue (uses __lt__ from AudioTask for ordering)
        self._queue = queue.PriorityQueue(maxsize=max_queue_size)

        # Worker thread
        self._worker_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Recent messages tracking (for duplicate detection)
        self._recent_messages = {}  # {text: timestamp}
        self._recent_lock = threading.Lock()

        # Statistics
        self._stats = {
            "messages_queued": 0,
            "messages_played": 0,
            "messages_skipped_duplicate": 0,
            "messages_skipped_full": 0,
            "errors": 0,
        }
        self._stats_lock = threading.Lock()

    def start(self):
        """Start the worker thread."""
        if self._worker_thread is not None and self._worker_thread.is_alive():
            self._logger.warning("Worker thread already running")
            return

        self._shutdown_event.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="AudioQueueWorker")
        self._worker_thread.start()
        self._logger.debug("Audio queue manager started")

    def shutdown(self, timeout: float = 5.0):
        """
        Stop the worker thread and wait for completion.

        Args:
            timeout: Maximum seconds to wait for shutdown
        """
        if self._worker_thread is None:
            return

        self._logger.debug("Shutting down audio queue manager...")
        self._shutdown_event.set()

        # Signal queue to unblock
        try:
            # Add a sentinel task to wake up worker
            self._queue.put_nowait(AudioTask("", priority=-1000))
        except queue.Full:
            pass

        self._worker_thread.join(timeout=timeout)

        if self._worker_thread.is_alive():
            self._logger.warning("Worker thread did not shut down cleanly")
        else:
            self._logger.debug("Audio queue manager shut down successfully")

        # Log final stats
        self._log_statistics()

    def enqueue(self, text: str, priority: int = 0) -> bool:
        """
        Queue a message for audio playback (non-blocking).

        Args:
            text: Message to speak
            priority: Priority (higher = more urgent, range 0-100)

        Returns:
            True if queued successfully, False if skipped/failed
        """
        if not text or not text.strip():
            return False

        # Check for duplicates
        if self._is_duplicate(text):
            with self._stats_lock:
                self._stats["messages_skipped_duplicate"] += 1
            self._logger.debug(f"Skipped duplicate: {text[:50]}")
            return False

        # Create task
        task = AudioTask(text=text, priority=priority)

        # Try to queue (non-blocking)
        try:
            self._queue.put_nowait(task)

            with self._stats_lock:
                self._stats["messages_queued"] += 1

            # Track recent message
            self._track_message(text)

            self._logger.debug(f"Queued (priority={priority}): {text[:50]}")
            return True

        except queue.Full:
            # Queue full - log and skip
            with self._stats_lock:
                self._stats["messages_skipped_full"] += 1
            self._logger.warning(f"Queue full, skipped: {text[:50]}")
            return False

    def clear_queue(self):
        """Clear all pending messages from queue."""
        cleared = 0
        try:
            while True:
                self._queue.get_nowait()
                cleared += 1
        except queue.Empty:
            pass

        if cleared > 0:
            self._logger.info(f"Cleared {cleared} messages from queue")

    def get_stats(self) -> dict:
        """Get playback statistics."""
        with self._stats_lock:
            return self._stats.copy()

    def is_running(self) -> bool:
        """Check if worker thread is active."""
        return self._worker_thread is not None and self._worker_thread.is_alive()

    # Private methods

    def _worker_loop(self):
        """Worker thread main loop."""
        self._logger.debug("Worker thread started")

        while not self._shutdown_event.is_set():
            try:
                # Get next task (blocking with timeout)
                task = self._queue.get(timeout=1.0)

                # Check if shutdown signal or sentinel
                if self._shutdown_event.is_set() or task.priority == -1000:
                    self._queue.task_done()
                    break

                # Play audio (blocking)
                self._play_audio(task.text)

                # Mark task as done
                self._queue.task_done()

            except queue.Empty:
                # Timeout - check shutdown flag and continue
                continue
            except Exception as e:
                self._logger.error(f"Worker error: {e}", exc_info=True)
                with self._stats_lock:
                    self._stats["errors"] += 1

        self._logger.debug("Worker thread exiting")

    def _play_audio(self, text: str):
        """
        Play audio using TTS callable.

        Args:
            text: Message to speak
        """
        try:
            self._logger.debug(f"Playing: {text[:50]}")

            # Call TTS function (blocking)
            self._tts_callable(text)

            with self._stats_lock:
                self._stats["messages_played"] += 1

            self._logger.debug("Playback complete")

        except Exception as e:
            self._logger.error(f"TTS error: {e}", exc_info=True)
            with self._stats_lock:
                self._stats["errors"] += 1

    def _is_duplicate(self, text: str) -> bool:
        """Check if message is a recent duplicate."""
        with self._recent_lock:
            if text in self._recent_messages:
                last_time = self._recent_messages[text]
                if time.time() - last_time < self._duplicate_timeout:
                    return True
        return False

    def _track_message(self, text: str):
        """Track message to detect duplicates."""
        with self._recent_lock:
            current_time = time.time()

            # Add/update message
            self._recent_messages[text] = current_time

            # Cleanup old messages (keep dict small)
            if len(self._recent_messages) > 100:
                cutoff_time = current_time - self._duplicate_timeout
                self._recent_messages = {msg: ts for msg, ts in self._recent_messages.items() if ts > cutoff_time}

    def _log_statistics(self):
        """Log playback statistics."""
        stats = self.get_stats()
        self._logger.info(
            f"Audio Queue Stats: "
            f"queued={stats['messages_queued']}, "
            f"played={stats['messages_played']}, "
            f"skipped_dup={stats['messages_skipped_duplicate']}, "
            f"skipped_full={stats['messages_skipped_full']}, "
            f"errors={stats['errors']}"
        )
