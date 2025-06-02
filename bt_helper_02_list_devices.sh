#!/bin/bash
LOG="/opt/diane/diane_logs/bluetooth_scan.log"
mkdir -p "$(dirname "$LOG")"

echo "🔧 Initializing Bluetooth controller..." | tee "$LOG"

bluetoothctl <<EOF | tee -a "$LOG"
power on
agent on
default-agent
paired-devices
quit
EOF

echo "" | tee -a "$LOG"
echo "📡 Scanning nearby devices (10 seconds)..." | tee -a "$LOG"
timeout 10s bluetoothctl --timeout 10 <<EOF | tee -a "$LOG"
scan on
EOF
