#!/bin/bash
MODEL_ID="DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF"
MODEL_FILENAME="L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B.Q4_K_M.gguf"
TOKEN_FILE="$HOME/.huggingface/token"
MODEL_DIR="$HOME/diane_models"

mkdir -p "$MODEL_DIR"

if [ ! -f "$TOKEN_FILE" ]; then
  echo "Hugging Face token file not found at $TOKEN_FILE"
  echo "Please create it and paste your token inside."
  exit 1
fi

TOKEN=$(cat "$TOKEN_FILE")

echo "Downloading $MODEL_FILENAME from $MODEL_ID..."
curl -L -H "Authorization: Bearer $TOKEN" \
     -o "$MODEL_DIR/$MODEL_FILENAME" \
     "https://huggingface.co/$MODEL_ID/resolve/main/$MODEL_FILENAME"

if [ $? -eq 0 ]; then
  echo "Model downloaded successfully to $MODEL_DIR/$MODEL_FILENAME"
else
  echo "Download failed. Please check your token or internet connection."
fi
