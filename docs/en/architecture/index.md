# Architecture

This page describes the internal architecture of `text2speech`.

## System Overview

The system is divided into several components that work together to convert text to speech and play it safely.

```mermaid
graph TD
    User([User/Application]) --> T2S[Text2Speech]
    T2S --> Config[Config Manager]
    T2S --> AQM[Audio Queue Manager]
    AQM --> Worker[Worker Thread]
    Worker --> Engine{TTS Engine}
    Engine --> Kokoro[Kokoro Engine]
    Engine --> EL[ElevenLabs Engine]
    Kokoro --> Audio[Audio Data]
    EL --> Audio
    Audio --> Proc[Audio Processing]
    Proc --> Playback[Sounddevice Playback]
```

## Data Flow

The data flow follows a clear pipeline to enable non-blocking processing.

```mermaid
sequenceDiagram
    participant App as Application
    participant T2S as Text2Speech
    participant AQM as Audio Queue Manager
    participant Worker as Worker Thread
    participant Engine as TTS Engine
    participant Device as Audio Device

    App->>T2S: speak("Hello", priority=5)
    T2S->>AQM: enqueue(task)
    AQM-->>T2S: Success (bool)
    T2S-->>App: Return

    loop Worker Loop
        Worker->>AQM: get_task()
        AQM-->>Worker: task
        Worker->>Engine: synthesize(text)
        Engine-->>Worker: audio_tensor
        Worker->>Device: play(audio)
        Device-->>Worker: finished
    end
```

## Component Details

### Text2Speech
The main entry point class. It coordinates the initialization of engines, loads the configuration, and provides the public API.

### AudioQueueManager
A thread-safe manager that uses a priority queue. It ensures that audio requests are processed sequentially, which is particularly important for avoiding hardware conflicts with ALSA or PortAudio.

### TTS Engines
We support two main backends:
1. **Kokoro Engine**: Locally executed, highly efficient model (82M parameters).
2. **ElevenLabs Engine**: Cloud-based backend for high-end speech synthesis (legacy support).

### Audio Processing
Before the audio data is sent to the hardware, it passes through a processing chain:
- **Resampling**: Adjustment to the sample rate supported by the device.
- **Normalization**: Adjustment of the volume.
- **Clamping**: Prevention of clipping.
