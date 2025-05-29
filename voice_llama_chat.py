#!/usr/bin/env python3
import os
import sys
import time
import sounddevice as sd
import soundfile as sf
import subprocess
import logging

# Setup logging
log_file = "/opt/diane/logs/diane_run.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Diane boot script starting...")

def play_startup_sound():
    try:
        subprocess.run(["aplay", "/opt/diane/sounds/startup.wav"], check=True)
        logging.info("Played startup sound.")
    except Exception as e:
        logging.error(f"Failed to play startup sound: {e}")

def main_loop():
    logging.info("Entering main listening loop.")
    print("[Diane says]: I am Diane, online and listening.")
    try:
        while True:
            print("Listening for wake word...")
            time.sleep(5)
            # Simulate wake word for debug
            logging.info("Simulated wake word heard.")
            print("[Diane says]: Yes?")
            # Simulate response generation and audio playback
            try:
                if os.path.exists("/tmp/diane_output.wav"):
                    subprocess.run(["aplay", "/tmp/diane_output.wav"], check=True)
                    logging.info("Played response audio.")
                else:
                    logging.warning("Response audio file not found.")
            except Exception as e:
                logging.error(f"Error playing response audio: {e}")
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Shutting down on user interrupt.")

if __name__ == "__main__":
    try:
        play_startup_sound()
        main_loop()
    except Exception as e:
        logging.exception("Fatal error occurred")
        sys.exit(1)
