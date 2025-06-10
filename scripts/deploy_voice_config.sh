#!/usr/bin/env bash
#
# deploy_voice_config.sh
#
# Copy voice_config files from the Git repo into /mnt/ssd/voice_config.
#

set -e

REPO_VC="/home/diane/diane/voice_config"
SSD_VC="/mnt/ssd/voice_config"

echo "Deploying voice_config from $REPO_VC → $SSD_VC..."

# 1. Ensure SSD voice_config directory exists
sudo mkdir -p "${SSD_VC}"
sudo chown diane:diane "${SSD_VC}"
chmod 755 "${SSD_VC}"

# 2. Copy everything under repo/voice_config into SSD
#    (preserves subfolders like slang_modes/)
rsync -av --delete "${REPO_VC}/" "${SSD_VC}/"

# 3. Fix ownership/permissions recursively
sudo chown -R diane:diane "${SSD_VC}"
find "${SSD_VC}" -type d -exec chmod 755 {} \;
find "${SSD_VC}" -type f -exec chmod 644 {} \;

echo "voice_config deployed."
