import json
import os

WIFI_CONFIG_PATH = "/opt/diane/wifi_connections.json"

def load_wifi_config():
    if not os.path.exists(WIFI_CONFIG_PATH):
        return {}
    with open(WIFI_CONFIG_PATH) as f:
        return json.load(f)

def save_wifi_config(data):
    with open(WIFI_CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)

def handle_add_wifi(ssid, password):
    data = load_wifi_config()
    data[ssid] = password
    save_wifi_config(data)
    return f"I've saved the Wi-Fi network {ssid}."

def handle_forget_wifi(ssid):
    data = load_wifi_config()
    if ssid in data:
        del data[ssid]
        save_wifi_config(data)
        return f"I've removed the Wi-Fi network {ssid}."
    return f"I don't have {ssid} in the list."

def handle_list_wifi():
    data = load_wifi_config()
    if not data:
        return "I don't know any Wi-Fi networks yet."
    return "Known networks: " + ", ".join(data.keys())
