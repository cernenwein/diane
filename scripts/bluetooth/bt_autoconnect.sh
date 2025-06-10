#!/bin/bash
# Read only the MAC addresses (first field of each line)
MACS=$(cut -d' ' -f1 /home/diane/diane/bluetooth_trusted_devices.txt)

for MAC in $MACS; do
  echo "Attempting to connect to $MAC"
  bluetoothctl connect "$MAC" || echo "Failed to connect to $MAC"
done

# Always exit 0 so systemd considers it a success
exit 0

