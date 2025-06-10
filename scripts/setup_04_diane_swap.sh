#!/bin/bash
# setup_04_diane_swap.sh
# Creates and enables a swap file on the SSD for Diane.

SWAP_FILE="/mnt/ssd/swapfile"
SWAP_SIZE="8G"  # Desired swap size

# Check if swap is already configured
if grep -q "$SWAP_FILE" /etc/fstab; then
    echo "Swap file already configured at $SWAP_FILE"
    exit 0
fi

# Create swap file if it doesn't exist
if [ ! -f "$SWAP_FILE" ]; then
    echo "Creating swap file at $SWAP_FILE of size $SWAP_SIZE..."
    if command -v fallocate &> /dev/null; then
        sudo fallocate -l $SWAP_SIZE "$SWAP_FILE"
    else
        sudo dd if=/dev/zero of="$SWAP_FILE" bs=1M count=8192
    fi
else
    echo "Swap file already exists at $SWAP_FILE"
fi

# Set permissions
sudo chmod 600 "$SWAP_FILE"

# Format swap
sudo mkswap "$SWAP_FILE"

# Enable swap immediately
sudo swapon "$SWAP_FILE"

# Add to fstab for persistence
echo "$SWAP_FILE none swap sw 0 0" | sudo tee -a /etc/fstab

echo "Swap file created and enabled on $SWAP_FILE ($SWAP_SIZE)."
