#!/home/diane/diane/.venv/bin/python3
"""
voice_llama_chat.py

Diane voice assistant, using Mycroft Precise for wake-word detection.

Adjusted to handle PreciseEngine constructor signature changes.
"""

import os
import sys
import argparse
import logging
import subprocess
import re
import json
import struct
import threading
import time
import wave
import queue

# Attempt imports for audio
try:
    import pyaudio
    import webrtcvad
    import numpy as np
    import sounddevice as sd
    AUDIO_LIBS = True
except ImportError:
    AUDIO_LIBS = False

# ASR / LLM / TTS
import whisper
from llama_cpp import Llama
from piper.voice import PiperVoice

# Flask web interface
from flask import Flask, request, jsonify

# Precise wake-word
from precise_runner import PreciseEngine, PreciseRunner

# ------------------------------------------------------------------------------------
# Defaults and paths
# ------------------------------------------------------------------------------------
DEFAULT_LLM_PATH = os.getenv(
    "LLM_MODEL_PATH",
    "/mnt/ssd/models/L3.2-Rogue-Creative-Instruct-7B-D_AU-Q4_k_m.gguf"
)
DEFAULT_TTS_MODEL_PATH = os.getenv("TTS_MODEL_PATH", "/mnt/ssd/models/tts/en_US-amy-medium.onnx")
CUSTOM_PRECISION_MODEL = "/mnt/ssd/models/hotword/precise_diane.pb"
try:
    import precise_engine
    BUILTIN_PRECISION_MODEL = precise_engine.hey_mycroft_model
except Exception:
    BUILTIN_PRECISION_MODEL = None

DEFAULT_SYNONYMS_JSON = "/mnt/ssd/voice_config/synonyms.json"
APPROVED_NETWORKS_FILE = "/mnt/ssd/voice_config/approved_networks.txt"
DEFAULT_BLUETOOTH_TRUSTED = "/mnt/ssd/voice_config/bluetooth_trusted_devices.txt"

SSD_TMP_DIR = "/mnt/ssd/tmp"
WHISPER_CACHE_DIR = "/mnt/ssd/whisper_cache"

AUDIO_SAMPLE_RATE = 16000
VAD_FRAME_DURATION = 30

# Ensure SSD dirs
os.makedirs(SSD_TMP_DIR, exist_ok=True)
os.makedirs(WHISPER_CACHE_DIR, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = WHISPER_CACHE_DIR

def verify_file(path: str, description: str):
    if path and not os.path.isfile(path):
        logging.error(f"{description} not found at: {path}")
        sys.exit(1)
    logging.info(f"{description} found: {path}")

# Connectivity, network, commands omitted for brevity ...

class WakeWordListener:
    def __init__(self, model_path, audio_device_index=None, on_wake=None):
        self.model_path = model_path
        self.audio_device_index = audio_device_index
        self.on_wake = on_wake

        # Instantiate PreciseEngine with fallback
        try:
            self.engine = PreciseEngine(self.model_path)
        except TypeError:
            # Older/newer signature may require library path first
            self.engine = PreciseEngine(None, self.model_path)

        self.runner = PreciseRunner(self.engine,
                                    on_activation=self._on_activation,
                                    on_stop=lambda: None,
                                    wake_word="Diane")

        self.thread = threading.Thread(target=self._run, daemon=True)

    def _on_activation(self):
        logging.info("Wake word detected (Precise)!")
        if self.on_wake:
            self.on_wake()

    def _run(self):
        self.runner.start()

    def start(self):
        logging.info("Starting Precise wake-word listener")
        self.thread.start()

    def stop(self):
        logging.info("Stopping Precise wake-word listener")
        self.runner.stop()

# Rest of the script unchanged...
# ...
