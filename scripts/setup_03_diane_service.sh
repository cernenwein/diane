#!/usr/bin/env bash
#
# setup_03_diane_service.sh
#
# Finds all *.service files in the Diane repository, installs them into /etc/systemd/system/,
# reloads systemd, and enables+starts (or restarts) each service. Idempotent—safe to run repeatedly.
#
# Usage (on Diane, after git pull):
#   cd /home/diane/diane/scripts
#   sudo ./setup_03_diane_service.sh

set -euo pipefail

### 1. Determine paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SYSTEMD_DIR="/etc/systemd/system"

echo
echo "→ Installing/updating any *.service files from repo into ${SYSTEMD_DIR} ..."
echo

# 2. Find all .service files in the repo
mapfile -t SERVICE_FILES < <(find "$REPO_ROOT" -maxdepth 3 -type f -name "*.service")

if [ "${#SERVICE_FILES[@]}" -eq 0 ]; then
  echo "⚠️  No .service files found under ${REPO_ROOT}. Nothing to install."
  exit 0
fi

# 3. Copy each .service file to /etc/systemd/system/
for SERVICE_PATH in "${SERVICE_FILES[@]}"; do
  SERVICE_NAME="$(basename "$SERVICE_PATH")"
  DEST_PATH="${SYSTEMD_DIR}/${SERVICE_NAME}"

  echo "  • Installing ${SERVICE_NAME} → ${DEST_PATH}"
  cp "$SERVICE_PATH" "$DEST_PATH"
  chmod 644 "$DEST_PATH"
  chown root:root "$DEST_PATH"
done

# 4. Reload systemd daemon to pick up new/changed unit files
echo
echo "→ Reloading systemd daemon..."
systemctl daemon-reload

# 5. Enable & (re)start each service
echo
echo "→ Enabling and starting/restarting services..."
for SERVICE_PATH in "${SERVICE_FILES[@]}"; do
  SERVICE_NAME="$(basename "$SERVICE_PATH")"

  # Enable the service (idempotent even if already enabled)
  if systemctl is-enabled --quiet "$SERVICE_NAME"; then
    echo "    • ${SERVICE_NAME} is already enabled → reenabling (no-op)."
    systemctl enable "$SERVICE_NAME" --now
  else
    echo "    • Enabling ${SERVICE_NAME} ..."
    systemctl enable "$SERVICE_NAME" --now
  fi

  # Restart if already running, otherwise just start
  if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "    • ${SERVICE_NAME} is active → restarting to pick up changes..."
    systemctl restart "$SERVICE_NAME"
  else
    echo "    • ${SERVICE_NAME} is not active → starting..."
    systemctl start "$SERVICE_NAME"
  fi
done

# 6. Print a short status check for each service
echo
echo "→ Service statuses:"
for SERVICE_PATH in "${SERVICE_FILES[@]}"; do
  SERVICE_NAME="$(basename "$SERVICE_PATH")"
  STATUS="$(systemctl is-active "$SERVICE_NAME")"
  echo "    • ${SERVICE_NAME}: ${STATUS}"
done

echo
echo "✔  Done. All *.service units from the repo are installed, enabled, and running (if valid)."
exit 0
