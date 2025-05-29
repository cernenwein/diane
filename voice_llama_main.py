#!/usr/bin/env python3
import logging
from voice_utils import speak_text, record_voice, wait_for_wake_word
from wifi_handler import handle_wifi_connection
from command_processor import process_command

LOG_PATH = "/opt/diane/logs/diane_run.log"
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG, format="%(asctime)s - %(message)s")

if __name__ == "__main__":
    logging.info("Diane is online and starting.")
    speak_text("I am Diane, online and listening.")
    while True:
        wait_for_wake_word()
        speak_text("Yes?")
        record_voice()
        process_command("connect to wifi")  # Replace with actual speech-to-text
