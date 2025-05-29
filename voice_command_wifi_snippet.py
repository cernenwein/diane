
def handle_wifi_connection():
    speak_text("Scanning for known Wi-Fi networks.")
    result = subprocess.run(["python3", "/opt/diane/connect_wifi.py"], capture_output=True, text=True)
    if result.returncode == 0:
        speak_text("Wi-Fi connected.")
    else:
        speak_text("I couldn't connect to any known Wi-Fi.")
