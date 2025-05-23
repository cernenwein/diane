#!/bin/bash
set -e
echo "[Diane Log2RAM Setup]"
sudo apt update -qq
sudo apt install -y git
git clone https://github.com/azlux/log2ram.git /tmp/log2ram
cd /tmp/log2ram
sudo ./install.sh
echo "Log2RAM installed. You may reboot to apply it fully."
