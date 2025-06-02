#!/bin/bash
LOG="/opt/diane/diane_logs/bluetooth_scan.log"
mkdir -p "$(dirname "$LOG")"

echo "🔗 Paired Bluetooth Devices:" | tee "$LOG"
echo -e 'paired-devices\nquit' | bluetoothctl | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "📡 Scanning nearby devices (10 seconds)..." | tee -a "$LOG"
timeout 10s bash -c 'echo -e "scan on\nquit" | bluetoothctl' | tee -a "$LOG"
