#!/bin/bash
set -e
echo "[DIANE PHASE 2 SETUP STARTING]"
source ~/diane_venv/bin/activate

echo "[Installing additional Python modules for Diane's extended features]"
pip install flask psutil watchdog requests python-docx

echo "[Creating persistent store and profile system]"
mkdir -p ~/diane_core_knowledge/default
mkdir -p ~/diane_plugins
mkdir -p ~/diane_logs
mkdir -p ~/diane_personality_profiles
mkdir -p ~/diane_projects

echo "[Installing Diane system files]"
cp voice_llama_chat.py ~/voice_llama_chat.py || echo "Warning: voice_llama_chat.py not found"
cp diane_task_manager.py ~/.diane/ || echo "Warning: diane_task_manager.py not found"
cp diane_plugin_loader.py ~/.diane/ || echo "Warning: diane_plugin_loader.py not found"
cp diane_status_report.py ~/.diane/ || echo "Warning: diane_status_report.py not found"
cp diane_self_modify.py ~/.diane/ || echo "Warning: diane_self_modify.py not found"
cp diane_version_control.py ~/.diane/ || echo "Warning: diane_version_control.py not found"

echo "[Setting up systemd service for auto-start]"
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

echo "[Creating placeholder plugin and personality data]"
echo '{}' > ~/.diane/diane_personality_config.json

echo "[DONE: Diane advanced features installed. You may now reboot or start manually with:]"
echo "  source ~/diane_venv/bin/activate && python ~/voice_llama_chat.py"
