# ADR-001: Audio Queue Manager

## Status
Accepted

## Context
Users reported "device busy" ALSA/PortAudio errors when multiple TTS requests occurred simultaneously. This happened because multiple threads attempted to access the audio hardware at the same time.

## Decision
Implement an `AudioQueueManager` to serialize audio playback on a single worker thread. All TTS requests are queued (with priority support) and processed sequentially.

## Consequences
- **Positive**: Eliminates device conflicts, adds priority support, prevents system resource exhaustion from excessive threading.
- **Negative**: Slightly increased latency for concurrent requests as they must wait for previous ones to finish.
- **Neutral**: Becomes the default behavior, requiring a migration for users who relied on simultaneous (and potentially conflicting) playback.
