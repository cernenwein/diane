#!/bin/bash

echo "🔧 Installing Porcupine and audio dependencies..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio python3-pip

echo "🐍 Installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install pvporcupine pyaudio

echo "📁 Setting up Diane directory..."
mkdir -p /opt/diane
cp voice_llama_chat.py /opt/diane/

echo "🛠️ Installing systemd service..."
cat << EOF | sudo tee /etc/systemd/system/diane_voice.service
[Unit]
Description=Diane Voice Assistant with Porcupine Wake Word
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/diane/voice_llama_chat.py
WorkingDirectory=/opt/diane
StandardOutput=journal
StandardError=journal
Restart=always
User=diane

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl enable diane_voice.service
sudo systemctl start diane_voice.service

echo "✅ Diane voice assistant with Porcupine is now running."
