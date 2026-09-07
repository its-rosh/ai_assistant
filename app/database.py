import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
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
    connection = get_connection()

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

    connection.commit()
    connection.close()


def save_message(role, content):
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO conversations (role, content)
            VALUES (%s, %s);
            """,
            (role, content),
        )

    connection.commit()
    connection.close()


def get_messages():
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, role, content, created_at
            FROM conversations
            ORDER BY created_at ASC;
            """
        )

        messages = cursor.fetchall()

    connection.close()

    return messages

"""GET CONNECTION
        ↓
CREATE CURSOR
        ↓
EXECUTE SQL
        ↓
COMMIT
        ↓  
CLOSE CURSOR
        ↓
CLOSE CONNECTION """
