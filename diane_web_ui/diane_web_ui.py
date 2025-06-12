#!/home/diane/diane/.venv/bin/python3
"""diane_web_ui.py

Flask-based web UI for Diane with login and chat interface.
Loads configuration from .env.
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, session, redirect, url_for, render_template, jsonify

# Load environment variables
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'changeme')

# Credentials
USERNAME = os.getenv('WEB_USERNAME', 'diane')
PASSWORD = os.getenv('WEB_PASSWORD', 'diane')

# LLM interface
from voice_llama_chat import generate_with_llm

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == USERNAME and request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('chat'))
        error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 403
    data = request.get_json() or {}
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({'error': 'Empty message'}), 400
    llm_path = os.getenv('LLM_MODEL_PATH')
    response = generate_with_llm(llm_path, msg)
    return jsonify({'response': response})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', '8080'))
    host = '0.0.0.0'
    app.run(host=host, port=port)
