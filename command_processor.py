from wifi_handler import handle_wifi_connection
from voice_utils import speak_text

def process_command(text):
    text = text.lower()
    if "connect to wi-fi" in text or "connect to wifi" in text:
        handle_wifi_connection()
    elif "status" in text:
        speak_text("I’m running and ready.")
    else:
        speak_text("I didn’t catch that.")
