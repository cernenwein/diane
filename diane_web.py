#!/home/diane/diane/.venv/bin/python3
"""diane_web.py

Launch only the web interface of Diane's voice_llama_chat app,
listening on a configurable port via the WEB_PORT environment variable.
"""
import logging
import os
from voice_llama_chat import app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("WEB_PORT", "5000"))
    host = "0.0.0.0"
    logging.info(f"Starting web interface on {host}:{port}")
    app.run(host=host, port=port)
