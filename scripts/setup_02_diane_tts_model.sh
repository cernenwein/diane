#!/usr/bin/env bash
#
# setup_02_diane_tts_model.sh
#
# Downloads Piper TTS model (en_US-amy-medium.onnx) and its metadata JSON
# into /mnt/ssd/models/tts so that Diane can load it at runtime.
# Idempotent: if files already exist, it skips the download.
#
# Usage (on Diane, after git pull):
#   cd /home/diane/diane/scripts
#   sudo ./setup_02_diane_tts_model.sh

set -euo pipefail

# Where we want to store Piper TTS models:
TTS_DIR="/mnt/ssd/models/tts"

# The exact filenames we expect:
MODEL_FILE="en_US-amy-medium.onnx"
META_FILE="en_US-amy-medium.onnx.json"

# Base URL on Hugging Face for this voice:
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium"

# Full URLs for model + metadata
URL_MODEL="${BASE_URL}/${MODEL_FILE}"
URL_META="${BASE_URL}/${META_FILE}"

echo
echo "→ Ensuring TTS folder exists at ${TTS_DIR} ..."
if [ ! -d "$TTS_DIR" ]; then
  mkdir -p "$TTS_DIR"
  echo "    • Created directory: $TTS_DIR"
else
  echo "    • Directory already exists: $TTS_DIR"
fi

# Function to download a file if it's missing
download_if_missing() {
  local url="$1"
  local dest="$2"

  if [ -f "$dest" ]; then
    echo "    • Already present: $(basename "$dest")"
  else
    echo "    • Downloading $(basename "$dest") ..."
    wget -q --show-progress -O "$dest" "$url"
    echo "      → Saved to: $dest"
  fi
}

echo
echo "→ Checking for Piper TTS model and metadata ..."

# 1) Model
download_if_missing "$URL_MODEL" "${TTS_DIR}/${MODEL_FILE}"

# 2) Metadata JSON
download_if_missing "$URL_META" "${TTS_DIR}/${META_FILE}"

# Verify both files now exist
echo
if [ -f "${TTS_DIR}/${MODEL_FILE}" ] && [ -f "${TTS_DIR}/${META_FILE}" ]; then
  echo "✔  Piper TTS files are in place:"
  echo "    • ${TTS_DIR}/${MODEL_FILE}"
  echo "    • ${TTS_DIR}/${META_FILE}"
  echo
  echo "→ Diane should now see and load the TTS model from ${TTS_DIR}."
  echo
  exit 0
else
  echo "❌  Error: one or both files are missing under ${TTS_DIR}."
  exit 1
fi
