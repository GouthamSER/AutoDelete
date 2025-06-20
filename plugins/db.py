import psycopg2
import os


# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS delete_times (
        chat_id BIGINT PRIMARY KEY,
        delay INTEGER NOT NULL
    );
""")

def set_delete_time(chat_id: int, delay: int):
    cursor.execute("""
        INSERT INTO delete_times (chat_id, delay)
        VALUES (%s, %s)
        ON CONFLICT (chat_id)
        DO UPDATE SET delay = EXCLUDED.delay;
    """, (chat_id, delay))

def get_delete_time(chat_id: int):
    cursor.execute("SELECT delay FROM delete_times WHERE chat_id = %s;", (chat_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None
