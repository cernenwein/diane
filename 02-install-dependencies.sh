#!/bin/bash
echo "[✓] Installing dependencies..."

sudo apt-get update
sudo apt-get install -y bluez pulseaudio pulseaudio-module-bluetooth python3-pip

# Optional: install voice recognition deps
pip3 install -r ../requirements.txt

echo "[✓] Dependencies installed."
