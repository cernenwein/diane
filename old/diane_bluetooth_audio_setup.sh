#!/bin/bash
set -e

echo "[Installing Bluetooth headset audio support for Diane]"

# Install dependencies
sudo apt update
sudo apt install -y pulseaudio pulseaudio-module-bluetooth bluez bluez-tools pavucontrol

# Enable and start PulseAudio for user session
if ! grep -q "autospawn = yes" ~/.config/pulse/client.conf 2>/dev/null; then
  mkdir -p ~/.config/pulse
  echo "autospawn = yes" >> ~/.config/pulse/client.conf
  echo "daemon-binary = /usr/bin/pulseaudio" >> ~/.config/pulse/client.conf
fi

# Enable system modules
pactl load-module module-bluetooth-discover || true
pactl load-module module-bluetooth-policy || true

# Set Bluetooth as trusted and pairable
echo "[Enabling Bluetooth pairing and trust agent]"
sudo rfkill unblock bluetooth
sudo systemctl enable bluetooth.service
sudo systemctl start bluetooth.service

# Optional: Turn on agent to allow pairing
bluetoothctl <<EOF
power on
agent on
default-agent
discoverable on
pairable on
EOF

echo "[Bluetooth setup complete — Diane is ready to pair with headsets]"

echo "To pair a headset manually:"
echo "1. Run 'bluetoothctl'"
echo "2. Use 'scan on' and 'pair XX:XX:XX:XX:XX:XX'"
echo "3. Use 'trust XX:XX:XX:XX:XX:XX' and 'connect XX:XX:XX:XX:XX:XX'"
