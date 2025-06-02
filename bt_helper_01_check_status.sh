#!/bin/bash
LOG="/opt/diane/diane_logs/bluetooth_status.log"
echo "🔍 Checking Bluetooth service..." | tee -a "$LOG"
systemctl status bluetooth | grep Active | tee -a "$LOG"
hciconfig -a | tee -a "$LOG"
