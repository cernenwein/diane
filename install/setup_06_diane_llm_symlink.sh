#!/usr/bin/env bash
#
# setup_06_diane_llm_symlink.sh
# Create an 'llm' directory and a stable symlink 'current_model.gguf'
# pointing to the most recent .gguf model in /mnt/ssd/models.
#

set -euo pipefail

MODEL_DIR="/mnt/ssd/models"
LLM_DIR="${MODEL_DIR}/llm"
# Find newest .gguf
LATEST=$(ls -1t "${MODEL_DIR}"/*.gguf | head -n1)

if [ -z "$LATEST" ]; then
  echo "No .gguf models found in ${MODEL_DIR}"
  exit 1
fi

echo "Latest model: $LATEST"
# Create llm subdir
if [ ! -d "$LLM_DIR" ]; then
  sudo mkdir -p "$LLM_DIR"
  sudo chown diane:diane "$LLM_DIR"
fi

# Create symlink
sudo ln -sf "$LATEST" "${LLM_DIR}/current_model.gguf"
sudo chown -h diane:diane "${LLM_DIR}/current_model.gguf"

echo "Symlink created: ${LLM_DIR}/current_model.gguf -> $LATEST"
echo "You can now use /mnt/ssd/models/llm/current_model.gguf as the LLM_MODEL_PATH"
