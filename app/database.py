import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    Create and return a PostgreSQL database connection.

    Locally:
        Uses individual DATABASE_* environment variables.

    On Render:
        Uses DATABASE_URL provided by Render.
    """

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg.connect(database_url)

    return psycopg.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
    )


def initialize_database():
    """
    Create the conversations table if it does not already exist.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )


def save_message(user_id, role, content):
    """
    Save one message for a specific authenticated user.
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO conversations (user_id, role, content)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (user_id, role, content),
            )

            message_id = cursor.fetchone()[0]

            return message_id


def get_messages(user_id):
    """
    Retrieve conversation history for one specific user.
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, role, content, created_at
                FROM conversations
                WHERE user_id = %s
                ORDER BY id ASC;
                """,
                (user_id,),
            )

            return cursor.fetchall()

"""User
    │
"Hello"
    ▼
Flask /api/chat
    │
    ▼
get_messages()
    │
    ▼
PostgreSQL
    │
    ▼
Previous messages
    │
    ▼
messages[]
    │   
    ▼
OpenRouter
    │
    ▼
Ling 3.0
    │
    ▼
Assistant response
    │
    ▼
save_message()
    │
    ▼
PostgreSQL """
