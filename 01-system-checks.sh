#!/bin/bash
echo "[✓] Checking system status..."

# Check required commands
for cmd in bluetoothctl systemctl python3; do
    if ! command -v $cmd &> /dev/null; then
        echo "[✗] Required command not found: $cmd"
        exit 1
    fi
done

echo "[✓] All required commands found."
