#!/usr/bin/env bash
#
# setup_05_diane_environment.sh
# One-shot script to bring Diane Pi environment to a runnable state,
# installing precise-runner (which includes the engine) rather than mycroft-precise.
#
# - Creates and activates Python virtualenv
# - Installs required Python packages
# - Deploys voice_config templates into /mnt/ssd/voice_config
# - Copies prebuilt Precise hotword model (hey computer)
# - Enables and starts the Diane systemd service
#

set -e

echo "=== 1. Create & activate Python virtualenv ==="
if [ ! -d "/home/diane/diane/.venv" ]; then
  python3 -m venv /home/diane/diane/.venv
fi
source /home/diane/diane/.venv/bin/activate

echo -e "\n=== 2. Install Python dependencies ==="
pip install --upgrade pip setuptools wheel
pip install \
  whisper \
  llama-cpp-python \
  piper-tts \
  flask \
  sounddevice \
  pyaudio \
  webrtcvad \
  huggingface-hub \
  precise-runner

echo -e "\n=== 3. Deploy voice_config from repo root to SSD ==="
/home/diane/diane/scripts/deploy_voice_config.sh

echo -e "\n=== 4. Deploy Precise hotword model ==="
HOTWORD_SRC="/home/diane/diane/mycroft-precise/hey-computer.pb"
HOTWORD_DST="/mnt/ssd/models/hotword/precise_diane.pb"
if [ -f "$HOTWORD_SRC" ]; then
  sudo mkdir -p /mnt/ssd/models/hotword
  sudo chown diane:diane /mnt/ssd/models/hotword
  cp "$HOTWORD_SRC" "$HOTWORD_DST"
  sudo chown diane:diane "$HOTWORD_DST"
  chmod 644 "$HOTWORD_DST"
  echo "  Deployed hotword model to $HOTWORD_DST"
else
  echo "  Warning: hotword source $HOTWORD_SRC not found; model not deployed"
fi

echo -e "\n=== 5. Enable & start Diane service ==="
sudo systemctl daemon-reload
sudo systemctl enable voice_llama_chat.service
sudo systemctl start voice_llama_chat.service

echo -e "\n=== 6. Check service status ==="
sudo systemctl status voice_llama_chat.service --no-pager

echo -e "\n=== 7. Environment setup complete ==="
