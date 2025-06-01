#!/bin/bash
# Phase 2: Install Diane services, voice modules, and dependencies
set -e
echo "[Diane Setup] Installing Python dependencies..."
sudo apt-get install -y python3-venv python3-dev portaudio19-dev libffi-dev ffmpeg
python3 -m venv /home/diane/diane_venv
source /home/diane/diane_venv/bin/activate
pip install --upgrade pip
pip install sounddevice soundfile faster-whisper

echo "[Diane Setup] Cloning models directory structure..."
mkdir -p /mnt/ssd/models /home/diane/models
mkdir -p /opt/diane/{logs,projects,plugins,core_knowledge,personality_profiles}

echo "[Diane Setup] Phase 2 setup complete."
