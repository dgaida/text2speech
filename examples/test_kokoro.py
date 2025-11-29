# source: https://aleksandarhaber.com/kokoro-82m-install-and-run-locally-fast-small-and-free-text-to-speech-tts-ai-model-kokoro-82m/

from kokoro import KPipeline

# import soundfile as sf
import sounddevice as sd

# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
pipeline = KPipeline(lang_code="a")  # <= make sure lang_code matches voice

# This text is for demonstration purposes only, unseen during training
text = """
In this tutorial, we explain how to download, install, and run locally
Kokoro on Windows computer. Kokoro is an open-weight text to speech model
or briefly TTS model. Its main advantages is that it is lightweight,
however, at the same time it delivers comparably quality to larger models.
Due to its relatively small number of parameters it is faster and
more cost-efficient than larger models.
In this tutorial, we will thoroughly explain all the steps you
need to perform in order to run the model.
In a practical application, you would use this model to develop
a personal AI assistant, or to enable a computer to communicate with humans.
"""

# af_nicole
generator = pipeline(text, voice="af_heart", speed=1, split_pattern=r"\n+")  # 'af_nicole', #

for i, (gs, ps, audio) in enumerate(generator):
    print(i)  # i => index
    print(gs)  # gs => graphemes/text
    print(ps)  # ps => phonemes
    sd.play(audio.cpu().numpy(), samplerate=24000)
    sd.wait()  # Warten, bis die Wiedergabe abgeschlossen ist
    # sf.write(f'{i}.wav', 24000, audio.cpu().numpy()) # save each audio file
