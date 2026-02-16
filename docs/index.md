# text2speech Dokumentation

Willkommen zur Dokumentation des text2speech-Moduls. Dieses Modul bietet Text-to-Speech-Funktionalität (TTS) unter Verwendung des Kokoro-82M-Modells mit einem fortschrittlichen, thread-sicheren Audio-Queue-Management.

---

## Übersicht

Das **text2speech**-Modul wurde entwickelt, um eine robuste und einfach zu bedienende Sprachsynthese für Robotik-Anwendungen und andere Python-Projekte bereitzustellen.

### Hauptmerkmale

- ✅ **Thread-sichere Audio-Queue** - Verhindert ALSA/PortAudio-Konflikte durch serialisierte Wiedergabe.
- ✅ **Hochwertige Synthese** - Verwendet das Kokoro-82M-Modell für natürlich klingende Stimmen.
- ✅ **Prioritätsbasierte Steuerung** - Dringende Nachrichten unterbrechen normale Nachrichten.
- ✅ **Duplikaterkennung** - Vermeidet die Wiederholung identischer Nachrichten in kurzen Abständen.
- ✅ **Flexibles Konfigurationssystem** - YAML-basierte Einstellungen für Audio, Stimmen und Leistung.
- ✅ **Mehrsprachig** - Unterstützung für verschiedene Akzente und Sprachen.

---

## Schnellzugriff

| Bereich | Beschreibung |
|---------|--------------|
| [🚀 Erste Schritte](getting-started.md) | Schneller Einstieg in die Nutzung |
| [📦 Installation](installation.md) | Systemanforderungen und Setup |
| [⚙️ Konfiguration](configuration.md) | Anpassung der Bibliothek |
| [📚 API-Referenz](api/core.md) | Detaillierte technische Dokumentation |
| [🏗️ Architektur](architecture/index.md) | Einblick in die interne Funktionsweise |

---

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Details finden Sie in der [LICENSE](https://github.com/dgaida/text2speech/blob/master/LICENSE)-Datei.
