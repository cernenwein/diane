#!/home/diane/diane/.venv/bin/python3
"""
voice_llama_chat.py

Diane voice assistant that:
  - Attempts voice input/output if available.
  - Always runs a web interface requiring a keyword (API key) to accept queries.
  - Web endpoint `/query` expects JSON: {"prompt": "...", "key": "..."}.

Adjust `WEB_API_KEY` environment variable or pass via CLI `--web-key`.
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

# Attempt to import audio-related libraries; if unavailable, disable voice features
try:
    import pvporcupine
    import pyaudio
    import webrtcvad
    import numpy as np
    import sounddevice as sd
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

import whisper
from llama_cpp import Llama
from piper.voice import PiperVoice

# Web server
from flask import Flask, request, jsonify

# ------------------------------------------------------------------------------------
# Defaults and paths
# ------------------------------------------------------------------------------------
DEFAULT_LLM_PATH = os.getenv(
    "LLM_MODEL_PATH",
    "/mnt/ssd/models/L3.2-Rogue-Creative-Instruct-7B-D_AU-Q4_k_m.gguf"
)
DEFAULT_TTS_MODEL_PATH = os.getenv("TTS_MODEL_PATH", "/mnt/ssd/models/tts/en_US-amy-medium.onnx")
DEFAULT_HOTWORD_PATH = os.getenv("HOTWORD_MODEL_PATH", "/mnt/ssd/models/hotword/porcupine_diane.ppn")
DEFAULT_SYNONYMS_JSON = os.getenv("SYNONYMS_PATH", "/mnt/ssd/voice_config/synonyms.json")
DEFAULT_BLUETOOTH_TRUSTED = "/home/diane/diane/bluetooth_trusted_devices.txt"
APPROVED_NETWORKS_FILE = "/mnt/ssd/voice_config/approved_networks.txt"

# Directories on SSD for temporary and cache files
SSD_TMP_DIR = "/mnt/ssd/tmp"
WHISPER_CACHE_DIR = "/mnt/ssd/whisper_cache"

AUDIO_SAMPLE_RATE = 16000
VAD_FRAME_DURATION = 30  # ms for webrtcvad

# ------------------------------------------------------------------------------------
# Ensure SSD temp/cache directories exist
# ------------------------------------------------------------------------------------
os.makedirs(SSD_TMP_DIR, exist_ok=True)
os.makedirs(WHISPER_CACHE_DIR, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = WHISPER_CACHE_DIR

# ------------------------------------------------------------------------------------
# Helper: verify file exists
# ------------------------------------------------------------------------------------
def verify_file(path: str, description: str):
    if path and not os.path.isfile(path):
        logging.error(f"{description} not found at: {path}")
        sys.exit(1)
    logging.info(f"{description} found: {path}")

# ------------------------------------------------------------------------------------
# Wi-Fi reconnection logic with SSID/password
# ------------------------------------------------------------------------------------
def is_connected():
    try:
        subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"], stdout=subprocess.DEVNULL)
        return True
    except:
        return False

def load_approved_networks():
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
    while True:
        if not is_connected():
            logging.warning("Internet connectivity lost; attempting reconnection")
            try_connect_networks()
        time.sleep(30)

# ------------------------------------------------------------------------------------
# Voice-command handlers (only if audio libs exist)
# ------------------------------------------------------------------------------------
if AUDIO_LIBS_AVAILABLE:
    def handle_self_update():
        logging.info("Running self-update: git pull and restart service...")
        try:
            subprocess.run(["git", "-C", "/home/diane/diane", "pull", "origin", "main"], check=True)
            subprocess.run(["sudo", "systemctl", "restart", "voice_llama_chat.service"], check=True)
            logging.info("Self-update complete; service restarted.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Self-update failed: {e}")

    def handle_wifi_connect(text: str):
        match = re.search(r"connect wifi (\\S+) (\\S+)", text)
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
        match = re.search(r"disconnect wifi (\\S+)", text)
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
                            f.write(mac + "\\n")
                else:
                    with open(DEFAULT_BLUETOOTH_TRUSTED, "w") as f:
                        f.write(mac + "\\n")
                subprocess.run(["bash", "-c", f"echo 'trust {mac}' | bluetoothctl"], check=True)
                logging.info("Bluetooth device trusted immediately.")
                subprocess.run(["sudo", "systemctl", "restart", "bluetooth-trusted.service"], check=True)
            except Exception as e:
                logging.error(f"Failed to trust Bluetooth device: {e}")
        else:
            logging.warning("Bluetooth trust command not understood.")

    def handle_slang_mode(text: str):
        match = re.search(r"set slang mode (\\w+)", text, re.IGNORECASE)
        if match:
            mode = match.group(1).lower()
            slang_dir = "/mnt/ssd/voice_config/slang_modes"
            file_path = os.path.join(slang_dir, f"{mode}.json")
            if os.path.isfile(file_path):
                logging.info(f"Switching to slang mode: {mode}")
                try:
                    with open(file_path, 'r') as f:
                        slang_map = json.load(f)
                    logging.info(f"Loaded slang mode '{mode}'.")
                except Exception as e:
                    logging.error(f"Failed to load slang mode: {e}")
            else:
                logging.warning(f"Slang mode file not found: {file_path}")
        else:
            logging.warning("Slang mode command not understood.")

    def handle_vpn_connect(text: str):
        match = re.search(r"(?:connect vpn|vpn connect) (\\S+)", text, re.IGNORECASE)
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

    def record_until_silence(vad, audio_device_index=None):
        pa = pyaudio.PyAudio()
        frame_bytes = int(AUDIO_SAMPLE_RATE * (VAD_FRAME_DURATION / 1000))
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=AUDIO_SAMPLE_RATE,
                         input=True, frames_per_buffer=frame_bytes,
                         input_device_index=audio_device_index)
        speech_frames = []
        silence_count = 0
        triggered = False
        while True:
            frame = stream.read(frame_bytes, exception_on_overflow=False)
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
else:
    # Dummy placeholders if audio libs not available
    def handle_self_update(): pass
    def handle_wifi_connect(text): pass
    def handle_wifi_disconnect(text): pass
    def handle_add_trusted_bluetooth(text): pass
    def handle_slang_mode(text): pass
    def handle_vpn_connect(text): pass
    def handle_vpn_disconnect(text): pass

# ------------------------------------------------------------------------------------
# Transcription using Whisper (caches on SSD)
# ------------------------------------------------------------------------------------
def transcribe_audio(raw_audio_bytes):
    tmp_wav = os.path.join(SSD_TMP_DIR, "diane_input.wav")
    wf = wave.open(tmp_wav, 'wb')
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(AUDIO_SAMPLE_RATE)
    wf.writeframes(raw_audio_bytes); wf.close()

    model = whisper.load_model("base", device="cpu", download_root=WHISPER_CACHE_DIR)
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
# TTS synthesis via PiperVoice
# ------------------------------------------------------------------------------------
def synthesize_tts(tts_model_path, text):
    voice = PiperVoice.load(tts_model_path)
    audio = voice.synthesize(text, speaker_id=0)
    return audio

# ------------------------------------------------------------------------------------
# Playback audio using sounddevice
# ------------------------------------------------------------------------------------
def play_audio(audio_array, sample_rate=AUDIO_SAMPLE_RATE, output_device_index=None):
    try:
        sd.play(audio_array, samplerate=sample_rate, device=output_device_index)
        sd.wait()
    except Exception as e:
        logging.warning(f"Audio playback failed: {e}")

# ------------------------------------------------------------------------------------
# Web interface setup
# ------------------------------------------------------------------------------------
app = Flask(__name__)
WEB_API_KEY = os.getenv("WEB_API_KEY", "changeme")

@app.route("/query", methods=["POST"])
def query():
    data = request.json or {}
    prompt = data.get("prompt", "").strip()
    key = data.get("key", "")
    if key != WEB_API_KEY:
        return jsonify({"error": "Invalid API key"}), 403
    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    try:
        response_text = generate_with_llm(app.config["llm_model"], prompt)
    except Exception as e:
        return jsonify({"error": f"LLM error: {e}"}), 500

    return jsonify({"response": response_text})

# ------------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Diane voice assistant with web interface")
    parser.add_argument("--llm-model", type=str, default=DEFAULT_LLM_PATH, help="Path to local LLM binary")
    parser.add_argument("--tts-model", type=str, default=DEFAULT_TTS_MODEL_PATH, help="Path to Piper TTS model")
    parser.add_argument("--hotword-model", type=str, default=DEFAULT_HOTWORD_PATH, help="Path to Porcupine .ppn")
    parser.add_argument("--vad-mode", type=str, default="1", help="webrtcvad mode (0-3)")
    parser.add_argument("--synonyms", type=str, default=DEFAULT_SYNONYMS_JSON, help="Path to synonyms JSON")
    parser.add_argument("--wake-word", type=str, default="Diane", help="Wake-word to listen for")
    parser.add_argument("--audio-input", type=int, default=None, help="Index of ALSA audio-capture device")
    parser.add_argument("--audio-output", type=int, default=None, help="Index of ALSA audio-playback device")
    parser.add_argument("--web-key", type=str, default=WEB_API_KEY, help="API key for web interface")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG","INFO","WARNING","ERROR"], help="Set logging level")
    return parser.parse_args()

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
    logging.info(f"  Web API key:     {args.web_key}")

    verify_file(args.llm_model, "LLM model")
    verify_file(args.tts_model, "TTS model")
    if AUDIO_LIBS_AVAILABLE:
        verify_file(args.hotword_model, "Porcupine model")
    verify_file(args.synonyms, "Synonyms JSON")

    # Set Flask config
    app.config["llm_model"] = args.llm_model

    # Start Wi-Fi reconnection thread
    reconnect_thread = threading.Thread(target=wifi_reconnector, daemon=True)
    reconnect_thread.start()

    # Start voice loop in a separate thread if audio libs available
    if AUDIO_LIBS_AVAILABLE:
        try:
            detector = WakeWordDetector(model_path=args.hotword_model, audio_device_index=args.audio_input)
            vad_engine = webrtcvad.Vad(int(args.vad_mode))

            def voice_loop():
                while True:
                    detector.listen()
                    raw_audio = record_until_silence(vad_engine, audio_device_index=args.audio_input)
                    try:
                        user_text = transcribe_audio(raw_audio)
                    except Exception as e:
                        logging.error(f"Transcription error: {e}")
                        continue

                    logging.info(f"Heard: '{user_text}'")
                    # Built-in commands
                    if re.search(r"\\b(update code|self update)\\b", user_text, re.IGNORECASE):
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

                    # Otherwise, forward to LLM
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
                        play_audio(audio_out, sample_rate=AUDIO_SAMPLE_RATE, device=args.audio_output)
                    except Exception as e:
                        logging.error(f"Playback error: {e}"); continue

            t = threading.Thread(target=voice_loop, daemon=True)
            t.start()
        except Exception as e:
            logging.error(f"Audio initialization failed, running web-only: {e}")
    else:
        logging.info("Audio libraries missing; running web interface only.")

    # Always start Flask web server
    # Note: For production, use a proper WSGI server instead of Flask's built-in
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
