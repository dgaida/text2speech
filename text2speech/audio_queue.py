# text2speech/audio_queue.py
"""
Thread-safe audio queue manager for text2speech module.

Prevents ALSA/PortAudio device conflicts by serializing audio playback.
"""

import threading
import queue
import logging
import time
from typing import Optional, Callable, Dict
from dataclasses import dataclass
from types import MappingProxyType
from cachetools import TTLCache

from .constants import MAX_RECENT_MESSAGES


@dataclass
class AudioTask:
    """Represents a single TTS task."""

    text: str
    priority: int = 0  # Higher = more urgent
    timestamp: Optional[float] = None

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()

    def __lt__(self, other: "AudioTask") -> bool:
        """Compare tasks by priority (for PriorityQueue)."""
        # Inverted priority (higher priority value = processed first)
        if self.priority != other.priority:
            return self.priority > other.priority
        # If same priority, older message first
        if self.timestamp is not None and other.timestamp is not None:
            return self.timestamp < other.timestamp
        return False


class AudioQueueManager:
    """Thread-safe audio queue manager that serializes TTS playback.

    Features:
        - Single worker thread for sequential audio playback
        - Priority queue for urgent messages
        - Automatic cleanup on shutdown
        - Skip duplicate messages within timeout
        - Non-blocking queueing
    """

    def __init__(
        self,
        tts_callable: Callable[[str], None],
        max_queue_size: int = 50,
        duplicate_timeout: float = 2.0,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the audio queue manager.

        Args:
            tts_callable: Synchronous function that performs TTS (blocks until done).
            max_queue_size: Maximum queued messages (older discarded if full).
            duplicate_timeout: Skip duplicate messages within this window (seconds).
            logger: Optional logger instance (creates one if None).
        """
        self._tts_callable: Callable[[str], None] = tts_callable
        self._max_queue_size: int = max_queue_size
        self._duplicate_timeout: float = duplicate_timeout

        # Logging
        self._logger: logging.Logger = logger or logging.getLogger(__name__)

        # Priority queue (uses __lt__ from AudioTask for ordering)
        self._queue: queue.PriorityQueue[AudioTask] = queue.PriorityQueue(maxsize=max_queue_size)

        # Worker thread
        self._worker_thread: Optional[threading.Thread] = None
        self._shutdown_event: threading.Event = threading.Event()

        # Recent messages tracking (for duplicate detection) using TTL cache
        self._recent_messages: TTLCache[str, float] = TTLCache(maxsize=MAX_RECENT_MESSAGES, ttl=duplicate_timeout)
        self._recent_lock: threading.Lock = threading.Lock()

        # Statistics
        self._stats: Dict[str, int] = {
            "messages_queued": 0,
            "messages_played": 0,
            "messages_skipped_duplicate": 0,
            "messages_skipped_full": 0,
            "errors": 0,
        }
        self._stats_lock: threading.Lock = threading.Lock()

    def start(self) -> None:
        """Start the worker thread."""
        if self._worker_thread is not None and self._worker_thread.is_alive():
            self._logger.warning("Worker thread already running")
            return

        self._shutdown_event.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="AudioQueueWorker")
        self._worker_thread.start()
        self._logger.debug("Audio queue manager started")

    def shutdown(self, timeout: float = 5.0) -> None:
        """Stop the worker thread and wait for completion.

        Args:
            timeout: Maximum seconds to wait for shutdown.
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
        """Queue a message for audio playback (non-blocking).

        Args:
            text: Message to speak.
            priority: Priority (higher = more urgent, range 0-100).

        Returns:
            bool: True if queued successfully, False if skipped/failed.
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

    def clear_queue(self) -> None:
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

    def get_stats(self) -> MappingProxyType[str, int]:
        """Get playback statistics."""
        with self._stats_lock:
            return MappingProxyType(self._stats.copy())

    def is_running(self) -> bool:
        """Check if worker thread is active."""
        return self._worker_thread is not None and self._worker_thread.is_alive()

    # Private methods

    def _worker_loop(self) -> None:
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

    def _play_audio(self, text: str) -> None:
        """Play audio using TTS callable.

        Args:
            text: Message to speak.
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
            # TTL cache handles expiration automatically
            return text in self._recent_messages

    def _track_message(self, text: str) -> None:
        """Track message to detect duplicates."""
        with self._recent_lock:
            # TTL cache handles size and expiration automatically
            self._recent_messages[text] = time.time()

    def _log_statistics(self) -> None:
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
