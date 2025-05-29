#!/bin/bash
DEVICE_NAME="JLab GO Air Sport"
MAC=$(bluetoothctl devices | grep "$DEVICE_NAME" | awk '{print $2}')
[ -z "$MAC" ] && echo "Device not found" && exit 1
LOGFILE="/tmp/bluetooth_auto_connect.log"
echo "$(date): Starting auto-connect" >> $LOGFILE
bluetoothctl << EOF
power on
connect $MAC
EOF
