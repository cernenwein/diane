#!/home/diane/diane/.venv/bin/python3
from flask import Flask, request, jsonify, render_template, redirect
from dotenv import load_dotenv
from llama_cpp import Llama
import os

# Load environment
load_dotenv("/home/diane/diane/.env")

app = Flask(__name__, template_folder="templates")

# Load model
model_path = os.getenv("LLM_MODEL_PATH", "/mnt/ssd/models/llm/current_model.gguf")
if not os.path.exists(model_path):
    raise RuntimeError(f"❌ LLM model not found at {model_path}")

print(f"🧠 Loading model from: {model_path}")
llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4)

# Store chat history in memory
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
    user_input = data.get("query", "").strip()
    chat_history.append({"sender": "user", "text": user_input})

    # Basic LLM prompt formatting
    prompt = f"User: {user_input}\nAssistant:"

    # Run model and get output
    output = llm(prompt, stop=["User:", "Assistant:"], echo=False)
    response_text = output["choices"][0]["text"].strip()

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
