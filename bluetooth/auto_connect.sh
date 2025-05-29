#!/bin/bash
DEVICE_NAME="JLab GO Air Sport"
MAC=$(bluetoothctl devices | grep "$DEVICE_NAME" | awk '{print $2}')
[ -z "$MAC" ] && echo "Device not found" && exit 1
bluetoothctl << EOF
power on
connect $MAC
EOF
