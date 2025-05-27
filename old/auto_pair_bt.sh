#!/bin/bash
# Auto-pair and trust a Bluetooth device by name (one-time use)
# Usage: ./auto_pair_bt.sh "Device Name"

set -e

TARGET_NAME="$1"
RETRY_COUNT=5
SLEEP_INTERVAL=5

if [ -z "$TARGET_NAME" ]; then
  echo "Usage: $0 'Device Name'"
  exit 1
fi

echo "[Searching for Bluetooth device named: $TARGET_NAME]"

DEVICE_ADDR=""

for i in $(seq 1 $RETRY_COUNT); do
  echo "Scan attempt $i of $RETRY_COUNT..."
  DEVICE_ADDR=$(bluetoothctl --timeout 10 scan on | grep "$TARGET_NAME" | awk '{print $3}' | head -n 1)

  if [ ! -z "$DEVICE_ADDR" ]; then
    echo "[Found device: $DEVICE_ADDR]"
    break
  fi

  echo "Device not found, retrying in $SLEEP_INTERVAL seconds..."
  sleep $SLEEP_INTERVAL
done

if [ -z "$DEVICE_ADDR" ]; then
  echo "[Failed to find device after $RETRY_COUNT attempts]"
  exit 1
fi

echo "[Pairing with device: $DEVICE_ADDR]"

bluetoothctl <<EOF
power on
agent on
default-agent
pair $DEVICE_ADDR
trust $DEVICE_ADDR
connect $DEVICE_ADDR
EOF

echo "[Pairing and connection to $TARGET_NAME ($DEVICE_ADDR) complete.]"
