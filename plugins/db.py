# db.py
import psycopg2
import os
from info import DATABASE_URL




conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS delete_times (
    chat_id BIGINT PRIMARY KEY,
    seconds INTEGER
);
""")
conn.commit()

def set_delete_time(chat_id: int, seconds: int):
    cursor.execute(
        """
        INSERT INTO delete_times (chat_id, seconds)
        VALUES (%s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET seconds = EXCLUDED.seconds;
        """,
        (chat_id, seconds)
    )
    conn.commit()

def get_delete_time(chat_id: int):
    cursor.execute("SELECT seconds FROM delete_times WHERE chat_id = %s", (chat_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_all_delete_times():
    cursor.execute("SELECT chat_id, seconds FROM delete_times")
    return dict(cursor.fetchall())
