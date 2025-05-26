#!/bin/bash
set -e

echo "[Creating SSD target directory]"
mkdir -p /mnt/ssd/diane_data

echo "[Moving Diane folders to SSD and symlinking]"

for dir in \
  diane_core_knowledge \
  diane_logs \
  diane_models \
  diane_personality_profiles \
  diane_plugins \
  diane_projects \
  diane_updated_bundle \
  models \
  piper; do

  if [ -d "$HOME/$dir" ]; then
    echo "  Moving $dir..."
    mv "$HOME/$dir" "/mnt/ssd/diane_data/$dir"
    ln -s "/mnt/ssd/diane_data/$dir" "$HOME/$dir"
  else
    echo "  Skipping $dir (not found)"
  fi
done

echo "[All selected directories have been moved to the SSD and symlinked.]"
