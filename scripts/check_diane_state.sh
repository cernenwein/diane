#!/usr/bin/env bash
#
# check_diane_state.sh
# Verifies Diane Pi environment: directories, files, permissions, services, Python env.
# Run as diane user (sudo may be needed for some checks).
#

set -e

echo "=== 1. OS and Kernel ==="
uname -a
if command -v lsb_release &> /dev/null; then
  lsb_release -a
else
  cat /etc/os-release
fi

echo -e "\n=== 2. Disk Usage ==="
df -h
echo -e "\nSSD mount usage (/mnt/ssd):"
df -h /mnt/ssd || echo "  /mnt/ssd not found"

echo -e "\n=== 3. RAM and Swap ==="
free -h
echo -e "\nSwap details:"
swapon --show

echo -e "\n=== 4. Directory Structure ==="
echo "/home/diane/diane (depth 2):"
find /home/diane/diane -maxdepth 2 | sed 's/^/  /'
echo -e "\n/mnt/ssd (depth 2):"
find /mnt/ssd -maxdepth 2 | sed 's/^/  /'

echo -e "\n=== 5. Config Files on SSD ==="
for file in /mnt/ssd/voice_config/approved_networks.txt \
            /mnt/ssd/voice_config/synonyms.json \
            /mnt/ssd/voice_config/bluetooth_trusted_devices.txt; do
  if [ -e "$file" ]; then
    echo "  $file exists:"
    ls -l "$file"
  else
    echo "  $file MISSING"
  fi
done

echo -e "\n=== 6. Model Files on SSD ==="
for file in /mnt/ssd/models/L3.2-Rogue-Creative-Instruct-7B-D_AU-Q4_k_m.gguf \
            /mnt/ssd/models/tts/en_US-amy-medium.onnx \
            /mnt/ssd/models/hotword/precise_diane.pb; do
  if [ -e "$file" ]; then
    echo "  $file exists:"
    ls -l "$file"
  else
    echo "  $file MISSING"
  fi
done

echo -e "\n=== 7. Swap File Check ==="
echo -n "Swap entries: "; swapon --show
if swapon --show | grep -q '/mnt/ssd/swapfile'; then
  echo "  SSD swapfile present"
else
  echo "  SSD swapfile NOT present"
fi

echo -e "\n=== 8. Python Virtualenv and Packages ==="
if [ -d "/home/diane/diane/.venv" ]; then
  echo "  Virtualenv exists"
  echo "  Python path: $(/home/diane/diane/.venv/bin/python3 --version)"
  echo "  Installed packages:"
  /home/diane/diane/.venv/bin/pip freeze | sed 's/^/    /'
else
  echo "  Virtualenv missing"
fi

echo -e "\n=== 9. Git Status ==="
if [ -d "/home/diane/diane/.git" ]; then
  git -C /home/diane/diane status --short
else
  echo "  /home/diane/diane is not a git repo"
fi

echo -e "\n=== 10. Service Status ==="
echo "  voice_llama_chat.service:"
systemctl status voice_llama_chat.service --no-pager
echo -e "\n  bluetooth-trusted.service:"
systemctl status bluetooth-trusted.service --no-pager

echo -e "\n=== 11. Audio Devices ==="
echo "  Recording devices (arecord -l):"
arecord -l || echo "    (none)"
echo "  Playback devices (aplay -l):"
aplay -l || echo "    (none)"

echo -e "\n=== 12. Internet Connectivity ==="
ping -c 1 -W 2 google.com >/dev/null && echo "  Internet OK" || echo "  Internet FAIL"

echo -e "\n=== 13. Environment Variables ==="
echo "  HF_ACCESS_TOKEN=${HF_ACCESS_TOKEN:-<not set>}"
echo "  LLM_MODEL_PATH=${LLM_MODEL_PATH:-<not set>}"
echo "  TTS_MODEL_PATH=${TTS_MODEL_PATH:-<not set>}"
echo "  SYNONYMS_PATH=${SYNONYMS_PATH:-<not set>}"
echo "  WEB_API_KEY=${WEB_API_KEY:-<not set>}"

echo -e "\n=== End of Diane State Check ==="
