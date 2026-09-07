import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openrouter import OpenRouter

from app.database import (
    get_messages,
    initialize_database,
    save_message,
)


load_dotenv()

app = Flask(__name__)

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenRouter(
    api_key=api_key
)

MODEL_NAME = "inclusionai/ling-3.0-flash-fin:free"

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
    data = request.get_json()

    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Message cannot be empty."}), 400

    stored_messages = get_messages()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful personal AI assistant."
        }
    ]

    for row in stored_messages:
        messages.append(
            {
                "role": row[1],
                "content": row[2],
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    save_message("user", user_input)

    response = client.chat.send(
        model=MODEL_NAME,
        messages=messages,
    )

    assistant_reply = response.choices[0].message.content

    save_message("assistant", assistant_reply)

    return jsonify(
        {
            "reply": assistant_reply
        }
    )


if __name__ == "__main__":
    app.run(debug=True)