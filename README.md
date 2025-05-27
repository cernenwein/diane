# Diane: Portable Raspberry Pi Voice Assistant

## Overview
Diane is a locally run, voice-controlled AI assistant powered by LLMs and voice models.
This repository contains installation scripts, audio and Bluetooth configuration, and test tools.

## Setup Instructions
1. Run `install_phase_1.sh` for base packages and system config.
2. Run `install_phase_2.sh` for voice + LLM setup.
3. Scripts in `bluetooth/` allow pairing and audio routing.
4. Use `test/` to verify mic and speaker are working.

## Notes
- Data is stored on `/mnt/ssd/diane_data`
- Diane autostarts on boot, listens for the 'Diane' hotword
- Fully offline operation is supported
