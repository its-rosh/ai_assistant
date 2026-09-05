import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
    )


def save_message(role, content):
    connection = get_connection()# save_message() --> get_connection() --> PostgreSQL

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (role, content)
        VALUES (%s, %s); -- parameterized queries separater
        """,
        (role, content),
    )

    connection.commit()

    cursor.close()
    connection.close()


def get_messages():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, role, content, created_at
        FROM conversations
        ORDER BY created_at ASC;
        """
    )

    messages = cursor.fetchall()

    cursor.close()
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
CLOSE CONNECTION 
"""
if __name__ == "__main__":
    save_message("user", "Testing PostgreSQL memory.")

    messages = get_messages()

    for message in messages:
        print(message)