# `INSTRUCTIONS.md`
**Project: Diane – Voice Assistant on Raspberry Pi 5**  
**Owner:** [User]  
**Version:** 1.0  
**Last Updated:** 2025-06-03  

---

## 🧠 Project Overview

**Diane** is a custom voice assistant running fully offline on a Raspberry Pi 5 (8GB) using open-source speech-to-text, LLM inference, and text-to-speech. The assistant is designed for privacy, reliability, and modularity, supporting voice control, memory, RAG (Retrieval-Augmented Generation), and embedded hardware interfacing.

---

## 🛠️ Hardware Setup

- **Mainboard:** Raspberry Pi 5 (8GB)
- **Case:** GeeekPi NVMe Aluminum Case with heatsink/fan
- **Storage:** NVMe SSD via PCIe (mounted at `/mnt/ssd`)
- **Audio In:** SunFounder USB 2.0 Mini Microphone (M-305)
- **Audio Out:**  
  - DEWALT DPG17 Bluetooth Hearing Protection (auto-preferred)
  - Mini metal internal speaker + PAM8302 mono amp (backup)
- **Additional I/O:**  
  - Sabrent USB audio adapter (no longer used – deprecated)  
  - JLab GO Air Sport Bluetooth earbuds (optional fallback)

---

## 🧩 Core Software Stack

| Component             | Purpose                      | Toolchain Used                        |
|----------------------|------------------------------|---------------------------------------|
| **STT**              | Voice-to-text                | Silero VAD + Whisper (local)          |
| **LLM**              | Chat + Reasoning             | `DavidAU/L3.2-Rogue-Creative...` GGUF |
| **TTS**              | Text-to-speech               | Piper (`en_US-amy-medium.onnx`)       |
| **Wake Word**        | Voice activation             | `Diane` (custom, tuned sensitivity)   |
| **RAG Engine**       | Context retrieval            | Local file indexing (text + PDF)      |
| **Memory**           | Persistent profile system    | Structured by "Projects"              |
| **Web Dashboard**    | Optional GUI & log viewer    | Custom Flask-based interface          |

---

## 🔁 Boot & Auto-Import Behavior

On boot:
- Mount SSD to `/mnt/ssd`
- Import known Bluetooth devices (e.g. DEWALT DPG17)
- Auto-load core models (STT, LLM, TTS)
- Resume previous state (active project, logs)
- Run time sync check silently (NTP)
- Load `voice_llama_chat.py` and begin passive wake-word listening

---

## 📁 Folder Structure (on `/mnt/ssd`)

```
/mnt/ssd/
├── models/                      # GGUF and ONNX models
├── logs/                        # Rotated daily logs (buffered to RAM, log2ram)
├── projects/                    # Long-term memory by project
│   └── Diane System/            # Core config decisions
├── voice_config/
│   ├── synonyms.json            # Voice command synonym table
│   ├── slang_modes/             # Voice style variations (e.g. Shakespearean)
├── scripts/
│   └── XX_setup_diane_*.sh      # Setup automation scripts
```

---

## 🎙️ Supported Voice Commands (Examples)

- “**Diane, what’s your status?**”  
- “**Optimize system performance.**”
- “**Connect to DEWALT headset.**”
- “**Commit that to long-term memory.**”
- “**Re-index all documents.**”
- “**Switch to Shakespeare mode.**”
- “**Encrypt everything now.**”
- “**What’s the elevator pitch?**” *(normal or technical)*

All commands support synonyms. New ones can be added live.

---

## 🔐 Security Features

- Full offline capability
- Lightweight encryption for sensitive folders
- Voice-triggered encryption/decryption with passphrase prompt at startup
- “Temporary chat mode” wipes logs and memory on exit
- Modular control system locked by project priority

---

## 🧠 LLM/Expert Assistant Guidelines

### 📌 Always:

- Check that `voice_llama_chat.py` is synced to the GitHub canonical version.
- Use `XX_setup_diane_` prefixes when adding install/config scripts.
- Keep config files in `/mnt/ssd/voice_config/`
- Document changes in `Diane System` project memory.

### ⚠️ Never:

- Write to root folders outside `/mnt/ssd/`
- Use Sabrent AU-MMSA for audio — deprecated
- Assume online connectivity unless explicitly verified

---

## ✅ Onboarding Checklist for New Copilots or LLMs

- [ ] Confirm SSD mounted to `/mnt/ssd`
- [ ] Confirm models present in `/mnt/ssd/models`
- [ ] Confirm `voice_llama_chat.py` reflects latest GitHub version
- [ ] Validate `en_US-amy-medium.onnx` for TTS is available
- [ ] Sync known Bluetooth audio devices
- [ ] Load `Diane System` project memory and review current personality config
- [ ] Check and buffer logs to RAM (`log2ram`)
- [ ] Confirm voice command parsing and synonym tables are functional


# INSTRUCTIONS.md

These instructions assume you have already created a user called `diane` on your Raspberry Pi 5, and that you will run Diane under that account.  All paths are relative to `/home/diane/diane` unless otherwise noted.

---

## 1. Clone the Diane repository

```bash
# On your Ubuntu dev, you already have a `diane/` repo. Push commits to GitHub:
git push origin main

# On Diane (Raspberry Pi), SSH in and clone (if not already done):
cd /home/diane
git clone https://github.com/cernenwein/diane.git
cd diane
