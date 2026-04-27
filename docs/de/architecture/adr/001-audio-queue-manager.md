# ADR-001: Audio Queue Manager

## Status
Akzeptiert

## Kontext
Benutzer meldeten ALSA/PortAudio-Fehler ("device busy"), wenn mehrere TTS-Anfragen gleichzeitig auftraten. Dies geschah, weil mehrere Threads versuchten, gleichzeitig auf die Audio-Hardware zuzugreifen.

## Entscheidung
Implementierung eines `AudioQueueManager`, um die Audiowiedergabe in einem einzigen Worker-Thread zu serialisieren. Alle TTS-Anfragen werden in eine Warteschlange gestellt (mit Prioritätsunterstützung) und nacheinander verarbeitet.

## Konsequenzen  
- **Positiv**: Eliminiert Gerätekonflikte, fügt Prioritätsunterstützung hinzu, verhindert die Erschöpfung von Systemressourcen durch übermäßiges Threading.  
- **Negativ**: Leicht erhöhte Latenz bei gleichzeitigen Anfragen, da diese warten müssen, bis vorherige abgeschlossen sind.  
- **Neutral**: Wird zum Standardverhalten, was eine Migration für Benutzer erforderlich macht, die sich auf eine gleichzeitige (und potenziell konfliktreiche) Wiedergabe verlassen haben.  
