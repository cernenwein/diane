#!/usr/bin/env bash
#
# cleanup_diane_scripts.sh
#
# Moves any shell scripts in /home/diane/diane/scripts/ that do NOT
# start with "setup_diane_" into a "backup/" subdirectory.  This allows
# you to archive old or unneeded scripts without permanently deleting them.
#
# Usage (on Diane, after git pull):
#   cd /home/diane/diane/scripts
#   sudo ./cleanup_diane_scripts.sh
#
# – Assumes this script itself resides in /home/diane/diane/scripts
# – Only moves files named *.sh that do NOT begin with "setup_diane_"
# – Creates "backup/" if missing, preserves ownership/permissions.
# – Logs all moves to "cleanup.log" inside the same scripts/ folder.
#
# Idempotent: Any script already in "backup/" or already prefixed with
# "setup_diane_" is left alone.

set -euo pipefail

# Directory where this script lives (should be /home/diane/diane/scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Where to archive “old/unneeded” scripts
BACKUP_DIR="${SCRIPT_DIR}/backup"

# Log file (appends each run)
LOG_FILE="${SCRIPT_DIR}/cleanup.log"

echo
echo "→ Starting cleanup at $(date +"%Y-%m-%d %H:%M:%S")" | tee -a "$LOG_FILE"

# 1. Ensure backup/ exists
if [ ! -d "$BACKUP_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
  echo "  • Created backup folder: $BACKUP_DIR" | tee -a "$LOG_FILE"
else
  echo "  • Backup folder already exists: $BACKUP_DIR" | tee -a "$LOG_FILE"
fi

# 2. Find any *.sh in SCRIPT_DIR that do NOT start with 'setup_diane_' and are not already in backup/
echo "  • Scanning for legacy scripts to move…" | tee -a "$LOG_FILE"

shopt -s nullglob
for filepath in "$SCRIPT_DIR"/*.sh; do
  filename="$(basename "$filepath")"

  # Skip this cleanup script itself
  if [ "$filename" == "cleanup_diane_scripts.sh" ]; then
    echo "    – Skipping cleanup script itself: $filename" | tee -a "$LOG_FILE"
    continue
  fi

  # If it already lives in backup/, skip
  if [[ "$filepath" == "$BACKUP_DIR/"* ]]; then
    echo "    – Already in backup/: $filename" | tee -a "$LOG_FILE"
    continue
  fi

  # If it starts with setup_diane_, skip it
  if [[ "$filename" == setup_diane_* ]]; then
    echo "    – Reserved script (setup_diane_ prefix): $filename" | tee -a "$LOG_FILE"
    continue
  fi

  # Otherwise, move it into backup/
  mv "$filepath" "$BACKUP_DIR/"
  echo "    ✔ Moved: $filename → backup/$filename" | tee -a "$LOG_FILE"
done
shopt -u nullglob

echo "→ Cleanup complete. See $LOG_FILE for details." | tee -a "$LOG_FILE"
echo
exit 0
