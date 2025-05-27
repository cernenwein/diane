#!/bin/bash
# Force reset Bluetooth adapter and begin fresh scan

echo "[Restarting Bluetooth service]"
sudo systemctl restart bluetooth
sleep 2

echo "[Bringing up hci0 if down]"
sudo hciconfig hci0 up || true
sleep 1

echo "[Resetting agent and preparing to scan]"
bluetoothctl <<EOF
power on
agent on
default-agent
discoverable on
pairable on
scan on
EOF

echo "[Bluetooth is now scanning. Watch for device names to appear.]"
