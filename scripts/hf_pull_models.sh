#!/usr/bin/env bash
#
# hf_pull_models.sh
#
# Use Hugging Face CLI to download or update models into /mnt/ssd/models.
# Run this whenever you need to fetch newer versions of LLM, Whisper, or TTS models.
#
# Requires:
#   - ~/.hf_token containing a valid HF access token
#   - Diane’s venv activated (to have hf available)
#   - HDD/SSD mounted at /mnt/ssd with these directories:
#       /mnt/ssd/models/llm/
#       /mnt/ssd/models/whisper/
#       /mnt/ssd/models/tts/
#

set -e

# 1. Activate venv so hf CLI is on PATH and HF_ACCESS_TOKEN is set
source /home/diane/diane/.venv/bin/activate

# 2. Ensure target directories exist
sudo mkdir -p /mnt/ssd/models/llm
sudo mkdir -p /mnt/ssd/models/whisper
sudo mkdir -p /mnt/ssd/models/tts
sudo chown diane:diane /mnt/ssd/models/llm /mnt/ssd/models/whisper /mnt/ssd/models/tts
chmod 755 /mnt/ssd/models/llm /mnt/ssd/models/whisper /mnt/ssd/models/tts

# 3. Pull an LLM from Hugging Face (example: Llama 2 7B)
#    Replace 'my-org/llama-2-7b' with the actual repo you want
MODEL_LLM="my-org/llama-2-7b"
DEST_LLM="/mnt/ssd/models/llm/llama-2-7b"
echo "Pulling LLM model ${MODEL_LLM} → ${DEST_LLM}"
hf repo clone "${MODEL_LLM}" "${DEST_LLM}" --revision main --depth 1 || {
    echo "Model already exists, pulling updates..."
    cd "${DEST_LLM}"
    hf repo sync
    cd - >/dev/null
}

# 4. Pull Whisper model or any STT model (example: openai/whisper-small)
MODEL_WHIPPER="openai/whisper-small"
DEST_WHIPER="/mnt/ssd/models/whisper/whisper-small"
echo "Pulling Whisper model ${MODEL_WHIPPER} → ${DEST_WHIPER}"
hf repo clone "${MODEL_WHIPPER}" "${DEST_WHIPER}" --revision main --depth 1 || {
    echo "Model already exists, pulling updates..."
    cd "${DEST_WHIPER}"
    hf repo sync
    cd - >/dev/null
}

# 5. Pull TTS model (example: rhasspy/piper-tts-en-us)
MODEL_TTS="rhasspy/piper-tts-en-us-medium-v0.1"
DEST_TTS="/mnt/ssd/models/tts/piper-tts-en-us-medium-v0.1"
echo "Pulling TTS model ${MODEL_TTS} → ${DEST_TTS}"
hf repo clone "${MODEL_TTS}" "${DEST_TTS}" --revision main --depth 1 || {
    echo "Model already exists, pulling updates..."
    cd "${DEST_TTS}"
    hf repo sync
    cd - >/dev/null
}

echo "All models up to date."
