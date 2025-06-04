#!/bin/bash
# Phase 1: Setup base system for Diane on Raspberry Pi
set -e
echo "[Diane Setup] Creating diane user..."
sudo useradd -m -s /bin/bash diane || echo "User already exists"
sudo usermod -aG sudo diane

echo "[Diane Setup] Ensuring essential packages are installed..."
sudo apt-get update
sudo apt-get install -y unzip curl net-tools network-manager

echo "[Diane Setup] Mounting SSD if available..."
if lsblk | grep -q nvme; then
  sudo mkdir -p /mnt/ssd
  sudo mount /dev/nvme0n1p1 /mnt/ssd || echo "[Warn] SSD already mounted or error occurred"
fi

echo "[Diane Setup] Creating swap file..."
if [ ! -f /swapfile ]; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

echo "[Diane Setup] System base setup complete."
