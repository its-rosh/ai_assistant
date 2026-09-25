"""This file will handle:

user lookup
signup
login
logout
password hashing
Flask-Login session management"""

from flask import Blueprint, request, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
    logout_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import get_connection


login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, user_id, email):
        self.id = user_id
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email
                FROM users
                WHERE id = %s;
                """,
                (user_id,),
            )

            row = cursor.fetchone()

            if row:
                return User(row[0], row[1])

            return None

    finally:
        connection.close()


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    password_hash = generate_password_hash(password)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s;
                """,
                (email,),
            )

            existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({
                    "error": "An account with that email already exists."
                }), 409

            cursor.execute(
                """
                INSERT INTO users (email, password_hash)
                VALUES (%s, %s)
                RETURNING id, email;
                """,
                (email, password_hash),
            )

            user_id, user_email = cursor.fetchone()

            connection.commit()

            user = User(user_id, user_email)
            login_user(user)

            return jsonify({
                "message": "Account created successfully.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
            }), 201

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, password_hash
                FROM users
                WHERE email = %s;
                """,
                (email,),
            )

            row = cursor.fetchone()

            if not row:
                return jsonify({
                    "error": "Invalid email or password."
                }), 401

            user_id, user_email, password_hash = row

            if not check_password_hash(password_hash, password):
                return jsonify({
                    "error": "Invalid email or password."
                }), 401

            user = User(user_id, user_email)
            login_user(user)

            return jsonify({
                "message": "Login successful.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
            })

    finally:
        connection.close()


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()

    return jsonify({
        "message": "Logged out successfully."
    })

@auth_bp.route("/api/me", methods=["GET"])
def me():
    if not current_user.is_authenticated:
        return jsonify({
            "authenticated": False
        }), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
        },
    })