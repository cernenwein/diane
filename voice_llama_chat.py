#!/usr/bin/env python3
"""
voice_llama_chat.py

Diane voice assistant with automatic Wi-Fi reconnection using SSID/password pairs:
  - On startup and on connectivity loss, cycles through approved networks to connect.
  - Approved networks list now includes SSID and password.

Approved networks file format (one per line):
  SSID,Password

Example:
  HomeNetwork,MyHomePass123
  OfficeWiFi,OfficePass!
  MobileHotspot,12345678
  
Other features:
  - Wake‐word detection via Porcupine
  - VAD using webrtcvad
  - Transcription using OpenAI Whisper
  - LLM inference using llama-cpp-python
  - TTS synthesis using Piper
  - Audio playback using sounddevice
  - Built‐in commands: self-update, Wi-Fi connect/disconnect, Bluetooth trust, slang modes, ExpressVPN
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

import pvporcupine
import pyaudio
import webrtcvad
import numpy as np
import sounddevice as sd

import whisper
from llama_cpp import Llama
from piper_tts import PiperTTS

# ------------------------------------------------------------------------------------
# Defaults and paths
# ------------------------------------------------------------------------------------
DEFAULT_LLM_PATH = os.getenv("LLM_MODEL_PATH", "/mnt/ssd/models/ggml-diane-7b.bin")
DEFAULT_TTS_PATH = os.getenv("TTS_MODEL_PATH", "/mnt/ssd/models/tts/en_US-amy-medium.onnx")
DEFAULT_HOTWORD_PATH = os.getenv("HOTWORD_MODEL_PATH", "/mnt/ssd/models/hotword/porcupine_diane.ppn")
DEFAULT_SYNONYMS_JSON = os.getenv("SYNONYMS_PATH", "/mnt/ssd/voice_config/synonyms.json")
DEFAULT_BLUETOOTH_TRUSTED = "/home/diane/diane/bluetooth_trusted_devices.txt"
APPROVED_NETWORKS_FILE = "/mnt/ssd/voice_config/approved_networks.txt"

AUDIO_SAMPLE_RATE = 16000
VAD_FRAME_DURATION = 30  # ms for webrtcvad

# ------------------------------------------------------------------------------------
# Helper: verify file exists
# ------------------------------------------------------------------------------------
def verify_file(path: str, description: str):
    if path and not os.path.isfile(path):
        logging.error(f"{description} not found at: {path}")
        sys.exit(1)
    else:
        logging.info(f"{description} found: {path}")

# ------------------------------------------------------------------------------------
# Wi-Fi reconnection logic with SSID/password
# ------------------------------------------------------------------------------------
def is_connected():
    """Return True if ping to 8.8.8.8 succeeds."""
    try:
        subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"], stdout=subprocess.DEVNULL)
        return True
    except:
        return False

def load_approved_networks():
    """
    Read SSID,password from APPROVED_NETWORKS_FILE.
    Each line should be: SSID,Password
    Returns list of (ssid, password).
    """
    networks = []
    if not os.path.isfile(APPROVED_NETWORKS_FILE):
        logging.warning(f"Approved networks file not found: {APPROVED_NETWORKS_FILE}")
        return networks
    with open(APPROVED_NETWORKS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",", 1)]
            if len(parts) == 2:
                ssid, password = parts
                networks.append((ssid, password))
            else:
                logging.warning(f"Ignoring invalid network entry: {line}")
    return networks

def try_connect_networks():
    """Cycle through approved networks until one connects."""
    networks = load_approved_networks()
    for ssid, password in networks:
        logging.info(f"Attempting to connect to SSID: {ssid}")
        try:
            subprocess.run(
                ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
                check=True
            )
            time.sleep(5)  # allow time to connect
            if is_connected():
                logging.info(f"Successfully connected to {ssid}")
                return True
        except subprocess.CalledProcessError:
            logging.info(f"Failed to connect to {ssid}")
    logging.error("Could not connect to any approved network")
    return False

def wifi_reconnector():
    """Background thread: monitor connectivity and reconnect if lost."""
    while True:
        if not is_connected():
            logging.warning("Internet connectivity lost; attempting reconnection")
            try_connect_networks()
        time.sleep(30)

# ------------------------------------------------------------------------------------
# Voice-command handlers (unchanged)
# ------------------------------------------------------------------------------------
def handle_self_update():
    logging.info("Running self-update: git pull and restart service...")
    try:
        subprocess.run(["git", "-C", "/home/diane/diane", "pull", "origin", "main"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "voice_llama_chat.service"], check=True)
        logging.info("Self-update complete; service restarted.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Self-update failed: {e}")

def handle_wifi_connect(text: str):
    match = re.search(r"connect wifi (\S+) (\S+)", text)
    if match:
        ssid = match.group(1)
        password = match.group(2)
        logging.info(f"Connecting to Wi-Fi SSID: {ssid}")
        try:
            subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password], check=True)
            logging.info("Wi-Fi connect succeeded.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Wi-Fi connect failed: {e}")
    else:
        logging.warning("Wi-Fi connect command not understood.")

def handle_wifi_disconnect(text: str):
    match = re.search(r"disconnect wifi (\S+)", text)
    if match:
        ssid = match.group(1)
        logging.info(f"Disconnecting from Wi-Fi SSID: {ssid}")
        try:
            subprocess.run(["nmcli", "con", "down", ssid], check=True)
            logging.info("Wi-Fi disconnect succeeded.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Wi-Fi disconnect failed: {e}")
    else:
        logging.warning("Wi-Fi disconnect command not understood.")

def handle_add_trusted_bluetooth(text: str):
    match = re.search(r"trust device ([0-9A-F:]{17})", text, re.IGNORECASE)
    if match:
        mac = match.group(1).upper()
        logging.info(f"Adding Bluetooth MAC to trusted list: {mac}")
        try:
            if os.path.exists(DEFAULT_BLUETOOTH_TRUSTED):
                with open(DEFAULT_BLUETOOTH_TRUSTED, "r+") as f:
                    lines = [line.strip() for line in f if line.strip()]
                    if mac not in lines:
                        f.write(mac + "\n")
            else:
                with open(DEFAULT_BLUETOOTH_TRUSTED, "w") as f:
                    f.write(mac + "\n")
            subprocess.run(["bash", "-c", f"echo 'trust {mac}' | bluetoothctl"], check=True)
            logging.info("Bluetooth device trusted immediately.")
            subprocess.run(["sudo", "systemctl", "restart", "bluetooth-trusted.service"], check=True)
        except Exception as e:
            logging.error(f"Failed to trust Bluetooth device: {e}")
    else:
        logging.warning("Bluetooth trust command not understood.")

def handle_slang_mode(text: str):
    match = re.search(r"set slang mode (\w+)", text, re.IGNORECASE)
    if match:
        mode = match.group(1).lower()
        slang_dir = "/mnt/ssd/voice_config/slang_modes"
        file_path = os.path.join(slang_dir, f"{mode}.json")
        if os.path.isfile(file_path):
            logging.info(f"Switching to slang mode: {mode}")
            try:
                with open(file_path, 'r') as f:
                    slang_map = json.load(f)
                # TODO: store slang_map for later use in text processing
                logging.info(f"Loaded slang mode '{mode}'.")
            except Exception as e:
                logging.error(f"Failed to load slang mode: {e}")
        else:
            logging.warning(f"Slang mode file not found: {file_path}")
    else:
        logging.warning("Slang mode command not understood.")

def handle_vpn_connect(text: str):
    match = re.search(r"(?:connect vpn|vpn connect) (\S+)", text, re.IGNORECASE)
    if match:
        location = match.group(1)
        logging.info(f"Connecting ExpressVPN to location: {location}")
        try:
            subprocess.run(["expressvpn", "connect", location], check=True)
            logging.info("ExpressVPN connected.")
        except subprocess.CalledProcessError as e:
            logging.error(f"ExpressVPN connect failed: {e}")
    else:
        logging.warning("VPN connect command not understood.")

def handle_vpn_disconnect(text: str):
    if re.search(r"(?:disconnect vpn|vpn disconnect)", text, re.IGNORECASE):
        logging.info("Disconnecting ExpressVPN...")
        try:
            subprocess.run(["expressvpn", "disconnect"], check=True)
            logging.info("ExpressVPN disconnected.")
        except subprocess.CalledProcessError as e:
            logging.error(f"ExpressVPN disconnect failed: {e}")
    else:
        logging.warning("VPN disconnect command not understood.")

# ------------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Diane voice assistant")
    parser.add_argument("--llm-model", type=str, default=DEFAULT_LLM_PATH, help="Path to local LLM binary")
    parser.add_argument("--tts-model", type=str, default=DEFAULT_TTS_PATH, help="Path to Piper TTS model")
    parser.add_argument("--hotword-model", type=str, default=DEFAULT_HOTWORD_PATH, help="Path to Porcupine .ppn")
    parser.add_argument("--vad-mode", type=str, default="1", help="webrtcvad mode (0-3)")
    parser.add_argument("--synonyms", type=str, default=DEFAULT_SYNONYMS_JSON, help="Path to synonyms JSON")
    parser.add_argument("--wake-word", type=str, default="Diane", help="Wake-word to listen for")
    parser.add_argument("--audio-input", type=int, default=None, help="Index of ALSA audio-capture device")
    parser.add_argument("--audio-output", type=int, default=None, help="Index of ALSA audio-playback device")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG","INFO","WARNING","ERROR"], help="Set logging level")
    return parser.parse_args()

# ------------------------------------------------------------------------------------
# Wake-word detection via Porcupine
# ------------------------------------------------------------------------------------
class WakeWordDetector:
    def __init__(self, model_path: str, audio_device_index: int = None):
        self.porcupine = pvporcupine.create(keyword_paths=[model_path], sensitivities=[0.5])
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
            input=True, frames_per_buffer=self.porcupine.frame_length,
            input_device_index=audio_device_index
        )
    def listen(self):
        logging.info("Waiting for wake word...")
        while True:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm_unpacked)
            if result >= 0:
                logging.info("Wake word detected!")
                return
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.porcupine.delete()

# ------------------------------------------------------------------------------------
# Record audio until VAD indicates end of speech
# ------------------------------------------------------------------------------------
def record_until_silence(vad, audio_device_index=None):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=AUDIO_SAMPLE_RATE,
                     input=True, frames_per_buffer=int(AUDIO_SAMPLE_RATE * (VAD_FRAME_DURATION / 1000)),
                     input_device_index=audio_device_index)
    speech_frames = []
    silence_count = 0
    triggered = False
    while True:
        frame = stream.read(int(AUDIO_SAMPLE_RATE * (VAD_FRAME_DURATION / 1000)), exception_on_overflow=False)
        is_speech = vad.is_speech(frame, AUDIO_SAMPLE_RATE)
        if is_speech:
            speech_frames.append(frame)
            silence_count = 0
            triggered = True
        else:
            if triggered:
                silence_count += 1
                if silence_count > int(1000 / VAD_FRAME_DURATION):
                    break
    stream.stop_stream()
    stream.close()
    pa.terminate()
    return b"".join(speech_frames)

# ------------------------------------------------------------------------------------
# Transcription using Whisper
# ------------------------------------------------------------------------------------
def transcribe_audio(raw_audio_bytes):
    tmp_wav = "/tmp/diane_input.wav"
    wf = wave.open(tmp_wav, 'wb')
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(AUDIO_SAMPLE_RATE)
    wf.writeframes(raw_audio_bytes); wf.close()
    model = whisper.load_model("base", device="cpu")
    result = model.transcribe(tmp_wav)
    return result["text"].strip()

# ------------------------------------------------------------------------------------
# Generate text via Llama
# ------------------------------------------------------------------------------------
def generate_with_llm(llm_model_path, prompt):
    llm = Llama(model_path=llm_model_path)
    res = llm(prompt, max_tokens=128)
    return res["choices"][0]["text"].strip()

# ------------------------------------------------------------------------------------
# TTS synthesis via Piper
# ------------------------------------------------------------------------------------
def synthesize_tts(tts_model_path, text):
    tts = PiperTTS(model_path=tts_model_path)
    audio = tts.synthesize(text)
    return audio

# ------------------------------------------------------------------------------------
# Playback audio using sounddevice
# ------------------------------------------------------------------------------------
def play_audio(audio_array, sample_rate=AUDIO_SAMPLE_RATE, output_device_index=None):
    sd.play(audio_array, samplerate=sample_rate, device=output_device_index)
    sd.wait()

# ------------------------------------------------------------------------------------
# Main entrypoint
# ------------------------------------------------------------------------------------
def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level,
                        format="%(asctime)s %(levelname)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    logging.info("Starting Diane with configuration")
    logging.info(f"  LLM model:       {args.llm_model}")
    logging.info(f"  TTS model:       {args.tts_model}")
    logging.info(f"  Porcupine model: {args.hotword_model}")
    logging.info(f"  VAD mode:        {args.vad_mode}")
    logging.info(f"  Synonyms file:   {args.synonyms}")
    if args.audio_input is not None:
        logging.info(f"  Audio in index:  {args.audio_input}")
    else:
        logging.info("  Audio in:        (default)")
    if args.audio_output is not None:
        logging.info(f"  Audio out index: {args.audio_output}")
    else:
        logging.info("  Audio out:       (default)")

    verify_file(args.llm_model, "LLM model")
    verify_file(args.tts_model, "TTS model")
    verify_file(args.hotword_model, "Porcupine model")
    verify_file(args.synonyms, "Synonyms JSON")

    # Start Wi-Fi reconnection thread
    reconnect_thread = threading.Thread(target=wifi_reconnector, daemon=True)
    reconnect_thread.start()

    detector = WakeWordDetector(model_path=args.hotword_model, audio_device_index=args.audio_input)
    vad_engine = webrtcvad.Vad(int(args.vad_mode))

    try:
        logging.info("Listening for wake word...")
        while True:
            detector.listen()
            raw_audio = record_until_silence(vad_engine, audio_device_index=args.audio_input)
            try:
                user_text = transcribe_audio(raw_audio)
            except Exception as e:
                logging.error(f"Transcription error: {e}")
                continue

            logging.info(f"Heard: '{user_text}'")
            if re.search(r"\b(update code|self update)\b", user_text, re.IGNORECASE):
                handle_self_update(); continue
            if re.search(r"connect wifi", user_text, re.IGNORECASE):
                handle_wifi_connect(user_text.lower()); continue
            if re.search(r"disconnect wifi", user_text, re.IGNORECASE):
                handle_wifi_disconnect(user_text.lower()); continue
            if re.search(r"trust device", user_text, re.IGNORECASE):
                handle_add_trusted_bluetooth(user_text.lower()); continue
            if re.search(r"set slang mode", user_text, re.IGNORECASE):
                handle_slang_mode(user_text.lower()); continue
            if re.search(r"(?:connect vpn|vpn connect)", user_text, re.IGNORECASE):
                handle_vpn_connect(user_text.lower()); continue
            if re.search(r"(?:disconnect vpn|vpn disconnect)", user_text, re.IGNORECASE):
                handle_vpn_disconnect(user_text.lower()); continue

            try:
                response_text = generate_with_llm(args.llm_model, user_text)
            except Exception as e:
                logging.error(f"LLM error: {e}")
                continue

            logging.info(f"LLM response: '{response_text}'")
            try:
                audio_out = synthesize_tts(args.tts_model, response_text)
            except Exception as e:
                logging.error(f"TTS error: {e}"); continue

            try:
                play_audio(audio_out, samplerate=AUDIO_SAMPLE_RATE, output_device_index=args.audio_output)
            except Exception as e:
                logging.error(f"Playback error: {e}"); continue

    except KeyboardInterrupt:
        logging.info("Interrupted; exiting.")
    except Exception as e:
        logging.exception(f"Fatal error: {e}")
    finally:
        logging.info("Shutting down.")
        detector.close()

if __name__ == "__main__":
    main()
