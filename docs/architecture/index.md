# Architektur

Diese Seite beschreibt die interne Architektur von `text2speech`.

## Systemübersicht

Das System ist in mehrere Komponenten unterteilt, die zusammenarbeiten, um Text in Sprache umzuwandeln und diese sicher abzuspielen.

```mermaid
graph TD
    User([Benutzer/Anwendung]) --> T2S[Text2Speech]
    T2S --> Config[Config Manager]
    T2S --> AQM[Audio Queue Manager]
    AQM --> Worker[Worker Thread]
    Worker --> Engine{TTS Engine}
    Engine --> Kokoro[Kokoro Engine]
    Engine --> EL[ElevenLabs Engine]
    Kokoro --> Audio[Audio Daten]
    EL --> Audio
    Audio --> Proc[Audio Processing]
    Proc --> Playback[Sounddevice Playback]
```

## Datenfluss

Der Datenfluss folgt einer klaren Pipeline, um eine blockierungsfreie Verarbeitung zu ermöglichen.

```mermaid
sequenceDiagram
    participant App as Anwendung
    participant T2S as Text2Speech
    participant AQM as Audio Queue Manager
    participant Worker as Worker Thread
    participant Engine as TTS Engine
    participant Device as Audio Gerät

    App->>T2S: speak("Hallo", priority=5)
    T2S->>AQM: enqueue(task)
    AQM-->>T2S: Erfolg (bool)
    T2S-->>App: Rückgabe

    loop Worker Loop
        Worker->>AQM: get_task()
        AQM-->>Worker: task
        Worker->>Engine: synthesize(text)
        Engine-->>Worker: audio_tensor
        Worker->>Device: play(audio)
        Device-->>Worker: fertig
    end
```

## Komponentendetails

### Text2Speech
Die Haupt-Einstiegsklasse. Sie koordiniert die Initialisierung der Engines, lädt die Konfiguration und stellt die öffentliche API bereit.

### AudioQueueManager
Ein thread-sicherer Manager, der eine Prioritätswarteschlange verwendet. Er stellt sicher, dass Audio-Anfragen nacheinander verarbeitet werden, was besonders wichtig ist, um Hardware-Konflikte bei ALSA oder PortAudio zu vermeiden.

### TTS Engines
Wir unterstützen zwei Haupt-Backends:
1. **Kokoro Engine**: Lokal ausgeführtes, hocheffizientes Modell (82M Parameter).
2. **ElevenLabs Engine**: Cloud-basiertes Backend für High-End-Sprachsynthese (Legacy-Support).

### Audio Processing
Bevor die Audiodaten an die Hardware gesendet werden, durchlaufen sie eine Verarbeitungskette:
- **Resampling**: Anpassung an die vom Gerät unterstützte Abtastrate.
- **Normalisierung**: Anpassung der Lautstärke.
- **Clamping**: Verhindern von Übersteuerungen.
