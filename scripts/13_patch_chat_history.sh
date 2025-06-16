#!/bin/bash
set -e

WEB_FILE="/home/diane/diane/diane_web.py"
TEMPLATE_DIR="/home/diane/diane/templates"

echo "📦 Updating chat.html template with persistent history..."
mkdir -p "$TEMPLATE_DIR"
cp "$(dirname "$0")/templates/chat.html" "$TEMPLATE_DIR/"

echo "🔧 Patching diane_web.py to add chat history support..."

if ! grep -q "@app.route(\"/history\")" "$WEB_FILE"; then
cat << 'EOF' >> "$WEB_FILE"

chat_history = []

@app.route("/history")
def history():
    return {"history": chat_history[-200:]}

from flask import request, jsonify

@app.route("/query", methods=["POST"])
def patched_query():
    data = request.get_json()
    user_input = data.get("query", "")
    chat_history.append({"sender": "user", "text": user_input})
    response = "This is a mock response to: " + user_input
    chat_history.append({"sender": "ai", "text": response})
    return jsonify({"response": response})
EOF
fi

echo "♻️ Restarting service..."
sudo systemctl restart diane_voice_and_web.service

echo "✅ Persistent chat history is now live at http://diane.local:8081/chat"
