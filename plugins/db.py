import sqlite3

conn = sqlite3.connect("delete_times.db", check_same_thread=False)
cur = conn.cursor()

# Create the table to store delete times per group
cur.execute("""
CREATE TABLE IF NOT EXISTS delete_times (
    chat_id INTEGER PRIMARY KEY,
    delay INTEGER
)
""")
conn.commit()

def set_delete_time(chat_id: int, delay: int):
    cur.execute("REPLACE INTO delete_times (chat_id, delay) VALUES (?, ?)", (chat_id, delay))
    conn.commit()

def get_delete_time(chat_id: int) -> int | None:
    cur.execute("SELECT delay FROM delete_times WHERE chat_id = ?", (chat_id,))
    row = cur.fetchone()
    return row[0] if row else None

def load_all_delete_times() -> dict:
    cur.execute("SELECT chat_id, delay FROM delete_times")
    return {chat_id: delay for chat_id, delay in cur.fetchall()}
