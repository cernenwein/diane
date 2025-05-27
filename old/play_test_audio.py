import sounddevice as sd
import soundfile as sf

filename = 'test.wav'

print(f"Playing {filename}...")
data, fs = sf.read(filename, dtype='float32')
sd.play(data, samplerate=fs)
sd.wait()
print("Playback complete.")
