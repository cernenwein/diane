#!/home/diane/diane/.venv/bin/python3
"""diane_web.py

Launch only the web interface of Diane's voice_llama_chat app,
loading configuration from .env.
"""
import os
from dotenv import load_dotenv
import logging

# Load .env from repo root
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

# Import the Flask app and utility
from voice_llama_chat import app, verify_file

def configure_app():
    # Read environment variables
    llm_model = os.getenv('LLM_MODEL_PATH')
    tts_model = os.getenv('TTS_MODEL_PATH')
    synonyms = os.getenv('SYNONYMS_PATH')
    web_key = os.getenv('WEB_API_KEY')

    # Validate
    verify_file(llm_model, 'LLM model')
    verify_file(tts_model, 'TTS model')
    verify_file(synonyms, 'Synonyms JSON')
    if not web_key:
        logging.error('WEB_API_KEY not set in .env')
        raise RuntimeError('WEB_API_KEY not set')

    # Configure Flask app
    app.config['llm_model'] = llm_model
    app.config['tts_model'] = tts_model
    app.config['synonyms'] = synonyms

    # Patch the module's API key
    import voice_llama_chat
    voice_llama_chat.WEB_API_KEY = web_key

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    configure_app()
    port = int(os.getenv('WEB_PORT', '8080'))
    host = '0.0.0.0'
    logging.info(f'Starting Diane web interface on {host}:{port}')
    app.run(host=host, port=port)
