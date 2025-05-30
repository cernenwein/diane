#!/bin/bash

# Diane Git Repo Cleanup & Validation Script


echo "🔍 Cleaning up unnecessary files and directories..."

# 1. Remove common unneeded files and directories
rm -rf __pycache__ *.pyc *.log *.wav *.zip *.bak *.tmp *.egg-info .pytest_cache
rm -rf diane_setup.log voice_llama_chat.bak test_audio* sandbox diane_final_* old_*        archive/ dist/ build/ .mypy_cache/ .coverage htmlcov/ __snapshots__/

# 2. Remove orphaned directories that aren't part of the official structure
for dir in */; do
  case "$dir" in
    modules/|services/|config/|.git/|.github/)
      ;;
    *)
      echo "⚠️  Unknown directory: $dir"
      ;;
  esac
done

# 3. Flag anything suspicious at the top level
echo "🔎 Checking for unexpected top-level files..."
KNOWN_FILES=(
    "voice_llama_chat.py"
    "README.md"
    ".gitignore"
    "requirements.txt"
    "LICENSE"
)

for file in $(find . -maxdepth 1 -type f); do
    fname=$(basename "$file")
    if [[ ! " ${KNOWN_FILES[*]} " =~ " $fname " ]]; then
        echo "⚠️  Unknown file: $fname"
    fi
done

# 4. Stage and commit clean state
git add -A
git commit -m "🧹 Cleaned repository: removed unneeded files and standardized contents"
git push origin main

echo "✅ Repo cleaned and synced to GitHub."
