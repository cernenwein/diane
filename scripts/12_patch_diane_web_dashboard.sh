#!/bin/bash
set -e

WEB_FILE="/home/diane/diane/diane_web.py"
TEMPLATE_DIR="/home/diane/diane/templates"

echo "📦 Installing chat dashboard template..."
mkdir -p "$TEMPLATE_DIR"
cp "$(dirname "$0")/templates/chat.html" "$TEMPLATE_DIR/"

echo "🔧 Patching Flask routes for / and /chat..."

# Only add if not already present
if ! grep -q "@app.route(\"/chat\")" "$WEB_FILE"; then
cat << 'EOF' >> "$WEB_FILE"

from flask import render_template, redirect

@app.route("/")
def root_redirect():
    return redirect("/chat")

@app.route("/chat")
def chat_ui():
    return render_template("chat.html")
EOF
fi

echo "♻️ Restarting service..."
sudo systemctl restart diane_voice_and_web.service

echo "✅ Chat dashboard is live at http://diane.local:8081/chat"
