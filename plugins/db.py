import psycopg2
import os
from info import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def set_delete_time(chat_id: int, delay: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delete_times (
                    chat_id BIGINT PRIMARY KEY,
                    delay INTEGER NOT NULL
                );
            """)
            cursor.execute("""
                INSERT INTO delete_times (chat_id, delay)
                VALUES (%s, %s)
                ON CONFLICT (chat_id)
                DO UPDATE SET delay = EXCLUDED.delay;
            """, (chat_id, delay))

def get_delete_time(chat_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delete_times (
                    chat_id BIGINT PRIMARY KEY,
                    delay INTEGER NOT NULL
                );
            """)
            cursor.execute("SELECT delay FROM delete_times WHERE chat_id = %s;", (chat_id,))
            row = cursor.fetchone()
            return row[0] if row else None
