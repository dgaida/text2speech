# Fortgeschrittene Nutzung

Hier werden komplexe Szenarien wie das Management der Audio-Warteschlange, Prioritäten und die Verwendung mehrerer Instanzen behandelt.

## Prioritätssteuerung

Dringende Nachrichten können andere Nachrichten in der Warteschlange überholen.

```python
from text2speech import Text2Speech

tts = Text2Speech()

# Normale Nachrichten
tts.speak("Nachricht 1")
tts.speak("Nachricht 2")

# Nachricht mit hoher Priorität (wird als nächstes abgespielt)
tts.speak("Achtung: Batterie schwach!", priority=10)

tts.shutdown()
```

## Audio-Warteschlangen-Statistiken

Sie können den Status der Warteschlange überwachen, um zu sehen, wie viele Nachrichten verarbeitet wurden.

```python
stats = tts.get_queue_stats()
print(stats)
# {
#     'messages_queued': 3,
#     'messages_played': 1,
#     'messages_skipped_duplicate': 0,
#     'messages_skipped_full': 0,
#     'errors': 0
# }
```

## Duplikaterkennung

Der `AudioQueueManager` kann identische Nachrichten innerhalb eines Zeitfensters automatisch überspringen, um Redundanz zu vermeiden.

```python
from text2speech import Text2Speech

tts = Text2Speech(
    duplicate_timeout=5.0  # 5 Sekunden Fenster für Duplikate
)

tts.speak("System bereit")
tts.speak("System bereit")  # Wird übersprungen, wenn innerhalb von 5 Sek.
```

## Mehrere TTS-Instanzen

Sie können verschiedene Instanzen mit unterschiedlichen Konfigurationen verwenden, z.B. für verschiedene Rollen oder Sprecher.

```python
from text2speech import Text2Speech

# Roboter-Stimme
robot_tts = Text2Speech()
robot_tts.set_voice("am_adam")
robot_tts.set_speed(1.1)

# Erzähler-Stimme
narrator_tts = Text2Speech()
narrator_tts.set_voice("bf_emma")

robot_tts.speak("Ich bin ein Roboter.")
narrator_tts.speak("Der Erzähler beginnt die Geschichte.")

robot_tts.shutdown()
narrator_tts.shutdown()
```

## Legacy-Modus (Ohne Warteschlange)

Für Anwendungen, die das alte Threading-Modell benötigen:

```python
# Deaktiviert die Warteschlange
tts = Text2Speech(enable_queue=False)

# Startet einen separaten Thread für die Wiedergabe
thread = tts.call_text2speech_async("Hallo Welt")
thread.join()
```

## Beispiele ausführen

Im Verzeichnis `examples/` finden Sie die Datei `demo.py`, die verschiedene Szenarien demonstriert:

```bash
# Alle Beispiele nacheinander ausführen
python examples/demo.py

# Interaktiver Modus
python examples/demo.py --interactive
```
