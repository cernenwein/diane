#!/bin/bash
set -e
echo "[Diane Optimization Script]"
sudo systemctl disable --now triggerhappy.service || true
sudo systemctl disable --now hciuart.service || true
sudo systemctl disable --now bluetooth.service || true
# sudo systemctl disable --now wpa_supplicant.service || true
sudo apt-get update -qq
sudo apt-get install -y zram-tools
for CPUFREQ in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
  echo performance | sudo tee "$CPUFREQ"
done
/opt/vc/bin/tvservice -o || true
echo "Done optimizing. Reboot recommended."
