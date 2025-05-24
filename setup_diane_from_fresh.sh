#!/bin/bash
set -e
echo "[DIANE SETUP STARTING]"
sudo apt update && sudo apt install -y \
  python3 python3-pip python3-venv \
  git curl unzip sox ffmpeg libportaudio2 \
  build-essential cmake g++ pkg-config libopenblas-dev \
  liblapack-dev  libffi-dev \
  libssl-dev libmp3lame0  portaudio19-dev 


  # libsoundfile-dev

echo "[Creating Python virtual environment for Diane]"
python3 -m venv ~/diane_venv
source ~/diane_venv/bin/activate

echo "[Installing Python packages]"
pip install --upgrade pip
pip install pyaudio sounddevice numpy flask \
            rich python-dotenv psutil watchdog

echo "[Creating Diane directories]"
mkdir -p ~/diane_models
mkdir -p ~/diane_core_knowledge/default
mkdir -p ~/diane_plugins
mkdir -p ~/diane_logs
mkdir -p ~/diane_personality_profiles
mkdir -p ~/.diane

echo "[Setting up swap file (optional)]"
# sudo fallocate -l 4G /swapfile
# sudo chmod 600 /swapfile
# sudo mkswap /swapfile
# sudo swapon /swapfile
# echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

echo "[Downloading and installing log2ram]"
sudo apt install -y git
git clone https://github.com/azlux/log2ram.git /tmp/log2ram
cd /tmp/log2ram && sudo ./install.sh

echo "[Creating placeholder for model launcher]"
echo '# Put your llama.cpp-based model binary here' > ~/diane_models/README.txt

echo "[DONE: Diane environment is prepared. Models can be added manually to ~/diane_models]"
