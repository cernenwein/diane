#!/bin/bash

# Diane Git Repo Cleanup & Validation Script



echo "🔍 Cleaning up unnecessary files..."

# 1. Remove common unneeded files
rm -rf __pycache__ *.pyc *.log *.wav *.zip *.bak *.tmp diane_setup.log \
       voice_llama_chat.bak test_audio* sandbox diane_final_* old_* \
       *.egg-info .pytest_cache

# 2. Flag anything suspicious
echo "🔎 Checking for unexpected files..."
KNOWN_FILES=(
    "voice_llama_chat.py"
    "README.md"
    ".gitignore"
    "modules/"
    "services/"
    "config/"
    "requirements.txt"
    "LICENSE"
)

for file in $(find . -maxdepth 1 -type f); do
    fname=$(basename "$file")
    if [[ ! " ${KNOWN_FILES[*]} " =~ " $fname " ]]; then
        echo "⚠️  Unknown file: $fname"
    fi
done

# 3. Stage and commit clean state
git add -A
git commit -m "🧹 Cleaned repository: removed unneeded files and standardized contents"
git push origin main

echo "✅ Repo cleaned and synced to GitHub."
