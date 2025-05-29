#!/bin/bash
# pair_device.sh - Pair JLab GO Air Sport and trust it for automatic connections

DEVICE_NAME="JLab GO Air Sport"

bluetoothctl << EOF
power on
discoverable on
pairable on
agent NoInputNoOutput
default-agent
scan on
EOF

echo "Now put your earbuds in pairing mode. Waiting 20 seconds..."
sleep 20

echo "Attempting to pair with device..."
bluetoothctl << EOF
scan off
devices
EOF

MAC=$(bluetoothctl devices | grep "$DEVICE_NAME" | awk '{print $2}')

if [ -z "$MAC" ]; then
  echo "Could not find $DEVICE_NAME in scanned devices."
  exit 1
fi

echo "Pairing and trusting $MAC..."
bluetoothctl << EOF
pair $MAC
trust $MAC
connect $MAC
EOF

echo "$DEVICE_NAME should now be paired and connected."
