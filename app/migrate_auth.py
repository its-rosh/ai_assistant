from app.database import get_connection


def migrate():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                ALTER TABLE conversations
                ADD COLUMN IF NOT EXISTS user_id INTEGER;
            """)

            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'conversations_user_id_fkey'
                    ) THEN
                        ALTER TABLE conversations
                        ADD CONSTRAINT conversations_user_id_fkey
                        FOREIGN KEY (user_id)
                        REFERENCES users(id)
                        ON DELETE CASCADE;
                    END IF;
                END
                $$;
            """)

            connection.commit()

        print("Authentication database migration completed.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate()