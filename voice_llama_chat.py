#!/home/diane/diane/.venv/bin/python3
"""
voice_llama_chat.py

Diane Voice Assistant with Mycroft Precise wake-word detection.
Flask web server runs in foreground under systemd.
"""

import os
import sys
import argparse
import logging
import subprocess
import re
import json
import threading
import time
import wave
import queue

# Audio dependencies
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

# Flask web server
from flask import Flask, request, jsonify

# Precise wake-word detection
from precise_runner import PreciseEngine, PreciseRunner

# ------------------------------------------------------------------------------------
# Paths and defaults
# ------------------------------------------------------------------------------------
DEFAULT_LLM_PATH = os.getenv("LLM_MODEL_PATH", "/mnt/ssd/models/L3.2-Rogue-Creative-Instruct-7B-D_AU-Q4_k_m.gguf")
DEFAULT_TTS_MODEL_PATH = os.getenv("TTS_MODEL_PATH", "/mnt/ssd/models/tts/en_US-amy-medium.onnx")
CUSTOM_PRECISION_MODEL = "/mnt/ssd/models/hotword/precise_diane.pb"
try:
    import precise_engine
    BUILTIN_PRECISION_MODEL = precise_engine.hey_mycroft_model
except ImportError:
    BUILTIN_PRECISION_MODEL = None

DEFAULT_SYNONYMS_JSON = "/mnt/ssd/voice_config/synonyms.json"
APPROVED_NETWORKS_FILE = "/mnt/ssd/voice_config/approved_networks.txt"
DEFAULT_BLUETOOTH_TRUSTED = "/mnt/ssd/voice_config/bluetooth_trusted_devices.txt"

SSD_TMP_DIR = "/mnt/ssd/tmp"
WHISPER_CACHE_DIR = "/mnt/ssd/whisper_cache"
AUDIO_SAMPLE_RATE = 16000
VAD_FRAME_DURATION = 30

os.makedirs(SSD_TMP_DIR, exist_ok=True)
os.makedirs(WHISPER_CACHE_DIR, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = WHISPER_CACHE_DIR

def verify_file(path, desc):
    if not os.path.isfile(path):
        logging.error(f"{desc} not found at: {path}")
        sys.exit(1)
    logging.info(f"{desc} found: {path}")

class WakeWordListener:
    def __init__(self, model_path, audio_device_index=None, on_wake=None):
        self.on_wake = on_wake
        try:
            self.engine = PreciseEngine(model_path)
        except TypeError:
            # older/newer signature
            self.engine = PreciseEngine(None, model_path)
        # Instantiate runner with only on_activation callback
        self.runner = PreciseRunner(self.engine, on_activation=self._on_activation)
        self.thread = threading.Thread(target=self.runner.start, daemon=True)

    def _on_activation(self):
        logging.info("Wake word detected (Precise)!")
        if self.on_wake:
            self.on_wake()

    def start(self):
        logging.info("Starting Precise listener")
        self.thread.start()

    def stop(self):
        logging.info("Stopping Precise listener")
        self.runner.stop()

def record_until_silence(vad, audio_device_index=None):
    pa = pyaudio.PyAudio()
    frame_bytes = int(AUDIO_SAMPLE_RATE * (VAD_FRAME_DURATION / 1000))
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=AUDIO_SAMPLE_RATE,
                     input=True, frames_per_buffer=frame_bytes, input_device_index=audio_device_index)
    frames, silence, triggered = [], 0, False
    while True:
        frame = stream.read(frame_bytes, exception_on_overflow=False)
        if vad.is_speech(frame, AUDIO_SAMPLE_RATE):
            frames.append(frame); silence = 0; triggered = True
        else:
            if triggered:
                silence += 1
                if silence > int(1000 / VAD_FRAME_DURATION):
                    break
    stream.stop_stream(); stream.close(); pa.terminate()
    return b"".join(frames)

