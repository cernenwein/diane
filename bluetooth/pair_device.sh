#!/bin/bash
DEVICE_NAME="JLab GO Air Sport"
bluetoothctl << EOF
power on
discoverable on
pairable on
agent NoInputNoOutput
default-agent
scan on
EOF

echo "Put earbuds in pairing mode. Waiting 20s..."
sleep 20
bluetoothctl << EOF
scan off
devices
EOF

MAC=$(bluetoothctl devices | grep "$DEVICE_NAME" | awk '{print $2}')
[ -z "$MAC" ] && echo "Device not found" && exit 1
bluetoothctl << EOF
pair $MAC
trust $MAC
connect $MAC
EOF
