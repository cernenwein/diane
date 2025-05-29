#!/usr/bin/env python3
import os
import sys
import time
import logging
import subprocess
import sounddevice as sd
import soundfile as sf
from queue import Queue
import threading

# Configuration
LOG_PATH = "/opt/diane/logs/diane_run.log"
MODEL_PATH = "/opt/diane/diane_models"
AUDIO_OUTPUT_PATH = "/tmp/diane_output.wav"
STARTUP_SOUND_PATH = "/opt/diane/sounds/startup.wav"
WAKE_WORD = "Diane"

# Setup logging
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Starting Diane diane_launcher.py")

# Placeholder for TTS with Piper
def speak_text(text):
    try:
        logging.info(f"Speaking: {text}")
        subprocess.run([
            "piper", 
            "--model", "/opt/diane/piper/en_US-amy-low.onnx", 
            "--output_file", AUDIO_OUTPUT_PATH
        ], input=text.encode(), check=True)
        subprocess.run(["aplay", AUDIO_OUTPUT_PATH], check=True)
    except Exception as e:
        logging.error(f"TTS or playback error: {e}")

# Record short voice command
def record_voice(duration=4, filename="/tmp/diane_input.wav"):
    try:
        logging.info("Recording voice...")
        samplerate = 16000
        duration = int(duration)
        q = Queue()

        def callback(indata, frames, time, status):
            q.put(indata.copy())

        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            with sf.SoundFile(filename, mode='x', samplerate=samplerate,
                              channels=1, subtype='PCM_16') as file:
                for _ in range(0, int(samplerate / 8000 * duration)):
                    file.write(q.get())
        logging.info("Recording complete.")
    except Exception as e:
        logging.error(f"Recording failed: {e}")

# Simulated wake word detection
def wait_for_wake_word():
    print("Listening for wake word...")
    logging.info("Simulated wake word detection active.")
    while True:
        try:
            input_text = input("Say something to trigger Diane (type 'Diane' to wake): ")
            if WAKE_WORD.lower() in input_text.lower():
                logging.info("Wake word detected.")
                return
        except KeyboardInterrupt:
            logging.info("Interrupted during wake word detection.")
            sys.exit(0)

# Main loop
def main_loop():
    logging.info("Entering main loop.")
    while True:
        wait_for_wake_word()
        speak_text("Yes?")
        record_voice()
        speak_text("I'm still learning to understand. Please configure LLM inference next.")

# Startup sound
def play_startup_sound():
    try:
        if os.path.exists(STARTUP_SOUND_PATH):
            subprocess.run(["aplay", STARTUP_SOUND_PATH], check=True)
            logging.info("Played startup sound.")
    except Exception as e:
        logging.warning(f"Could not play startup sound: {e}")

if __name__ == "__main__":
    try:
        play_startup_sound()
        main_loop()
    except Exception as main_e:
        logging.exception("Fatal error in Diane startup loop")
        sys.exit(1)
