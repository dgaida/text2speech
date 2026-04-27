# Grundlegende Nutzung

Hier erfahren Sie, wie Sie `text2speech` für einfache Aufgaben einsetzen.

## Einfache Sprachausgabe mit Queue (Empfohlen)

Standardmäßig ist die Audio-Warteschlange aktiviert, was eine nicht-blockierende Ausführung ermöglicht.

```python
from text2speech import Text2Speech

# Initialisierung des TTS-Systems (Queue standardmäßig aktiviert)
tts = Text2Speech(verbose=True)

# Nachrichten in die Warteschlange stellen (nicht-blockierend)
tts.speak("Hallo, ich bin bereit für den Einsatz!")
tts.speak("Diese Nachricht wird nach der ersten abgespielt.")

# System ordnungsgemäß herunterfahren
tts.shutdown()
```

## Blockierender Modus

Sie können erzwingen, dass das Programm wartet, bis die Sprache ausgegeben wurde.

```python
from text2speech import Text2Speech

tts = Text2Speech()

# Warten, bis die Nachricht fertig gesprochen wurde
tts.speak("Bitte warten Sie auf diese Nachricht.", blocking=True)
print("Nachricht beendet!")

tts.shutdown()
```

## Verwendung als Kontextmanager

Für ein automatisches Ressourcenmanagement wird die Verwendung als Kontextmanager empfohlen.

```python
from text2speech import Text2Speech

with Text2Speech() as tts:
    tts.speak("Automatisches Herunterfahren nach diesem Block.")
```

## Kommandozeilenschnittstelle (CLI)

Die Bibliothek bietet ein einfaches CLI-Tool für schnelle Tests oder zur Integration in Shell-Skripte.

```bash
# Grundlegende Nutzung
text2speech "Hallo Welt"

# Mit spezifischer Stimme
text2speech "Hallo" --voice am_adam

# Mit spezifischer Konfigurationsdatei
text2speech "Hallo" --config meine_config.yaml
```

## Laufzeit-Anpassungen

Sie können die Stimme, Geschwindigkeit und Lautstärke jederzeit ändern.

```python
tts = Text2Speech()

# Stimme ändern
tts.set_voice("am_adam")
tts.speak("Spreche mit Adams Stimme")

# Geschwindigkeit anpassen (0.5 bis 2.0)
tts.set_speed(1.2)

# Lautstärke anpassen (0.0 bis 1.0)
tts.set_volume(0.7)

tts.shutdown()
```
