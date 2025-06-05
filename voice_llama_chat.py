#!/home/diane/diane/.venv/bin/python3
"""
voice_llama_chat.py

Diane voice assistant, now using Mycroft Precise for wake-word detection.

- Uses prebuilt “hey computer” model: /mnt/ssd/models/hotword/precise_diane.pb
- Falls back to built-in “hey mycroft” if custom not found
- On wake word, records via VAD, transcribes with Whisper, queries Llama, and speaks via PiperVoice
- Includes Wi-Fi reconnection, Bluetooth trust, slang modes, VPN commands
- Always runs Flask web server on port 5000 (gated by API key)
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

# Try importing audio-related libraries
try:
    import pyaudio
    import webrtcvad
    import numpy as np
    import sounddevice as sd
    AUDIO_LIBS = True
except ImportError:
    AUDIO_LIBS = False

# Whisper and Llama for ASR/LLM
import whisper
from llama_cpp import Llama
from piper.voice import PiperVoice

# Flask for web interface
from flask import Flask, request, jsonify

# Precise for wake-word detection
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
BUILTIN_PRECISION_MODEL = None
try:
    import precise_engine
    BUILTIN_PRECISION_MODEL = precise_engine.hey_mycroft_model
except Exception:
    BUILTIN_PRECISION_MODEL = None

DEFAULT_SYNONYMS_JSON = os.getenv("SYNONYMS_PATH", "/mnt/ssd/voice_config/synonyms.json")
DEFAULT_BLUETOOTH_TRUSTED = "/home/diane/diane/bluetooth_trusted_devices.txt"
APPROVED_NETWORKS_FILE = "/mnt/ssd/voice_config/approved_networks.txt"

# Directories on SSD for temporary and cache
SSD_TMP_DIR = "/mnt/ssd/tmp"
WHISPER_CACHE_DIR = "/mnt/ssd/whisper_cache"

AUDIO_SAMPLE_RATE = 16000
VAD_FRAME_DURATION = 30  # ms

# ------------------------------------------------------------------------------------
# Ensure SSD temp/cache directories exist
# ------------------------------------------------------------------------------------
os.makedirs(SSD_TMP_DIR, exist_ok=True)
os.makedirs(WHISPER_CACHE_DIR, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = WHISPER_CACHE_DIR

# ------------------------------------------------------------------------------------
# Helper: verify file exists (exit if missing)
# ------------------------------------------------------------------------------------
def verify_file(path: str, description: str):
    if path and not os.path.isfile(path):
        logging.error(f"{description} not found at: {path}")
        sys.exit(1)
    logging.info(f"{description} found: {path}")

# ------------------------------------------------------------------------------------
# Wi-Fi reconnection logic
#------------------------------------------------------------------------------------
def is_connected():
    """Return True if ping to 8.8.8.8 succeeds."""
    try:
        subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def load_approved_networks():
    """
    Read SSID,password pairs from APPROVED_NETWORKS_FILE.
    Each non-comment line: SSID,Password
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
                networks.append((parts[0], parts[1]))
            else:
                logging.warning(f"Ignoring invalid network entry: {line}")
    return networks

def try_connect_networks():
    """Attempt to connect to each approved SSID until one succeeds."""
    networks = load_approved_networks()
    for ssid, password in networks:
        logging.info(f"Attempting Wi-Fi connect: {ssid}")
        try:
            subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
            if is_connected():
                logging.info(f"Connected to {ssid}")
                return True
        except subprocess.CalledProcessError:
            logging.info(f"Failed to connect to {ssid}")
    logging.error("Could not connect to any approved network")
    return False

def wifi_reconnector():
    """Background thread that monitors connectivity and re-connects if lost."""
    while True:
        if not is_connected():
            logging.warning("Internet lost; attempting reconnection")
            try_connect_networks()
        time.sleep(30)

# ------------------------------------------------------------------------------------
# Voice-command handlers (Wi-Fi, Bluetooth, VPN, etc.)
# ------------------------------------------------------------------------------------
def handle_self_update():
    logging.info("Self-update: git pull and restart")
    try:
        subprocess.run(["git", "-C", "/home/diane/diane", "pull", "origin", "main"],
                       check=True)
        subprocess.run(["sudo", "systemctl", "restart", "voice_llama_chat.service"],
                       check=True)
        logging.info("Self-update complete; service restarted.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Self-update failed: {e}")

def handle_wifi_connect(text: str):
    match = re.search(r"connect wifi (\S+) (\S+)", text)
    if match:
        ssid, password = match.group(1), match.group(2)
        logging.info(f"Connecting to Wi-Fi: {ssid}")
        try:
            subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password],
                           check=True)
            logging.info("Wi-Fi connect succeeded.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Wi-Fi connect failed: {e}")
    else:
        logging.warning("Wi-Fi connect command not understood.")

