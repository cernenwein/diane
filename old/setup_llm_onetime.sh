#!/bin/bash
set -e

MARKER_FILE="$HOME/.diane_setup_complete"

if [ -f "$MARKER_FILE" ]; then
  echo "=== Diane one-time setup already completed. Skipping. ==="
  exit 0
fi

echo "=== Cloning and building llama.cpp (if not already present) ==="
if [ ! -d "$HOME/llama.cpp" ]; then
  git clone https://github.com/ggerganov/llama.cpp $HOME/llama.cpp
  mkdir -p $HOME/llama.cpp/build && cd $HOME/llama.cpp/build
  cmake ..
  make -j4
fi

echo "=== Downloading 3B model to ~/models (if missing) ==="
mkdir -p ~/models/mistral3b
cd ~/models/mistral3b
if [ ! -f "mistral-3b-instruct-v0.1.Q4_K_M.gguf" ]; then
  wget https://huggingface.co/TheBloke/Mistral-3B-Instruct-v0.1-GGUF/resolve/main/mistral-3b-instruct-v0.1.Q4_K_M.gguf
fi

echo "=== Installing Piper and downloading voice model (if missing) ==="
if [ ! -d "$HOME/piper" ]; then
  git clone https://github.com/rhasspy/piper.git $HOME/piper
  mkdir -p $HOME/piper/build && cd $HOME/piper/build
  cmake ..
  make -j4
fi

mkdir -p ~/piper/voices/en_US
cd ~/piper/voices/en_US
if [ ! -f "en_US-amy-low.onnx" ]; then
  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy-low/en_US-amy-low.onnx
  wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy-low/en_US-amy-low.onnx.json
fi

echo "=== Marking one-time setup as complete ==="
touch "$MARKER_FILE"
