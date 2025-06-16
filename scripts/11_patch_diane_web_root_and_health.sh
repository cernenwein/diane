#!/bin/bash
set -e

WEB_FILE="/home/diane/diane/diane_web.py"

echo "📦 Patching diane_web.py to add / and /health endpoints..."

# Check if already patched
if grep -q "@app.route(\"/health\")" "$WEB_FILE"; then
    echo "✅ Patch already applied. Skipping."
    exit 0
fi

cat << 'EOF' >> "$WEB_FILE"

@app.route("/")
def root():
    return (
        "<h1>Diane Web Interface</h1><p>Available routes:</p><ul>"
        "<li><a href='/chat'>/chat</a></li>"
        "<li><a href='/health'>/health</a></li>"
        "</ul>",
        200
    )

@app.route("/health")
def health():
    return {"status": "ok"}, 200
EOF

echo "✅ Patch applied. Restarting service..."
sudo systemctl restart diane_voice_and_web.service

echo "🌐 Visit http://diane.local:8081/ to verify."
