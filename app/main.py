import os

from app.auth import auth_bp, login_manager
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from app.database import (
    get_messages,
    initialize_database,
    save_message,
)

from app.rag import answer_question

load_dotenv()

## initialize flask log in
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

login_manager.init_app(app)

app.register_blueprint(auth_bp)   ### Flask-Login uses Flask's session mechanism. The session needs a secret key so Flask can securely sign the session information.

initialize_database()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/history", methods=["GET"])
def history():
    stored_messages = get_messages()

    messages = []

    for row in stored_messages:
        messages.append(
            {
                "role": row[1],
                "content": row[2],
            }
        )

    return jsonify(messages)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify(
            {
                "error": "Message cannot be empty."
            }
        ), 400

    save_message("user", user_input)

    try:
        result = answer_question(user_input)

        assistant_reply = result["answer"]

        sources = result["sources"]

        save_message("assistant", assistant_reply)

        return jsonify(
            {
                "reply": assistant_reply,
                "sources": sources,
            }
        )

    except Exception as error:

        print("RAG error:", error)

        return jsonify(
            {
                "error": "Something went wrong while processing your question."
            }
        ), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )