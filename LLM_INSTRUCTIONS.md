LLM instructions for use in AI coding

all variables that might change, like file locations of files shound be updates, stored and referenced in https://github.com/cernenwein/diane/blob/main/.env 

target code should be designed to run on a Raspberry Pi 5 with 8GB ram

new .gguf model file into /mnt/ssd/models/sudo systemctl restart voice_llama_chat.service diane_web.service
Example filename: L3.2-Rogue-Creative-Instruct-7B-D_AU-Q4_k_m_v2.gguf

We are using services via systemctl
- voice_llama_chat.service 
- diane_web.service

LLM_INSTRUCTIONS.md

System Instructions for Diane's ChatGPT LLM Instances

This document should be read or injected as the initial prompt for any new ChatGPT (or other LLM) session powering Diane’s conversational and voice assistant functionality.

1. Environment Variables

All runtime configuration is centralized in a .env file at /home/diane/diane/.env. Ensure this file is loaded before any script or service starts.

Key variables:

LLM_MODEL_PATH — /mnt/ssd/models/llm/current_model.gguf

TTS_MODEL_PATH — /mnt/ssd/models/tts/en_US-amy-medium.onnx

HOTWORD_MODEL_PATH — /mnt/ssd/models/hotword/precise_diane.pb

SYNONYMS_PATH — /mnt/ssd/voice_config/synonyms.json

APPROVED_NETWORKS_PATH — /mnt/ssd/voice_config/approved_networks.txt

BLUETOOTH_TRUSTED_PATH — /mnt/ssd/voice_config/bluetooth_trusted_devices.txt

WEB_API_KEY — secret key for HTTP /query endpoint

WEB_PORT — port for web interface (default 8080)

VAD_MODE — WebRTC VAD aggressiveness level

AUDIO_INPUT / AUDIO_OUTPUT — ALSA device indices or -1 for none

Loading .env:

Bash scripts:

set -a
source /home/diane/diane/.env
set +a

Python scripts:

from dotenv import load_dotenv
load_dotenv('/home/diane/diane/.env')

systemd units:

EnvironmentFile=/home/diane/diane/.env

2. Model Loading and Verification

On startup, the LLM entrypoint (voice_llama_chat.py or web-only diane_web.py) must:

Read LLM_MODEL_PATH from the environment.

Verify the model file exists (verify_file() utility).

Load the model via llama-cpp-python (or the configured adapter).

Stable symlink:

Use setup_06_diane_llm_symlink.sh to maintain /mnt/ssd/models/llm/current_model.gguf pointing to the newest .gguf.

3. Voice and Audio Pipeline

The full voice assistant leverages:

Hotword detection (PreciseEngine) via HOTWORD_MODEL_PATH.

VAD (webrtcvad) configured by VAD_MODE.

ASR by Whisper, using cache directory /mnt/ssd/whisper_cache.

Text generation by the LLM defined above.

TTS by Piper through TTS_MODEL_PATH.

The service must ensure:

Correct shebang (#!/home/diane/diane/.venv/bin/python3).

Flask web server runs in the foreground (blocking call) under systemd.

4. Service Units and Execution

voice_llama_chat.service: full voice assistant + web API.

diane_web.service: web-only interface (no audio), reading same .env.

Ensure each unit file:

Uses ExecStart=/home/diane/diane/.venv/bin/python3 /home/diane/diane/<script>.py.

Has EnvironmentFile=/home/diane/diane/.env up top (or individual Environment= lines).

Has Restart=on-failure and appropriate After= for network/DBus.

5. Model Update Workflow

When upgrading to a new LLM model:

Upload the new .gguf into /mnt/ssd/models/.

Run:

sudo /home/diane/diane/scripts/setup_06_diane_llm_symlink.sh

Reload & restart services:

sudo systemctl daemon-reload
sudo systemctl restart voice_llama_chat.service diane_web.service

Verify via logs:

sudo journalctl -u voice_llama_chat.service -n20

Look for the “LLM model found:” line referencing the new path.

6. Configuration File Deployment

Root-level templates (e.g., synonyms.json, approved_networks.txt, bluetooth_trusted_devices.txt) are deployed to SSD by:

/home/diane/diane/scripts/deploy_voice_config.sh

Ensure those files are filled in at the repo root before deployment.

By following this document, any new ChatGPT/LLM instance launched for Diane will have consistent access to the correct models, configurations, and runtime settings without manual path edits.

7. Hardware, OS, and System Configuration

Diane runs on a Raspberry Pi 4–class system with the following baseline configuration:

Operating System: Debian GNU/Linux 12 (Bookworm) aarch64, Kernel 6.12.25+rpt-rpi-2712

Storage:

Root filesystem: microSD (/dev/mmcblk0p2)

High–speed NVMe SSD: mounted at /mnt/ssd, used for models, swap, caches, and logs

Memory & Swap:

8 GiB RAM; 8 GiB SSD swap file at /mnt/ssd/swapfile; zram 256 MiB partition; /var/swap 512 MiB

Audio:

ALSA configured via /etc/asound.conf; default .service units run without a display or DBus session

Networking:

Wi‑Fi credentials from /mnt/ssd/voice_config/approved_networks.txt

Bluetooth trusted devices in /mnt/ssd/voice_config/bluetooth_trusted_devices.txt

ExpressVPN (if enabled) via your custom VPN service unit

User & Permissions:

All services run under the diane user

Key directories (models, configs, scripts) owned by diane:diane with strict permissions (600 or 644)

System Services:

Use systemd units for voice, web, Bluetooth reconnect, and health checks

Ensure network-online.target is used where necessary

Keep these hardware and OS details in mind when troubleshooting, adding drivers, or changing low‑level system settings.


The database of record will be github in https://github.com/cernenwein/diane
Diane is the name of the Pi, and files will be clones from github into /home/diane/diane as a way of transfering files to diane






