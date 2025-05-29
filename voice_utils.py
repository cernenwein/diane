import subprocess
import sounddevice as sd
import soundfile as sf
from queue import Queue
import os

AUDIO_OUTPUT_PATH = "/tmp/diane_output.wav"

def speak_text(text):
    subprocess.run([
        "piper", 
        "--model", "/opt/diane/piper/en_US-amy-low.onnx", 
        "--output_file", AUDIO_OUTPUT_PATH
    ], input=text.encode(), check=True)
    subprocess.run(["aplay", AUDIO_OUTPUT_PATH])

def record_voice(duration=4, filename="/tmp/diane_input.wav"):
    q = Queue()
    def callback(indata, frames, time, status):
        q.put(indata.copy())
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        with sf.SoundFile(filename, mode='x', samplerate=16000, channels=1, subtype='PCM_16') as file:
            for _ in range(0, int(16000 / 8000 * duration)):
                file.write(q.get())

def wait_for_wake_word():
    while True:
        text = input("Say something (type 'Diane' to trigger): ").lower()
        if "diane" in text:
            return
