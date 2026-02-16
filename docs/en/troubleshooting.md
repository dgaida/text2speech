# Troubleshooting

Here you can find solutions to common issues.

## No Audio Output

If you cannot hear any speech output:

1. **Check Device List**:
   Run the following to see if your device is detected:
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
2. **Test Default Device**:
   Ensure that your operating system has the correct default output device selected.
3. **Check Configuration**:
   Check your `config.yaml` to see if `audio.output_device` is set to the correct ID or to `null`.
4. **Volume**:
   Check `audio.default_volume` and the system volume.

## ALSA/PortAudio Errors (Linux)

If errors like `ALSA lib pcm.c:8432:(snd_pcm_recover) underrun occurred` occur:

- This is often a sign of resource conflicts. Ensure that you are using the `AudioQueueManager` functionality (enabled by default), which serializes access to the sound card.
- Install the necessary libraries: `sudo apt-get install libasound2-dev libportaudio2`.

## Kokoro Model Does Not Load

- **Internet Connection**: The model is downloaded from Hugging Face on the first start. Ensure you have an internet connection.
- **Disk Space**: Ensure there is enough disk space (~500MB) available.
- **PyTorch**: If CUDA errors occur, check your PyTorch installation:
  ```python
  import torch
  print(torch.cuda.is_available())
  ```
  Set `performance.use_gpu: false` in `config.yaml` if you do not have a compatible GPU.

## Slow Speech Synthesis

- **Use GPU**: Ensure that `use_gpu: true` is configured and that an NVIDIA GPU with installed drivers is available.
- **CPU Threads**: If necessary, increase the number of threads in the configuration under `performance.num_threads`.

## ElevenLabs Authentication Errors

- Ensure that your API key starts with `sk_`.
- Check your ElevenLabs account balance.
- ElevenLabs is only used if a valid API key is provided and the engine field is set to `elevenlabs`.
