#!/usr/bin/env python3

import os
import pvporcupine
import pyaudio
import struct
import subprocess

WAKE_WORD = "diane"
PIPER_VOICE = "/home/diane/piper/en_US-lessac-medium.onnx"
PIPER_COMMAND = "/usr/local/bin/piper"
AUDIO_OUTPUT_PATH = "/tmp/diane_output.wav"

def play_response_audio():
    if os.path.exists(AUDIO_OUTPUT_PATH):
        os.system(f"aplay {AUDIO_OUTPUT_PATH}")
    else:
        print("⚠️ Warning: No output audio to play (missing /tmp/diane_output.wav)")

def synthesize_speech(text):
    print(f"🗣️ Diane says: {text}")
    try:
        subprocess.run([PIPER_COMMAND, "--model", PIPER_VOICE, "--output_file", AUDIO_OUTPUT_PATH],
                       input=text.encode(), check=True)
    except Exception as e:
        print(f"❌ Piper synthesis error: {e}")

def main():
    print("🎤 Diane is running with Porcupine wake word detection...")
    porcupine = pvporcupine.create(keywords=[WAKE_WORD])

    pa = pyaudio.PyAudio()
    stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
                     input=True, frames_per_buffer=porcupine.frame_length)

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm_unpacked)
            if keyword_index >= 0:
                print(f"🎉 Wake word '{WAKE_WORD}' detected!")
                synthesize_speech("Yes, I’m listening.")
                play_response_audio()
    except KeyboardInterrupt:
        print("🛑 Stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == "__main__":
    main()
