#!/usr/bin/env python3

from flask import Flask, render_template_string, request
import subprocess
import os

app = Flask(__name__)
TEXT_OUTPUT_FILE = "/tmp/web_diane_input.txt"
AUDIO_OUTPUT_FILE = "/tmp/diane_output.wav"
PIPER_COMMAND = "/usr/local/bin/piper"
PIPER_VOICE = "/home/diane/piper/en_US-lessac-medium.onnx"

TEMPLATE = """
<!doctype html>
<html>
<head><title>Diane Web Interface</title></head>
<body>
    <h2>🗣️ Talk to Diane (Text Mode)</h2>
    <form action="/" method="post">
        <textarea name="query" rows="3" cols="60" placeholder="Say something to Diane..."></textarea><br><br>
        <input type="submit" value="Submit">
    </form>
    {% if response %}
        <p><b>Diane says:</b> {{ response }}</p>
    {% endif %}
</body>
</html>
"""

def synthesize_speech(text):
    try:
        subprocess.run([PIPER_COMMAND, "--model", PIPER_VOICE, "--output_file", AUDIO_OUTPUT_FILE],
                       input=text.encode(), check=True)
        os.system(f"aplay {AUDIO_OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Piper error: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    if request.method == "POST":
        query = request.form["query"]
        response = f"You said: {query}"
        synthesize_speech(response)
    return render_template_string(TEMPLATE, response=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080)
