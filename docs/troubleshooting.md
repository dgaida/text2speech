# Fehlerbehebung

Hier finden Sie Lösungen für häufig auftretende Probleme.

## Kein Audio-Ausgang

Wenn Sie keine Sprachausgabe hören:

1. **Geräte-Liste prüfen**:
   Führen Sie folgendes aus, um zu sehen, ob Ihr Gerät erkannt wird:
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
2. **Standardgerät testen**:
   Stellen Sie sicher, dass Ihr Betriebssystem das richtige Standard-Ausgabegerät ausgewählt hat.
3. **Konfiguration prüfen**:
   Überprüfen Sie in Ihrer `config.yaml`, ob `audio.output_device` auf die korrekte ID eingestellt ist oder auf `null` steht.
4. **Lautstärke**:
   Prüfen Sie `audio.default_volume` und die Systemlautstärke.

## ALSA/PortAudio Fehler (Linux)

Falls Fehler wie `ALSA lib pcm.c:8432:(snd_pcm_recover) underrun occurred` auftreten:

- Dies ist oft ein Zeichen für Ressourcenkonflikte. Stellen Sie sicher, dass Sie die `AudioQueueManager`-Funktionalität nutzen (standardmäßig aktiviert), die den Zugriff auf die Soundkarte serialisiert.
- Installieren Sie die notwendigen Bibliotheken: `sudo apt-get install libasound2-dev libportaudio2`.

## Kokoro-Modell lädt nicht

- **Internetverbindung**: Beim ersten Start wird das Modell von Hugging Face heruntergeladen. Stellen Sie eine Internetverbindung sicher.
- **Speicherplatz**: Stellen Sie sicher, dass genügend Festplattenplatz (~500MB) vorhanden ist.
- **PyTorch**: Falls CUDA-Fehler auftreten, prüfen Sie Ihre PyTorch-Installation:
  ```python
  import torch
  print(torch.cuda.is_available())
  ```
  Setzen Sie `performance.use_gpu: false` in der `config.yaml`, falls Sie keine kompatible GPU haben.

## Langsame Sprachsynthese

- **GPU nutzen**: Stellen Sie sicher, dass `use_gpu: true` konfiguriert ist und eine NVIDIA-GPU mit installierten Treibern vorhanden ist.
- **CPU-Threads**: Erhöhen Sie ggf. die Anzahl der Threads in der Konfiguration unter `performance.num_threads`.

## ElevenLabs Authentifizierungsfehler

- Stellen Sie sicher, dass Ihr API-Key mit `sk_` beginnt.
- Prüfen Sie Ihr Kontoguthaben bei ElevenLabs.
- ElevenLabs wird nur verwendet, wenn ein gültiger API-Key übergeben wurde und das Engine-Feld auf `elevenlabs` steht.
