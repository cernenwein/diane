#!/usr/bin/env python3

import os
import time
import json
import struct
import subprocess
import threading
from dotenv import load_dotenv
import pvporcupine
import pyaudio

# Load Porcupine Access Key securely
load_dotenv("/opt/diane/.env.porcupine")
ACCESS_KEY = os.getenv("ACCESS_KEY")
WAKE_WORD = "diane"

# Piper TTS model path and output
PIPER_COMMAND = "/usr/local/bin/piper"
PIPER_MODEL = "/home/diane/piper/en_US-lessac-medium.onnx"
AUDIO_OUTPUT = "/tmp/diane_output.wav"

# Optional: load slang, personality, and synonym system
PERSONALITY_FILE = "/opt/diane/diane_personality_profiles/default.json"
SLANG_TABLE = "/opt/diane/diane_core_knowledge/slang_map.json"
SYNONYM_TABLE = "/opt/diane/diane_core_knowledge/synonyms.json"
PROJECTS_DIR = "/opt/diane/diane_projects"
LOG_FILE = "/opt/diane/diane_logs/diane_voice.log"
RESPONSE_HISTORY = []

# Log helper
def log(msg):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as logf:
        logf.write(f"{ts} {msg}\n")
    print(msg)

def synthesize_speech(text):
    log(f"Diane says: {text}")
    try:
        result = subprocess.run(
            [PIPER_COMMAND, "--model", PIPER_MODEL, "--output_file", AUDIO_OUTPUT],
            input=text.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            subprocess.run(["aplay", AUDIO_OUTPUT])
        else:
            log("❌ Piper TTS failed.")
    except Exception as e:
        log(f"❌ Synthesis Error: {e}")

def handle_wake():
    synthesize_speech("Yes, I’m listening.")

def wake_loop():
    log("🎤 Diane is listening for wake word...")
    porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=[WAKE_WORD])
    pa = pyaudio.PyAudio()
    stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
                     input=True, frames_per_buffer=porcupine.frame_length)

    try:
        while True:
            frame = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, frame)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                log("🎉 Wake word detected!")
                handle_wake()
    except KeyboardInterrupt:
        log("🛑 Interrupted.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

def main():
    threading.Thread(target=wake_loop).start()

if __name__ == "__main__":
    main()
