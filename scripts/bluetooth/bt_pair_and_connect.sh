#!/bin/bash
MAC="$1"
if [ -z "$MAC" ]; then
  echo "Usage: $0 <MAC_ADDRESS>"
  exit 1
fi

bluetoothctl <<EOF
power on
agent on
default-agent
pairable on
discoverable on
scan on
pair $MAC
trust $MAC
connect $MAC
scan off
EOF
