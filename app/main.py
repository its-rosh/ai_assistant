import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from app.database import (
    get_messages,
    initialize_database,
    save_message,
)

from app.rag import answer_question

load_dotenv()

app = Flask(__name__)

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


###