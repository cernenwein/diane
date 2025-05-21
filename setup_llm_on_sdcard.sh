#!/bin/bash
set -e

echo "=== STEP 1: Update system and install base packages ==="
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake git wget unzip python3 python3-pip libsndfile1-dev ffmpeg aplay

echo "=== STEP 2: Create 4GB swap file ==="
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
grep -q "/swapfile" /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

echo "=== STEP 3: Clone and build llama.cpp ==="
cd ~
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir -p build && cd build
cmake ..
make -j4

echo "=== STEP 4: Download 3B model to SD card ==="
mkdir -p ~/models/mistral3b
cd ~/models/mistral3b
wget https://huggingface.co/TheBloke/Mistral-3B-Instruct-v0.1-GGUF/resolve/main/mistral-3b-instruct-v0.1.Q4_K_M.gguf

echo "=== STEP 5: Install Vosk and Piper ==="
pip3 install vosk sounddevice

echo "Downloading Vosk model..."
mkdir -p ~/vosk_model
cd ~/vosk_model
wget -O model.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip model.zip && rm model.zip

echo "Installing Piper..."
cd ~
git clone https://github.com/rhasspy/piper.git
cd piper
mkdir build && cd build
cmake ..
make -j4

echo "Downloading Piper voice model..."
mkdir -p ~/piper/voices/en_US
cd ~/piper/voices/en_US
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy-low/en_US-amy-low.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy-low/en_US-amy-low.onnx.json

echo "=== Setup complete! ==="
echo "To run the model:"
echo "  ~/llama.cpp/build/main -m ~/models/mistral3b/mistral-3b-instruct-v0.1.Q4_K_M.gguf --low-mem -t 4 -p 'Say something cool!'"
echo ""
echo "Swap is active. LLM and voice setup is ready on SD card."
