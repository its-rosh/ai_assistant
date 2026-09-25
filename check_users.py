from app.database import get_connection

connection = get_connection()

try:
    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT id, email, created_at
            FROM users
            ORDER BY id ASC;
        """)

        users = cursor.fetchall()

        print(f"\nTotal users: {len(users)}\n")

        for user in users:
            print(
                f"ID: {user[0]} | "
                f"Email: {user[1]} | "
                f"Created: {user[2]}"
            )

finally:
    connection.close()