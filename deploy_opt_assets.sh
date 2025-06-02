#!/bin/bash

# Deploy Diane's /opt files from /opt_copy
# This script assumes you run it from inside the /opt_copy folder.

echo "🚚 Moving Diane's /opt files into place..."

# Create destination directories if they don't exist
sudo mkdir -p /opt/diane
sudo mkdir -p /opt/diane/modules
sudo mkdir -p /opt/diane/config
sudo mkdir -p /opt/diane/personality
sudo mkdir -p /opt/diane/projects
sudo mkdir -p /opt/diane/models

# Copy relevant files and folders
if [ -d "modules" ]; then
    sudo cp -r modules/* /opt/diane/modules/
fi

if [ -f "wifi_connections.json" ]; then
    sudo cp wifi_connections.json /opt/diane/
fi

if [ -f "memory.json" ]; then
    sudo cp memory.json /opt/diane/
fi

if [ -f "personality.json" ]; then
    sudo cp personality.json /opt/diane/
fi

echo "✅ Files moved successfully to /opt/diane/"
