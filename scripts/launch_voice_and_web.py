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
