#!/home/diane/diane/.venv/bin/python3
"""diane_web.py

Launch only the web interface of Diane's voice_llama_chat app.
Configures model paths and API key from environment.
"""
import os
import logging
from voice_llama_chat import app, verify_file, DEFAULT_LLM_PATH, DEFAULT_TTS_MODEL_PATH, DEFAULT_SYNONYMS_JSON

def configure_app():
    # Read env vars or defaults
    llm_model = os.getenv("LLM_MODEL_PATH", DEFAULT_LLM_PATH)
    tts_model = os.getenv("TTS_MODEL_PATH", DEFAULT_TTS_MODEL_PATH)
    synonyms = os.getenv("SYNONYMS_PATH", DEFAULT_SYNONYMS_JSON)
    web_key = os.getenv("WEB_API_KEY", None)

    # Validate
    verify_file(llm_model, "LLM model")
    verify_file(tts_model, "TTS model")
    verify_file(synonyms, "Synonyms JSON")
    if not web_key:
        logging.error("WEB_API_KEY environment variable not set")
        raise RuntimeError("WEB_API_KEY not set")

    # Configure Flask app
    app.config["llm_model"] = llm_model
    app.config["tts_model"] = tts_model
    app.config["synonyms"] = synonyms
    app.config["precision_model"] = None
    app.config["audio_input"] = None
    app.config["audio_output"] = None
    app.config["web_key"] = web_key

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    configure_app()
    port = int(os.getenv("WEB_PORT", "8080"))
    host = "0.0.0.0"
    logging.info(f"Starting Diane web interface on {host}:{port}")
    app.run(host=host, port=port)
