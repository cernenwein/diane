#!/bin/bash
LOG="/opt/diane/diane_logs/bluetooth_connect.log"
MAC="$1"
if [ -z "$MAC" ]; then
  echo "❗ Usage: $0 <MAC_ADDRESS>" | tee -a "$LOG"
  exit 1
fi
echo "🔌 Trying to connect to $MAC..." | tee -a "$LOG"
bluetoothctl <<EOF | tee -a "$LOG"
power on
agent on
default-agent
connect $MAC
trust $MAC
EOF
