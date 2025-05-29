#!/usr/bin/env python3
import json
import subprocess
import os
import logging

CRED_PATH = "/opt/diane/config/wifi_credentials.json"
LOG_PATH = "/opt/diane/logs/wifi_connection.log"

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s - %(message)s")

def load_credentials():
    if not os.path.exists(CRED_PATH):
        logging.error("Wi-Fi credentials file not found.")
        return {}
    with open(CRED_PATH, 'r') as f:
        return json.load(f)

def scan_networks():
    result = subprocess.run(["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error("Failed to scan networks.")
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

def connect_to_known_network():
    known_networks = load_credentials()
    available = scan_networks()
    for ssid in available:
        if ssid in known_networks:
            password = known_networks[ssid]
            logging.info(f"Attempting to connect to: {ssid}")
            result = subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", password])
            if result.returncode == 0:
                logging.info(f"Connected to: {ssid}")
                print(f"Diane: Connected to {ssid}")
                return True
            else:
                logging.warning(f"Failed to connect to {ssid}")
    logging.info("No known networks available.")
    print("Diane: No trusted networks found nearby.")
    return False

if __name__ == "__main__":
    connect_to_known_network()
