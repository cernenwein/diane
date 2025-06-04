# TO-DO.md

_This file outlines every setup task—manual and automated—needed to get Diane fully operational. Place it at the repository root so it’s always available for reference._

---

## 1. Clone & Pull Repository

1. **On your Ubuntu development machine**
   - Ensure all changes are committed and pushed:
     ```bash
     cd /path/to/local/diane
     git add .
     git commit -m "Sync to GitHub"
     git push origin main
     ```
2. **On Diane (Raspberry Pi)**
   - SSH in as the `diane` user:
     ```bash
     ssh diane@<pi-address>
     ```
   - If not already cloned:
     ```bash
     cd /home/diane
     git clone https://github.com/cernenwein/diane.git
     cd diane
     ```
   - If already cloned:
     ```bash
     cd /home/diane/diane
     git pull origin main
     ```

---

## 2. System Packages & OS Prerequisites

1. **Update & Upgrade**
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   ```
2. **Python 3.11 & Virtualenv Prereqs**
   - Verify Python version:
     ```bash
     python3 --version
     ```
   - If older than 3.11:
     ```bash
     sudo apt install -y python3.11 python3.11-venv python3.11-dev
     ```
3. **Install Required Debian Packages**
   ```bash
   sudo apt install -y      git      libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0      alsa-utils pulseaudio alsa-plugins      bluetooth bluez bluez-tools      ffmpeg      pyaudio      python3-pip      expressvpn
   ```
   - Include `expressvpn` after installing its `.deb` from ExpressVPN’s website.
4. **Enable & Start Bluetooth Service**
   ```bash
   sudo systemctl enable bluetooth
   sudo systemctl start bluetooth
   ```
5. **Verify Audio Configuration**
   - Confirm `/etc/asound.conf` is present and correct for your DAW or ALSA devices.
   - List audio devices to confirm:
     ```bash
     arecord -l
     aplay -l
     ```
6. **Verify**
   - Check Python version: `python3 --version`
   - Confirm commands: `git`, `ffmpeg`, `expressvpn`, `pactl` (PulseAudio), `arecord`, `aplay`.

---

## 3. Configure Virtual Environment

1. **Create & Activate venv** (inside repo)
   ```bash
   cd /home/diane/diane
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   ```
2. **Auto-Activate on Shell Login**
   - Edit `/home/diane/.bashrc`:
     ```bash
     nano ~/.bashrc
     ```
   - Append:
     ```bash
     # ─────────── Activate Diane’s venv ───────────
     if [ -f "$HOME/diane/diane/.venv/bin/activate" ]; then
       source "$HOME/diane/diane/.venv/bin/activate"
     fi
     # ────────────────────────────────────────────────
     ```
   - Save & exit, then:
     ```bash
     source ~/.bashrc
     ```
   - Verify: `which pip` → `/home/diane/diane/.venv/bin/pip`

---

## 4. Install Python Dependencies

1. **Install from requirements.txt**
   ```bash
   pip install -r requirements.txt
   ```
2. **Ensure additional packages are installed:**
   ```bash
   pip install      pvporcupine      webrtcvad      pyaudio      numpy      sounddevice      openai-whisper      llama-cpp-python      piper-tts
   ```
3. **Verify**
   ```bash
   pip show pvporcupine webrtcvad sounddevice whisper llama_cpp piper_tts
   ```

---

## 5. Setup `/mnt/ssd` File Structure

1. **Run setup script**
   ```bash
   cd /home/diane/diane/scripts
   sudo ./setup_01_diane_filestructure.sh
   ```
   - Creates:
     ```
     /mnt/ssd/
     ├── models/
     ├── logs/
     ├── projects/
     │   └── Diane System/
     ├── voice_config/
     │   ├── synonyms.json
     │   ├── slang_modes/
     │   └── approved_networks.txt
     ├── tmp/
     └── whisper_cache/
     ```
   - Ownership set to `diane`, permissions correct.
2. **Verify**
   ```bash
   ls -R /mnt/ssd
   ```
   Confirm `models`, `logs`, `voice_config/`, `tmp/`, and `whisper_cache/` exist.

---

## 6. Download & Place Models

> Some models require manual download; others are automated.

### 6.1 LLM Model (manual)

1. **Download a GGML model**, for example:
   ```
   https://huggingface.co/DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF/resolve/main/ggml-7B-quantized.bin
   ```
2. **Move it to** `/mnt/ssd/models/`:
   ```bash
   cd /mnt/ssd/models
   sudo wget -O ggml-diane-7b.bin      https://huggingface.co/DavidAU/L3.2-Rogue-Creative-Instruct-Uncensored-Abliterated-7B-GGUF/resolve/main/ggml-7B-quantized.bin
   ```
3. **Verify**
   ```bash
   ls -lh /mnt/ssd/models/ggml-diane-7b.bin
   ```

### 6.2 Porcupine Wake‐Word Model (manual)

1. **Obtain or train** the “Diane” `.ppn` file; place at:
   ```
   /mnt/ssd/models/hotword/porcupine_diane.ppn
   ```
2. **Verify**
   ```bash
   ls -lh /mnt/ssd/models/hotword/porcupine_diane.ppn
   ```

### 6.3 VAD Model (WebRTC VAD uses embedded code)

- **No external download** required; handled by library.

### 6.4 Piper TTS Model (automated)

1. **Run setup script**
   ```bash
   cd /home/diane/diane/scripts
   sudo ./setup_02_diane_tts_model.sh
   ```
   - Downloads:
     ```
     /mnt/ssd/models/tts/en_US-amy-medium.onnx
     /mnt/ssd/models/tts/en_US-amy-medium.onnx.json
     ```
2. **Verify**
   ```bash
   ls -lh /mnt/ssd/models/tts/en_US-amy-medium.onnx          /mnt/ssd/models/tts/en_US-amy-medium.onnx.json
   ```

---

## 7. Populate Voice Configuration

1. **Synonyms JSON**
   ```bash
   nano /mnt/ssd/voice_config/synonyms.json
   ```
   - Example:
     ```json
     {
       "info": ["information", "details"],
       "weather": ["forecast", "climate"]
     }
     ```

2. **Slang Modes**
   - Create files under `/mnt/ssd/voice_config/slang_modes/`, e.g. `90s.json`:
     ```bash
     nano /mnt/ssd/voice_config/slang_modes/90s.json
     ```
   - Example:
     ```json
     {
       "cool": "rad",
       "hello": "yo"
     }
     ```

3. **Approved Networks**
   - Create `/mnt/ssd/voice_config/approved_networks.txt`:
     ```bash
     nano /mnt/ssd/voice_config/approved_networks.txt
     ```
   - Format: `SSID,Password` per line, for example:
     ```
     HomeNetwork,MyHomePass123
     OfficeWiFi,OfficePass!
     MobileHotspot,12345678
     ```
   - Set ownership and permissions:
     ```bash
     sudo chown diane:diane /mnt/ssd/voice_config/approved_networks.txt
     chmod 644 /mnt/ssd/voice_config/approved_networks.txt
     ```

---

## 8. Create & Populate Bluetooth Trusted Devices

1. **Create or edit** the file:
   ```bash
   nano /home/diane/diane/bluetooth_trusted_devices.txt
   ```
   - One MAC address per line, e.g.:
     ```
     AA:BB:CC:DD:EE:FF
     11:22:33:44:55:66
     ```
2. **Enable & start the service** (via setup script):
   ```bash
   cd /home/diane/diane/scripts
   sudo ./setup_03_diane_service.sh
   ```
3. **Verify**
   ```bash
   sudo systemctl status bluetooth-trusted.service
   ```

---

## 9. Install & Configure ExpressVPN

1. **Download the ExpressVPN Debian package** from ExpressVPN’s site and install:
   ```bash
   cd /home/diane/Downloads
   sudo dpkg -i expressvpn_*.deb
   sudo apt-get install -f
   ```
2. **Log in**
   ```bash
   expressvpn login
   ```
   - Follow prompts to enter activation code or credentials.
3. **Verify**
   ```bash
   expressvpn status
   ```
4. **Test CLI**
   ```bash
   expressvpn connect us
   expressvpn status
   expressvpn disconnect
   expressvpn status
   ```

---

## 10. SSD Swapfile Setup

1. **Run `setup_04_diane_swap.sh`**:
   ```bash
   cd /home/diane/diane/scripts
   sudo ./setup_04_diane_swap.sh
   ```
   - Creates or reuses `/mnt/ssd/swapfile` (8 GB), enables swap, and adds to `/etc/fstab`.
2. **Verify**
   ```bash
   sudo swapon --show
   free -h
   ```
3. **Remove any old swap** if needed:
   ```bash
   sudo swapoff /swapfile
   sudo swapoff /var/swap
   sudo rm /swapfile
   sudo rm /var/swap
   sudo sed -i '/\/swapfile/d' /etc/fstab
   sudo sed -i '/\/var\/swap/d' /etc/fstab
   sudo swapon --show
   free -h
   ```

---

## 11. SSD Storage for Temporary Files & Whisper Cache

1. **Create SSD temp/cache directories**
   ```bash
   sudo mkdir -p /mnt/ssd/tmp
   sudo mkdir -p /mnt/ssd/whisper_cache
   sudo chown -R diane:diane /mnt/ssd/tmp /mnt/ssd/whisper_cache
   chmod 755 /mnt/ssd/tmp /mnt/ssd/whisper_cache
   ```
2. **Behavior**
   - The script writes recorded audio to `/mnt/ssd/tmp/diane_input.wav`.
   - Whisper stores its model cache under `/mnt/ssd/whisper_cache`.

---

## 12. Systemd Service Setup

1. **Ensure service files** in `diane/services/`:
   - `voice_llama_chat.service`
   - `bluetooth-trusted.service`
2. **Run service setup script**
   ```bash
   cd /home/diane/diane/scripts
   sudo ./setup_03_diane_service.sh
   ```
   - Copies `*.service` to `/etc/systemd/system/`, reloads systemd, enables & starts services.
3. **Verify**
   ```bash
   sudo systemctl status voice_llama_chat.service
   sudo systemctl status bluetooth-trusted.service
   expressvpn status
   ```
4. **Inspect Logs** (if needed)
   ```bash
   sudo journalctl -u voice_llama_chat.service -f
   sudo journalctl -u bluetooth-trusted.service -f
   ```

---

## 13. Final Verification & Testing

1. **Manual Run** (debug):
   ```bash
   cd /home/diane/diane
   source .venv/bin/activate
   python3 voice_llama_chat.py --audio-input 1 --audio-output 0
   ```
   - Say “Diane” to trigger wake word.
   - Test built‐in commands:
     - “Diane, connect wifi HomeNetwork MyHomePass123”
     - “Diane, disconnect wifi HomeNetwork”
     - “Diane, trust device AA:BB:CC:DD:EE:FF”
     - “Diane, set slang mode 90s”
     - “Diane, connect vpn us”
     - “Diane, disconnect vpn”
   - Ask a general question and verify LLM response & TTS playback.
2. **Service Run**
   ```bash
   sudo systemctl enable voice_llama_chat.service
   sudo systemctl start voice_llama_chat.service
   ```
   - Check logs:
     ```bash
     sudo journalctl -u voice_llama_chat.service -f
     ```
3. **Wi-Fi Reconnection Test**
   - Disconnect existing network; Diane should log reconnection attempts and connect to an approved SSID.
   - Modify `/mnt/ssd/voice_config/approved_networks.txt` and reboot to test new entries.
4. **ExpressVPN Test via Service**
   - Speak “Diane, connect vpn uk” to switch to a UK server; confirm IP change.
   - Say “Diane, disconnect vpn” to disconnect.

---

## 14. Remaining Manual Tasks

1. **Obtain Porcupine `.ppn` Wake‐Word Model**
   - If you don’t have one, create on Picovoice console, download, and place at:
     ```
     /mnt/ssd/models/hotword/porcupine_diane.ppn
     ```
2. **Populate Slang Mode JSON Files**
   - Create and customize files under:
     ```
     /mnt/ssd/voice_config/slang_modes/<mode>.json
     ```
   - Each should map words/phrases to slang equivalents.
3. **Edit `synonyms.json`** (if needed)
   - Add synonyms mappings:
     ```json
     {
       "weather": ["forecast", "temperature", "climate"],
       "time": ["clock", "hour", "minute"]
     }
     ```
4. **Find & Note Audio Device Indices**
   - Enumerate devices:
     ```bash
     python3 - <<EOF
     import pyaudio
     pa = pyaudio.PyAudio()
     for i in range(pa.get_device_count()):
         print(i, pa.get_device_info_by_index(i)["name"])
     pa.terminate()
     EOF
     ```
   - Use indices with `--audio-input` and `--audio-output`.

---

## 15. Notes & Troubleshooting

- **PEP 668 “externally-managed-environment” pip errors**
  → Ensure `source .venv/bin/activate` before any `pip install`.
- **Porcupine requires 16 kHz, 16-bit PCM**  
  → Use a compatible microphone or resample if necessary.
- **Whisper model download (~1.4GB)**  
  → Ensure ≥2GB free under `/mnt/ssd/whisper_cache`.
- **Memory usage**  
  → A 7B GGML model uses ~4GB. If Diane crashes, switch to a smaller LLM.
- **Swapfile on SSD**  
  → Provides extra memory; the script creates an 8GB swap on `/mnt/ssd/swapfile`.
- **Bluetooth auto-trust**  
  → One-shot service runs at startup; voice commands append MACs to `bluetooth_trusted_devices.txt`.
- **Slang application**  
  → Currently loads JSON but does not transform text. Implement `apply_slang()` as needed.
- **Systemd logs**
  → Use `sudo journalctl -u voice_llama_chat.service -f` for realtime logs.

---

_End of TO-DO.md_
