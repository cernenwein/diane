#!/bin/bash
# This script removes all previously paired Bluetooth devices

echo "[Fetching list of paired devices...]"
paired_devices=$(bluetoothctl paired-devices | awk '{print $2}')

if [ -z "$paired_devices" ]; then
  echo "No paired devices found."
  exit 0
fi

echo "[Removing all paired devices...]"
for dev in $paired_devices; do
  echo "Removing $dev"
  bluetoothctl remove $dev
done

echo "[All paired Bluetooth devices have been removed.]"
