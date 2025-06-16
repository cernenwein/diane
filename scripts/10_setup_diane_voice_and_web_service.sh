#!/bin/bash
set -e

SERVICE_NAME=diane_voice_and_web
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
VENV_PATH="/home/diane/diane/.venv/bin/python3"
SCRIPT_PATH="/home/diane/diane/scripts/launch_voice_and_web.py"
ENV_FILE="/home/diane/diane/.env"

# Safety check for existing services
echo "[0/4] Checking for conflicting services..."

conflicts=0

if systemctl is-enabled --quiet voice_llama_chat.service; then
    echo "❌ voice_llama_chat.service is ENABLED. Please disable it before continuing:"
    echo "   sudo systemctl disable --now voice_llama_chat.service"
    conflicts=1
elif systemctl is-active --quiet voice_llama_chat.service; then
    echo "❌ voice_llama_chat.service is RUNNING. Please stop it before continuing:"
    echo "   sudo systemctl stop voice_llama_chat.service"
    conflicts=1
fi

if systemctl is-enabled --quiet diane_web.service; then
    echo "❌ diane_web.service is ENABLED. Please disable it before continuing:"
    echo "   sudo systemctl disable --now diane_web.service"
    conflicts=1
elif systemctl is-active --quiet diane_web.service; then
    echo "❌ diane_web.service is RUNNING. Please stop it before continuing:"
    echo "   sudo systemctl stop diane_web.service"
    conflicts=1
fi

if [ "$conflicts" -eq 1 ]; then
    echo "⚠️ Resolve service conflicts before installing the unified service."
    exit 1
fi

echo "[1/4] Creating launch script..."

cat << 'EOF' > "$SCRIPT_PATH"
#!/usr/bin/env bash
set -a
source "$ENV_FILE"
set +a

# Run voice and web processes in background with logging
/home/diane/diane/.venv/bin/python3 /home/diane/diane/voice_llama_chat.py > /home/diane/voice.log 2>&1 &
VOICE_PID=$!

/home/diane/diane/.venv/bin/python3 /home/diane/diane/diane_web.py > /home/diane/web.log 2>&1 &
WEB_PID=$!

# Wait for both
wait $VOICE_PID $WEB_PID
EOF

chmod +x "$SCRIPT_PATH"

echo "[2/4] Creating systemd service..."

cat << EOF | sudo tee "$SERVICE_FILE" > /dev/null
[Unit]
Description=Diane Combined Voice + Web Assistant
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=diane
ExecStart=/bin/bash $SCRIPT_PATH
Restart=on-failure
EnvironmentFile=$ENV_FILE
WorkingDirectory=/home/diane/diane

[Install]
WantedBy=multi-user.target
EOF

echo "[3/4] Reloading systemd..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "[4/4] Enabling and starting service..."
sudo systemctl enable --now $SERVICE_NAME

echo "✅ Combined service $SERVICE_NAME is running."
