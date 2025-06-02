#!/bin/bash
LOG="/opt/diane/diane_logs/bluetooth_scan.log"
echo "🔗 Paired Bluetooth Devices:" | tee "$LOG"
bluetoothctl paired-devices | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "📡 Scanning nearby devices (10 seconds)..." | tee -a "$LOG"
timeout 10s bluetoothctl scan on | tee -a "$LOG"
