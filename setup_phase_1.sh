#!/bin/bash

echo "🔧 Phase 1: System Preparation Starting..."

# Ensure root permissions
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run this script as root."
  exit 1
fi

# Step 1: Create a new user for Diane
if id "diane" &>/dev/null; then
  echo "👤 User 'diane' already exists. Skipping user creation."
else
  echo "👤 Creating user 'diane'..."
  useradd -m -s /bin/bash diane
  echo "diane ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/diane
fi

# Step 2: Mount SSD to /mnt/ssd if available
echo "💽 Checking for SSD..."
SSD_DEV=$(lsblk -ndo NAME,MODEL | grep -i 'SSD' | awk '{print $1}' | head -n 1)

if [ -n "$SSD_DEV" ]; then
  echo "📦 Found SSD: $SSD_DEV. Mounting to /mnt/ssd..."
  mkdir -p /mnt/ssd
  grep -q "/mnt/ssd" /etc/fstab || echo "/dev/$SSD_DEV /mnt/ssd ext4 defaults,nofail 0 2" >> /etc/fstab
  mount /mnt/ssd || echo "⚠️ SSD mount failed, continuing without it."
else
  echo "⚠️ No SSD detected. Continuing without SSD mount."
fi

# Step 3: Create swap file if not already configured
SWAPFILE="/swapfile"
if swapon --show | grep -q "$SWAPFILE"; then
  echo "🛌 Swap already configured. Skipping."
else
  echo "🛠 Creating 2GB swap file at $SWAPFILE..."
  fallocate -l 2G $SWAPFILE
  chmod 600 $SWAPFILE
  mkswap $SWAPFILE
  swapon $SWAPFILE
  echo "$SWAPFILE none swap sw 0 0" >> /etc/fstab
fi

# Step 4: Update and install base tools
echo "📦 Installing base system packages..."
apt update && apt install -y sudo unzip curl net-tools network-manager

echo "✅ Phase 1 system prep complete. Ready to reboot or run Phase 2."
