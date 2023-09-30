
from vosk import KaldiRecognizer , Model
import pyaudio

english_model = Model(model_name="vosk-model-small-en-us-0.15")
english_recognizer = KaldiRecognizer(english_model , 16000)

fil_model = Model(model_name="vosk-model-tl-ph-generic-0.6")
fil_recognizer = KaldiRecognizer(fil_model, 16000)

mic = pyaudio.PyAudio()

stream = mic.open(format=pyaudio.paInt16 , channels=1 , rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

while True:
    data = stream.read(4096)
    if english_recognizer.AcceptWaveform(data):
        trans = english_recognizer.Result()
        print(f"English Result: {trans[14:-3]}")
    if fil_recognizer.AcceptWaveform(data):
        trans = fil_recognizer.Result()
        print(f"Filipino Result: {trans}")
    print("None ========================")