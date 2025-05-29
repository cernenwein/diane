#!/bin/bash
# auto_connect.sh - Auto-connect JLab GO Air Sport if paired

DEVICE_NAME="JLab GO Air Sport"
MAC=$(bluetoothctl devices | grep "$DEVICE_NAME" | awk '{print $2}')

if [ -z "$MAC" ]; then
  echo "Device not found. Exiting."
  exit 1
fi

echo "Attempting to connect to $DEVICE_NAME..."
bluetoothctl << EOF
power on
connect $MAC
EOF
