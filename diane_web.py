#!/home/diane/diane/.venv/bin/python3
"""diane_web.py

Launch only the web interface of Diane's voice_llama_chat app.
"""
import logging
from voice_llama_chat import app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000)
