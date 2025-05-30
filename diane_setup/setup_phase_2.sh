#!/bin/bash

echo "🚀 Starting Diane Phase 2 Setup..."

# Ensure root privileges
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root"
  exit 1
fi

# Step 1: System update and dependency install
echo "🔧 Installing required packages..."
apt update && apt install -y     git python3 python3-pip python3-venv sox     portaudio19-dev libffi-dev libnss3-tools jq unzip curl

# Step 2: Setup virtual environment
echo "🐍 Creating Python virtual environment..."
cd /home/diane || exit 1
python3 -m venv diane_venv
source diane_venv/bin/activate
pip install --upgrade pip

# Step 3: Install Python dependencies
pip install sounddevice soundfile openwakeword faster-whisper numpy

# Step 4: Prepare folders
echo "📂 Preparing Diane folder structure..."
mkdir -p /home/diane/logs
mkdir -p /mnt/ssd/models

# Step 5: Install /opt/diane base structure
echo "📦 Installing Diane's /opt directory structure..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/opt_diane_generated" || exit 1
./install_opt_diane_structure.sh || echo "⚠️ Failed to install /opt structure"
cd "$SCRIPT_DIR"

echo "✅ Phase 2 setup complete. Ready for model and config population."
