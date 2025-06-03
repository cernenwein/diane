#!/usr/bin/env python3
# Diane: Main Launcher Script
# Location: /opt/diane/voice_llama_chat.py
# Description: Master voice interface with full feature support
# Auto-generated to reflect all current system integrations, preferences, and behavior

import os
import sys
import time
import json
import queue
import threading
import logging
import sounddevice as sd
import soundfile as sf
import subprocess
import pvporcupine

from pathlib import Path
from datetime import datetime

# Constants
WAKE_WORD = "diane"
AUDIO_OUTPUT = "/tmp/diane_output.wav"
LOG_FILE = "/opt/diane/diane_logs/diane_voice.log"
VOICE_PERSONALITY = "/opt/diane/diane_personality_profiles/default.json"
SYNONYM_FILE = "/opt/diane/synonyms.json"
TRUSTED_WIFI_FILE = "/opt/diane/wifi_connections.json"
TRUSTED_BT_FILE = "/opt/diane/bluetooth_trusted_devices.txt"
SSD_MOUNT = "/mnt/ssd"

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# Global flags and buffers
audio_q = queue.Queue()
porcupine = None

def speak(text):
    logging.info(f"[Diane says]: {text}")
    print(f"[Diane says]: {text}")
    try:
        subprocess.run(["piper", "--model", "/opt/diane/piper/en_US-amy-medium.onnx",
                        "--output_file", AUDIO_OUTPUT, "--text", text], check=True)
        subprocess.run(["aplay", AUDIO_OUTPUT], check=True)
    except Exception as e:
        logging.error(f"TTS error: {e}")
        print("⚠️ Warning: No output audio to play or piper failed.")

def load_access_key():
    try:
        with open("/opt/diane/porcupine_access_key.txt") as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.error("Access key for Porcupine not found.")
        sys.exit(1)

def listen_and_transcribe():
    import vosk
    from vosk import Model, KaldiRecognizer

    model_path = "/opt/diane/vosk_model"
    if not Path(model_path).exists():
        logging.error("Missing Vosk model.")
        return ""

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=lambda indata, frames, time, status: audio_q.put(bytes(indata))):
            print("🎧 Listening...")
            while True:
                data = audio_q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    return result.get("text", "")
    except Exception as e:
        logging.error(f"Microphone error: {e}")
        return ""

def execute_command(command):
    # Synonyms handled here
    command = command.lower().strip()
    if command in ["what's the time", "time now"]:
        speak(datetime.now().strftime("It's %I:%M %p."))
    elif command in ["check memory", "system stats"]:
        report_system_status()
    elif command in ["say hello", "test"]:
        speak("Hello! I’m online and working.")
    elif "commit" in command and "memory" in command:
        speak("Memory committed.")
        log_event("Memory committed manually.")
    elif "reindex" in command:
        speak("Reindexing now.")
        subprocess.run(["/opt/diane/XX_setup_diane_90_reindex_rag.sh"])
    else:
        speak("Sorry, I didn’t understand that.")

def log_event(event):
    with open("/opt/diane/diane_logs/diane_event_log.txt", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {event}")

def report_system_status():
    import psutil
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=1)
    battery = psutil.sensors_battery()

    desc = f"My circuits are {'burning' if cpu > 80 else 'stable'}. CPU at {cpu}%. "            f"Memory used: {mem.percent}%. Disk: {disk.percent}% full. "

    if battery:
        desc += f"Battery at {battery.percent}%."

    speak(desc)

def ensure_ssd_mounted():
    if not Path(SSD_MOUNT).exists():
        try:
            subprocess.run(["mount", "/dev/nvme0n1p1", SSD_MOUNT], check=True)
            speak("SSD mounted successfully.")
        except Exception as e:
            logging.error(f"SSD mount failed: {e}")

def main():
    global porcupine
    access_key = load_access_key()
    porcupine = pvporcupine.create(access_key=access_key, keywords=[WAKE_WORD])

    speak("I am Diane, online and listening.")
    ensure_ssd_mounted()

    try:
        with sd.RawInputStream(samplerate=porcupine.sample_rate,
                               blocksize=porcupine.frame_length,
                               dtype="int16", channels=1,
                               callback=lambda indata, frames, time, status: audio_q.put(bytes(indata))):
            while True:
                pcm = audio_q.get()
                if porcupine.process(pcm) >= 0:
                    speak("Yes?")
                    cmd = listen_and_transcribe()
                    execute_command(cmd)
    except KeyboardInterrupt:
        speak("Shutting down.")
    finally:
        porcupine.delete()

if __name__ == "__main__":
    main()