def transcribe_audio(raw_audio_bytes):
    tmp = os.path.join(SSD_TMP_DIR, "diane_input.wav")
    with wave.open(tmp, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(AUDIO_SAMPLE_RATE)
        wf.writeframes(raw_audio_bytes)
    model = whisper.load_model("base", device="cpu", download_root=WHISPER_CACHE_DIR)
    return model.transcribe(tmp)["text"].strip()

def generate_with_llm(llm_model_path, prompt):
    llm = Llama(model_path=llm_model_path)
    return llm(prompt, max_tokens=128)["choices"][0]["text"].strip()

def synthesize_tts(tts_model_path, text):
    voice = PiperVoice.load(tts_model_path)
    return voice.synthesize(text, speaker_id=0)

def play_audio(audio_array, sample_rate=AUDIO_SAMPLE_RATE, output_device_index=None):
    try:
        sd.play(audio_array, samplerate=sample_rate, device=output_device_index); sd.wait()
    except Exception as e:
        logging.warning(f"Audio playback failed: {e}")

# Flask web setup
app = Flask(__name__)
WEB_API_KEY = os.getenv("WEB_API_KEY", "changeme")

@app.route("/query", methods=["POST"])
def query():
    data = request.json or {}
    if data.get("key") != WEB_API_KEY:
        return jsonify({"error":"Invalid API key"}),403
    prompt = data.get("prompt","").strip()
    if not prompt: return jsonify({"error":"Missing prompt"}),400
    try:
        response = generate_with_llm(app.config["llm_model"], prompt)
        return jsonify({"response":response})
    except Exception as e:
        return jsonify({"error":str(e)}),500

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--llm-model", default=DEFAULT_LLM_PATH)
    p.add_argument("--tts-model", default=DEFAULT_TTS_MODEL_PATH)
    p.add_argument("--precision-model", default=None)
    p.add_argument("--vad-mode", default="1")
    p.add_argument("--synonyms", default=DEFAULT_SYNONYMS_JSON)
    p.add_argument("--audio-input", type=int, default=None)
    p.add_argument("--audio-output", type=int, default=None)
    p.add_argument("--web-key", default=WEB_API_KEY)
    p.add_argument("--log-level", default="INFO")
    return p.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s: %(message)s")
    verify_file(args.llm_model, "LLM model")
    verify_file(args.tts_model, "TTS model")
    verify_file(args.synonyms, "Synonyms JSON")
    # choose precise model
    pm = args.precision_model if args.precision_model and os.path.isfile(args.precision_model) else (
         CUSTOM_PRECISION_MODEL if os.path.isfile(CUSTOM_PRECISION_MODEL) else (
         BUILTIN_PRECISION_MODEL if BUILTIN_PRECISION_MODEL and os.path.isfile(BUILTIN_PRECISION_MODEL) else None))
    if pm: logging.info(f"Using Precise model: {pm}")
    else: logging.warning("No Precise model; voice disabled")
    app.config["llm_model"] = args.llm_model
    # start wake listener
    wake_q = queue.Queue()
    listener = None
    if AUDIO_LIBS and pm:
        listener = WakeWordListener(pm, args.audio_input, lambda: wake_q.put(True))
        listener.start()
    # set up VAD
    vad = webrtcvad.Vad(int(args.vad_mode)) if AUDIO_LIBS and pm else None
    # start voice loop thread
    def voice_loop():
        while True:
            wake_q.get()
            raw = record_until_silence(vad, args.audio_input)
            text = transcribe_audio(raw)
            logging.info(f"Heard: {text}")
            # [handle commands and chat logic...]
            resp = generate_with_llm(args.llm_model, text)
            audio = synthesize_tts(args.tts_model, resp)
            play_audio(audio, AUDIO_SAMPLE_RATE, args.audio_output)
    if AUDIO_LIBS and pm:
        threading.Thread(target=voice_loop, daemon=True).start()
    # finally, run the web server in foreground
    logging.info("Starting Flask web server")
    app.run(host="0.0.0.0", port=5000)

if __name__=='__main__':
    main()
