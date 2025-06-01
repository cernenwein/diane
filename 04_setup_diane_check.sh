#!/bin/bash
echo "🔍 Diane System Health Check"

echo "✅ Checking user..."
id diane || echo "❌ User 'diane' not found!"

echo "✅ Checking Python venv..."
[ -d /home/diane/diane_venv ] && echo "✔ Python venv found." || echo "❌ Python venv missing!"

echo "✅ Checking SSD mount..."
mount | grep /mnt/ssd && echo "✔ SSD mounted." || echo "❌ SSD not mounted!"

echo "✅ Checking /opt/diane structure..."
for dir in logs projects plugins core_knowledge personality_profiles rag_index; do
  [ -d /opt/diane/$dir ] && echo "✔ /opt/diane/$dir exists." || echo "❌ Missing: /opt/diane/$dir"
done

echo "✅ Checking voice startup file..."
[ -f /home/diane/voice_llama_chat.py ] && echo "✔ voice_llama_chat.py found." || echo "❌ voice_llama_chat.py missing!"

echo "✅ Checking diane.service..."
systemctl status diane.service >/dev/null 2>&1 && echo "✔ diane.service is installed." || echo "❌ diane.service not found or inactive."
