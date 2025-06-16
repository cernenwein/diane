#!/home/diane/diane/.venv/bin/python3
from flask import Flask, request, jsonify, render_template, redirect
import os
from dotenv import load_dotenv

load_dotenv("/home/diane/diane/.env")

app = Flask(__name__, template_folder="templates")

chat_history = []

@app.route("/")
def root():
    return redirect("/chat")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_input = data.get("query", "")
    chat_history.append({"sender": "user", "text": user_input})

    # Placeholder response logic — replace with actual LLM call
    response_text = "This is a mock response to: " + user_input

    chat_history.append({"sender": "ai", "text": response_text})
    return jsonify({"response": response_text})

@app.route("/history")
def history():
    return jsonify({"history": chat_history[-200:]})

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.getenv("WEB_PORT", 8080))
    app.run(host="0.0.0.0", port=port)