def handle_wifi_disconnect(text: str):
    match = re.search(r"disconnect wifi (\S+)", text)
    if match:
        ssid = match.group(1)
        logging.info(f"Disconnecting Wi-Fi: {ssid}")
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
        logging.info(f"Trust Bluetooth MAC: {mac}")
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
            subprocess.run(["sudo", "systemctl", "restart", "bluetooth-trusted.service"], check=True)
            logging.info("Bluetooth device trusted.")
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
                with open(file_path, "r") as f:
                    slang_map = json.load(f)
                # TODO: store slang_map for later text-processing
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
        logging.info(f"Connecting ExpressVPN: {location}")
        try:
            subprocess.run(["expressvpn", "connect", location], check=True)
            logging.info("ExpressVPN connected.")
        except subprocess.CalledProcessError as e:
            logging.error(f"ExpressVPN connect failed: {e}")
    else:
        logging.warning("VPN connect command not understood.")

def handle_vpn_disconnect(text: str):
    if re.search(r"(?:disconnect vpn|vpn disconnect)", text, re.IGNORECASE):
        logging.info("Disconnecting ExpressVPN")
        try:
            subprocess.run(["expressvpn", "disconnect"], check=True)
            logging.info("ExpressVPN disconnected.")
        except subprocess.CalledProcessError as e:
            logging.error(f"ExpressVPN disconnect failed: {e}")
    else:
        logging.warning("VPN disconnect command not understood.")

# ------------------------------------------------------------------------------------
# Audio/VAD and LLM helpers
# ------------------------------------------------------------------------------------
def record_until_silence(vad, audio_device_index=None):
    pa = pyaudio.PyAudio()
    frame_bytes = int(AUDIO_SAMPLE_RATE * (VAD_FRAME_DURATION / 1000))
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=AUDIO_SAMPLE_RATE,
                     input=True,
                     frames_per_buffer=frame_bytes,
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

