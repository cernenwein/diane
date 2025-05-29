
# Add this to your command processor logic in voice_llama_chat.py

def process_command(text):
    text = text.lower()
    if "connect to wi-fi" in text or "connect to wifi" in text:
        handle_wifi_connection()
    elif "status" in text:
        speak_text("I'm running and listening. Let me know what you'd like.")
    else:
        speak_text("I'm sorry, I didn't understand that command.")
