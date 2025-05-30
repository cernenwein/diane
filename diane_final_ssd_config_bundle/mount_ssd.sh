#!/bin/bash
DEVICE="/dev/nvme0n1p1"
MOUNTPOINT="/mnt/ssd"
if lsblk | grep -q "nvme0n1"; then
    sudo mkdir -p "$MOUNTPOINT"
    sudo mount "$DEVICE" "$MOUNTPOINT"
    echo "Mounted SSD at $MOUNTPOINT"
fi
