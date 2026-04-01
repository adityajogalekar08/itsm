from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import run_agent
from voice_routes import voice_bp
app = Flask(__name__)
CORS(app)
app.register_blueprint(voice_bp)
conversation_store = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id", "default")
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation_store[session_id].append({
        "role": "user",
        "content": user_message
    })

    response = run_agent(conversation_store[session_id])

    conversation_store[session_id].append({
        "role": "assistant",
        "content": response["message"]
    })

    return jsonify(response)

@app.route("/reset", methods=["POST"])
def reset():
    data = request.json
    session_id = data.get("session_id", "default")
    conversation_store[session_id] = []
    return jsonify({"status": "reset successful"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)