import subprocess
import json
import os
from voice_utils import speak_text

CRED_PATH = "/opt/diane/config/wifi_credentials.json"

def handle_wifi_connection():
    if not os.path.exists(CRED_PATH):
        speak_text("Wi-Fi credentials are missing.")
        return
    with open(CRED_PATH, 'r') as f:
        known_networks = json.load(f)
    result = subprocess.run(["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"], capture_output=True, text=True)
    available = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    for ssid in available:
        if ssid in known_networks:
            pw = known_networks[ssid]
            connect = subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", pw])
            if connect.returncode == 0:
                speak_text(f"Connected to {ssid}")
                return
    speak_text("No trusted networks found.")
