# Erste Schritte

In diesem Leitfaden erfahren Sie, wie Sie das `text2speech`-Modul schnell in Ihr Projekt integrieren.

## Grundlegende Verwendung

Die einfachste Art, `text2speech` zu nutzen, ist über die `Text2Speech`-Klasse. Standardmäßig ist die Audio-Warteschlange (Queue) aktiviert, was eine nicht-blockierende Ausführung ermöglicht.

```python
from text2speech import Text2Speech

# Initialisierung des TTS-Systems
tts = Text2Speech()

# Nachrichten in die Warteschlange stellen (nicht-blockierend)
tts.speak("Hallo, ich bin bereit für den Einsatz!")
tts.speak("Diese Nachricht wird nach der ersten abgespielt.")

# System ordnungsgemäß herunterfahren
tts.shutdown()
```

## Prioritäten und Blockierung

Sie können die Priorität von Nachrichten steuern und entscheiden, ob der Aufruf warten soll, bis die Sprache ausgegeben wurde.

```python
# Eine Nachricht mit hoher Priorität
tts.speak("Achtung: Kritischer Fehler!", priority=10)

# Blockierender Aufruf (wartet bis die Nachricht fertig gesprochen wurde)
tts.speak("Bitte warten Sie auf diese Durchsage.", blocking=True)
print("Nachricht beendet!")
```

## Stimmen und Lautstärke anpassen

Sie können die Stimme, Geschwindigkeit und Lautstärke zur Laufzeit ändern.

```python
# Stimme auf einen männlichen Sprecher ändern
tts.set_voice("am_adam")

# Geschwindigkeit erhöhen (0.5 bis 2.0)
tts.set_speed(1.2)

# Lautstärke anpassen (0.0 bis 1.0)
tts.set_volume(0.9)

tts.speak("Ich spreche jetzt mit einer anderen Stimme.")
```

## Verwendung als Kontextmanager

Für ein automatisches Ressourcenmanagement wird die Verwendung als Kontextmanager empfohlen.

```python
from text2speech import Text2Speech

with Text2Speech() as tts:
    tts.speak("Automatisches Herunterfahren nach diesem Block.")
```

## Kommandozeilenschnittstelle (CLI)

Sie können die Bibliothek auch direkt über das Terminal verwenden:

```bash
text2speech "Hallo von der Kommandozeile" --voice af_nicole
```
