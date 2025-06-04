#!/bin/bash
LOG="/opt/diane/diane_logs/bluetooth_trust.log"
TRUSTED_FILE="/opt/diane/bluetooth_trusted_devices.txt"
mkdir -p "$(dirname "$LOG")"

echo "💙 Importing trusted Bluetooth devices..." | tee "$LOG"

if [ -f "$TRUSTED_FILE" ]; then
    while IFS= read -r line; do
        MAC=$(echo "$line" | awk '{print $1}')
        NAME=$(echo "$line" | cut -d' ' -f2-)
        echo "🔗 Trusting $NAME ($MAC)..." | tee -a "$LOG"
        bluetoothctl <<EOF | tee -a "$LOG"
power on
agent on
default-agent
trust $MAC
connect $MAC
EOF
    done < "$TRUSTED_FILE"
else
    echo "⚠️ Trusted device list not found at $TRUSTED_FILE" | tee -a "$LOG"
fi
