#!/bin/bash
TRUSTED_MACS=$(cat /home/diane/bluetooth_trusted_devices.txt)

for MAC in $TRUSTED_MACS; do
  bluetoothctl connect "$MAC"
done
