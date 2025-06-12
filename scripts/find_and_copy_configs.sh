#!/usr/bin/env bash
#
# find_and_copy_configs.sh
# Searches /home/diane for the largest 
# approved_networks.txt, synonyms.json, and bluetooth_trusted_devices.txt,
# then copies each into /mnt/ssd/voice_config/ replacing placeholders.
#
# Usage: sudo ./find_and_copy_configs.sh

set -euo pipefail

CONFIG_DIR="/mnt/ssd/voice_config"
FILES=("approved_networks.txt" "synonyms.json" "bluetooth_trusted_devices.txt")

echo "Ensuring CONFIG_DIR exists: $CONFIG_DIR"
mkdir -p "$CONFIG_DIR"
chown diane:diane "$CONFIG_DIR"
chmod 755 "$CONFIG_DIR"

for filename in "${FILES[@]}"; do
  echo "----------------------------------------"
  echo "Processing $filename"

  # Find candidate files under /home/diane, excluding SSD mount
  mapfile -t candidates < <(
    find /home/diane -type f -name "$filename"       ! -path "/mnt/ssd/*" 2>/dev/null       -printf "%s %p
" | sort -nr
  )

  if [ ${#candidates[@]} -eq 0 ]; then
    echo "  No candidates found for $filename under /home/diane"
    continue
  fi

  # Take the largest file
  largest_entry="${candidates[0]}"
  largest_path="${largest_entry#* }"
  size="${largest_entry%% *}"

  echo "  Found candidate: $largest_path (size: $size bytes)"
  echo "  Copying to $CONFIG_DIR/$filename"
  cp "$largest_path" "$CONFIG_DIR/$filename"
  chown diane:diane "$CONFIG_DIR/$filename"
  chmod 644 "$CONFIG_DIR/$filename"
done

echo "----------------------------------------"
echo "Final content of $CONFIG_DIR:"
ls -l "$CONFIG_DIR"
