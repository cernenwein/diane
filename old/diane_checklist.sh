#!/bin/bash
set -e

echo "===== DIANE SETUP CHECKLIST ====="

# Check Python and virtual environment
echo -n "Python version: "
python3 --version || echo "Missing Python 3"
echo -n "Virtual environment: "
[ -d ~/diane_venv ] && echo "Found" || echo "Missing ~/diane_venv"

# Check required directories
for dir in ~/diane_models ~/diane_core_knowledge/default ~/diane_plugins ~/diane_logs ~/diane_projects ~/.diane; do
  echo -n "Checking $dir: "
  [ -d $dir ] && echo "Exists" || echo "Missing"
done

# Check Piper voices
echo -n "Piper voices: "
ls ~/.diane/piper_voices/*.onnx 2>/dev/null | wc -l | xargs echo "voices found"

# Check swap file
echo -n "Swap active: "
swapon --summary | grep -q '/swapfile' && echo "Yes" || echo "No"

# Check systemd service
echo -n "Diane systemd service: "
systemctl list-unit-files | grep -q diane.service && echo "Enabled" || echo "Missing"

# Check log2ram
echo -n "Log2RAM status: "
systemctl is-active log2ram.service 2>/dev/null || echo "Not running"

# Check RAG readiness
echo -n "Core knowledge files: "
find ~/diane_core_knowledge -type f | wc -l | xargs echo "files indexed"

# Check plugin system
echo -n "Plugin loader: "
[ -f ~/.diane/diane_plugin_loader.py ] && echo "Present" || echo "Missing"

echo "===== CHECK COMPLETE ====="
