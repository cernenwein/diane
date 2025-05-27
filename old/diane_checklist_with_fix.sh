#!/bin/bash
set -e

echo "===== DIANE SETUP CHECKLIST WITH AUTO-FIX ====="

# Check Python and virtual environment
echo -n "Python version: "
python3 --version || { echo "Missing Python 3"; exit 1; }

echo -n "Virtual environment: "
if [ -d ~/diane_venv ]; then
  echo "Found"
else
  echo "Missing - creating"
  python3 -m venv ~/diane_venv
fi

# Check required directories
for dir in ~/diane_models ~/diane_core_knowledge/default ~/diane_plugins ~/diane_logs ~/diane_projects ~/.diane; do
  echo -n "Checking $dir: "
  if [ -d $dir ]; then
    echo "Exists"
  else
    echo "Missing - creating"
    mkdir -p $dir
  fi
done

# Check Piper voices
echo -n "Piper voices: "
PIPER_DIR=~/.diane/piper_voices
if [ ! -d $PIPER_DIR ]; then
  mkdir -p $PIPER_DIR
fi
VOICE_COUNT=$(ls $PIPER_DIR/*.onnx 2>/dev/null | wc -l)
echo "$VOICE_COUNT voices found"

# Check swap file
echo -n "Swap active: "
if swapon --summary | grep -q '/swapfile'; then
  echo "Yes"
else
  echo "No - setting up swap"
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Check systemd service
echo -n "Diane systemd service: "
if systemctl list-unit-files | grep -q diane.service; then
  echo "Enabled"
else
  echo "Missing - creating"
  cat <<EOF | sudo tee /etc/systemd/system/diane.service
[Unit]
Description=Diane Voice Assistant
After=network.target

[Service]
Type=simple
ExecStart=/home/pi/diane_venv/bin/python /home/pi/voice_llama_chat.py
Restart=on-failure
User=pi
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reexec
  sudo systemctl enable diane.service
fi

# Check log2ram
echo -n "Log2RAM status: "
if systemctl is-active log2ram.service > /dev/null; then
  echo "Running"
else
  echo "Not running - attempting install"
  sudo apt install -y git
  git clone https://github.com/azlux/log2ram.git /tmp/log2ram
  cd /tmp/log2ram && sudo ./install.sh
fi

# Check plugin system
echo -n "Plugin loader: "
if [ -f ~/.diane/diane_plugin_loader.py ]; then
  echo "Present"
else
  echo "Missing - creating placeholder"
  echo '# Plugin loader placeholder' > ~/.diane/diane_plugin_loader.py
fi

echo "===== CHECK COMPLETE ====="
