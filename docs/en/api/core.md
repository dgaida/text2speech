# Core API

This page contains the reference for the core components of `text2speech`.

## Text2Speech

::: text2speech.text2speech.Text2Speech
    options:
      members:
        - __init__
        - speak
        - speak_sync
        - set_voice
        - set_speed
        - set_volume
        - shutdown
        - get_available_devices
        - get_queue_stats

## AudioQueueManager

::: text2speech.audio_queue.AudioQueueManager
    options:
      members:
        - __init__
        - start
        - shutdown
        - enqueue
        - clear_queue
        - get_stats
        - is_running

## Config

::: text2speech.config.Config
    options:
      members:
        - __init__
        - load_from_file
        - get
        - set
        - save_to_file
        - audio_output_device
        - audio_volume
        - sample_rate
