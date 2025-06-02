#!/usr/bin/env python3

import os
import time
import sounddevice as sd
import soundfile as sf
import subprocess
import speech_recognition as sr

WAKE_WORD = "diane"
AUDIO_OUTPUT_PATH = "/tmp/diane_output.wav"
AUDIO_INPUT_PATH = "/tmp/diane_input.wav"
PIPER_VOICE = "/home/diane/piper/en_US-lessac-medium.onnx"
PIPER_COMMAND = "/usr/local/bin/piper"

def play_response_audio():
    if os.path.exists(AUDIO_OUTPUT_PATH):
        os.system(f"aplay {AUDIO_OUTPUT_PATH}")
    else:
        print("⚠️ Warning: No output audio to play (missing /tmp/diane_output.wav)")

def record_audio(duration=5):
    print("🎙️ Listening...")
    samplerate = 16000
    channels = 1
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=channels, dtype='int16')
    sd.wait()
    sf.write(AUDIO_INPUT_PATH, recording, samplerate)
    print("✅ Recorded.")

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile(AUDIO_INPUT_PATH) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"❌ Speech Recognition error: {e}")
        return ""

def generate_response(text):
    # Simple placeholder response generator
    return f"You said: {text}"

def synthesize_speech(response_text):
    print(f"🗣️ Diane says: {response_text}")
    try:
        subprocess.run([PIPER_COMMAND, "--model", PIPER_VOICE, "--output_file", AUDIO_OUTPUT_PATH],
                       input=response_text.encode(), check=True)
    except Exception as e:
        print(f"❌ Piper synthesis error: {e}")

def main():
    print("[Diane says]: I am Diane, online and listening.")
    while True:
        try:
            print("👂 Listening for wake word...")
            record_audio(duration=3)
            text = transcribe_audio().lower()
            if WAKE_WORD in text:
                print(f"🎉 Wake word '{WAKE_WORD}' detected!")
                record_audio(duration=5)
                spoken = transcribe_audio()
                print(f"📥 Heard: {spoken}")
                response = generate_response(spoken)
                synthesize_speech(response)
                play_response_audio()
            else:
                print("⏸️ Wake word not detected.")
        except KeyboardInterrupt:
            print("
🛑 Diane session ended.")
            break
        except Exception as e:
            print(f"⚠️ Unhandled error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
