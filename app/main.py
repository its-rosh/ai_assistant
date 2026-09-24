import os

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from flask_login import current_user, login_required

from app.auth import auth_bp, login_manager
from app.database import (
    get_messages,
    initialize_database,
    save_message,
)
from app.rag import answer_question


load_dotenv()

# Initialize Flask

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

# Initialize Flask-Login

login_manager.init_app(app)

login_manager.login_view = "login_page"

# Register authentication routes

app.register_blueprint(auth_bp)

# Initialize database

initialize_database()

# Home / Chat Page

@app.route("/")
@login_required
def home():
    return render_template("index.html")

# Login Page

@app.route("/login")
def login_page():
    return render_template("login.html")

# Signup Page

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

# Conversation History

@app.route("/api/history", methods=["GET"])
@login_required
def history():

    stored_messages = get_messages(
        current_user.id
    )

    messages = []

    for row in stored_messages:

        messages.append(
            {
                "role": row[1],
                "content": row[2],
            }
        )

    return jsonify(messages)


# --------------------------------------------------
# Chat
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
@login_required
def chat():

    data = request.get_json(
        silent=True
    ) or {}

    user_input = data.get(
        "message",
        ""
    ).strip()


    if not user_input:

        return jsonify(
            {
                "error": "Message cannot be empty."
            }
        ), 400


    # Save user's message
    save_message(
        current_user.id,
        "user",
        user_input,
    )


    try:

        # Existing RAG system
        result = answer_question(
            user_input
        )

        assistant_reply = result["answer"]

        sources = result["sources"]


        # Save assistant's response
        save_message(
            current_user.id,
            "assistant",
            assistant_reply,
        )


        return jsonify(
            {
                "reply": assistant_reply,
                "sources": sources,
            }
        )


    except Exception as error:

        print(
            "RAG error:",
            error
        )


        return jsonify(
            {
                "error":
                    "Something went wrong while processing your question."
            }
        ), 500

# Start Flask

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )