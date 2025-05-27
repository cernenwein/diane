import sounddevice as sd
import soundfile as sf

filename = "mic_test.wav"
duration = 5  # seconds
samplerate = 16000
channels = 1

print("Recording from microphone for 5 seconds...")
recording = sd.rec(int(duration * samplerate), samplerate=samplerate,
                   channels=channels, dtype='float32')
sd.wait()
sf.write(filename, recording, samplerate)
print(f"Recording complete. Saved to {filename}")

print("Playing back the recorded audio...")
data, fs = sf.read(filename, dtype='float32')
sd.play(data, samplerate=fs)
sd.wait()
print("Playback complete.")
