#!/usr/bin/env bash
#
# setup_01_diane_filestructure.sh
#
# Creates (or verifies) the directory layout under /mnt/ssd for Diane,
# sets ownership to the invoking user (or 'pi' if run via sudo),
# and applies sensible permissions.  Idempotent—safe to run repeatedly.
#
# Usage (on Diane, after git pull):
#   cd /home/diane/diane/scripts
#   sudo ./setup_01_diane_filestructure.sh

set -euo pipefail

# Determine the real user (so ownership is correct if run via sudo)
OWNER="${SUDO_USER:-$USER}"
GROUP="$(id -gn "$OWNER")"

SSD_BASE="/mnt/ssd"

# List of directories to create under /mnt/ssd
declare -a DIRS=(
  "models"
  "logs"
  "projects"
  "projects/Diane System"
  "voice_config"
  "voice_config/slang_modes"
  "scripts"
)

echo
echo "→ Ensuring Diane directory layout under ${SSD_BASE} ..."
for rel in "${DIRS[@]}"; do
  fullpath="${SSD_BASE}/${rel}"
  if [ ! -d "$fullpath" ]; then
    mkdir -p "$fullpath"
    echo "    Created: $fullpath"
  else
    echo "    (exists) $fullpath"
  fi
done

# Ensure a placeholder synonyms.json in voice_config/
SYNS_FILE="${SSD_BASE}/voice_config/synonyms.json"
if [ ! -f "$SYNS_FILE" ]; then
  echo "{}" > "$SYNS_FILE"
  echo "    Created placeholder: $SYNS_FILE"
else
  echo "    (exists) $SYNS_FILE"
fi

# Set ownership and permissions
echo
echo "→ Applying ownership ($OWNER:$GROUP) and permissions ..."
for rel in "${DIRS[@]}"; do
  fullpath="${SSD_BASE}/${rel}"
  chown -R "$OWNER:$GROUP" "$fullpath"
  chmod 755 "$fullpath"
done

# Fix permissions for the placeholder file
chown "$OWNER:$GROUP" "$SYNS_FILE"
chmod 644 "$SYNS_FILE"

echo
echo "✔  Done. Folder structure under ${SSD_BASE} is ready for Diane."
exit 0