def transcribe_audio(raw_audio_bytes):
    tmp_wav = os.path.join(SSD_TMP_DIR, "diane_input.wav")
    wf = wave.open(tmp_wav, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(AUDIO_SAMPLE_RATE)
    wf.writeframes(raw_audio_bytes)
    wf.close()

    model = whisper.load_model("base", device="cpu", download_root=WHISPER_CACHE_DIR)
    result = model.transcribe(tmp_wav)
    return result["text"].strip()

def generate_with_llm(llm_model_path, prompt):
    llm = Llama(model_path=llm_model_path)
    res = llm(prompt, max_tokens=128)
    return res["choices"][0]["text"].strip()

def synthesize_tts(tts_model_path, text):
    voice = PiperVoice.load(tts_model_path)
    audio = voice.synthesize(text, speaker_id=0)
    return audio

def play_audio(audio_array, sample_rate=AUDIO_SAMPLE_RATE, output_device_index=None):
    try:
        sd.play(audio_array, samplerate=sample_rate, device=output_device_index)
        sd.wait()
    except Exception as e:
        logging.warning(f"Audio playback failed: {e}")

# ------------------------------------------------------------------------------------
# Precise wake-word detection thread
# ------------------------------------------------------------------------------------
class WakeWordListener:
    def __init__(self, model_path, audio_device_index=None, on_wake=None):
        """
        model_path: path to .pb (or .tflite) Precise model
        audio_device_index: microphone index for sounddevice (or None for default)
        on_wake: callback function to invoke when wake-word detected
        """
        self.model_path = model_path
        self.audio_device_index = audio_device_index
        self.on_wake = on_wake

        # Set up PreciseEngine & Runner
        self.engine = PreciseEngine(self.model_path)
        # Create runner: 16kHz, 512-window, 160-hop  → ~10 ms per frame
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
        # Start listening (blocks until runner.stop() is called)
        self.runner.start()

    def start(self):
        logging.info("Starting Precise wake-word listener")
        self.thread.start()

    def stop(self):
        logging.info("Stopping Precise wake-word listener")
        self.runner.stop()

# ------------------------------------------------------------------------------------
# Flask Web Interface
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
    parser = argparse.ArgumentParser(
        description="Diane voice assistant (Precise-based wake-word + Flask web)"
    )
    parser.add_argument("--llm-model", type=str, default=DEFAULT_LLM_PATH,
                        help="Path to local LLM binary")
    parser.add_argument("--tts-model", type=str, default=DEFAULT_TTS_MODEL_PATH,
                        help="Path to Piper TTS model")
    parser.add_argument("--precision-model", type=str, default=None,
                        help="Path to Precise wake-word model (.pb or .tflite)")
    parser.add_argument("--vad-mode", type=str, default="1",
                        help="webrtcvad mode (0-3)")
    parser.add_argument("--synonyms", type=str, default=DEFAULT_SYNONYMS_JSON,
                        help="Path to synonyms JSON")
    parser.add_argument("--audio-input", type=int, default=None,
                        help="Index of ALSA audio-capture device")
    parser.add_argument("--audio-output", type=int, default=None,
                        help="Index of ALSA audio-playback device")
    parser.add_argument("--web-key", type=str, default=WEB_API_KEY,
                        help="API key for web interface")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Set logging level")
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
    logging.info(f"  LLM model:           {args.llm_model}")
    logging.info(f"  TTS model:           {args.tts_model}")
    logging.info(f"  Synonyms JSON:       {args.synonyms}")
    logging.info(f"  Web API key:         {args.web_key}")

    # Verify core files
    verify_file(args.llm_model, "LLM model")
    verify_file(args.tts_model, "TTS model")
    verify_file(args.synonyms, "Synonyms JSON")

    # Determine which Precise model to use
    precision_model = None
    if args.precision_model and os.path.isfile(args.precision_model):
        precision_model = args.precision_model
    elif os.path.isfile(CUSTOM_PRECISION_MODEL):
        precision_model = CUSTOM_PRECISION_MODEL
    elif BUILTIN_PRECISION_MODEL and os.path.isfile(BUILTIN_PRECISION_MODEL):
        precision_model = BUILTIN_PRECISION_MODEL

    if precision_model:
        logging.info(f"Using Precise model: {precision_model}")
    else:
        logging.warning("No Precise model found; voice wake-word disabled (web-only mode)")

    # Start Wi-Fi reconnection background thread
    reconnect_thread = threading.Thread(target=wifi_reconnector, daemon=True)
    reconnect_thread.start()

    # If audio libraries are present and we have a wake-word model, start Precise listener
    wake_queue = queue.Queue()

    def on_wake():
        wake_queue.put(True)

    if AUDIO_LIBS and precision_model:
        try:
            listener = WakeWordListener(model_path=precision_model,
                                        audio_device_index=args.audio_input,
                                        on_wake=on_wake)
            listener.start()
            logging.info("Precise wake-word listener started.")
        except Exception as e:
            logging.error(f"Failed to start Precise listener: {e}")
            precision_model = None
    else:
        logging.info("Audio or Precise model missing; running web-only.")

    # If we have audio and wake-word, set up VAD
    if AUDIO_LIBS and precision_model:
        vad_engine = webrtcvad.Vad(int(args.vad_mode))
    else:
        vad_engine = None

    # Flask config
    app.config["llm_model"] = args.llm_model

    # Spawn thread to run Flask
    def run_flask():
        app.run(host="0.0.0.0", port=5000)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Main loop: wait for wake-word, then record, transcribe, generate, and TTS
    if AUDIO_LIBS and precision_model:
        try:
            logging.info("Ready for wake word...")
            while True:
                # Block until Precise signals wake-word
                wake_queue.get()
                logging.info("Wake-word callback triggered, recording...")

                raw_audio = record_until_silence(vad_engine,
                                                 audio_device_index=args.audio_input)
                try:
                    user_text = transcribe_audio(raw_audio)
                except Exception as e:
                    logging.error(f"Transcription error: {e}")
                    continue

                logging.info(f"Heard: '{user_text}'")

                # Voice commands
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

                # Otherwise forward to LLM
                try:
                    response_text = generate_with_llm(args.llm_model, user_text)
                except Exception as e:
                    logging.error(f"LLM error: {e}")
                    continue

                logging.info(f"LLM response: '{response_text}'")
                try:
                    audio_out = synthesize_tts(args.tts_model, response_text)
                except Exception as e:
                    logging.error(f"TTS error: {e}")
                    continue

                try:
                    play_audio(audio_out, sample_rate=AUDIO_SAMPLE_RATE,
                               output_device_index=args.audio_output)
                except Exception as e:
                    logging.error(f"Playback error: {e}")
                    continue

        except KeyboardInterrupt:
            logging.info("Interrupted; exiting.")
        except Exception as e:
            logging.exception(f"Fatal error: {e}")
        finally:
            if AUDIO_LIBS and precision_model:
                listener.stop()
            logging.info("Shutting down.")

    else:
        # If no audio/wake-word, idle forever (Flask is running in background)
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            logging.info("Interrupted; exiting.")

if __name__ == "__main__":
    main()
