#!/bin/bash
LOG="/opt/diane/diane_logs/bluetooth_scan.log"
mkdir -p "$(dirname "$LOG")"

echo "🔧 Scanning for Paired Bluetooth Devices..." | tee "$LOG"

bluetoothctl <<EOF | tee -a "$LOG"
power on
agent on
default-agent
devices Paired
quit
EOF
