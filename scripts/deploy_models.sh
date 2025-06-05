#!/bin/bash
#
# deploy_models.sh
# Copies models from Git (or downloads via HF CLI) into /mnt/ssd/models.
#

# 1. Fetch updated models via Hugging Face CLI
/home/diane/diane/scripts/hf_pull_models.sh

# 2. (Optional) Copy any local models committed in Git into SSD
#    For example, if you store small “example” files in Git:
# cp -r /home/diane/diane/models/hotword /mnt/ssd/models/

# 3. Ensure ownership/permissions
sudo chown -R diane:diane /mnt/ssd/models
sudo chmod -R 755 /mnt/ssd/models

echo "Deployment complete."
