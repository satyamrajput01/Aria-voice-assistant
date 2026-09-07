import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "aria_memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_memory():
    conn = get_connection()
    cursor = conn.cursor()

    # Long-term memories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Conversation history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# LONG-TERM MEMORY
# =========================================================

def save_memory(category, key, value):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM memories
        WHERE category = ? AND key = ?
    """, (category, key))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE memories
            SET value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (value, existing[0]))
    else:
        cursor.execute("""
            INSERT INTO memories (category, key, value)
            VALUES (?, ?, ?)
        """, (category, key, value))

    conn.commit()
    conn.close()


def get_memory(key):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, key, value
        FROM memories
        WHERE key = ?
        ORDER BY updated_at DESC
        LIMIT 1
    """, (key,))

    result = cursor.fetchone()

    conn.close()

    if result:
        return {
            "category": result[0],
            "key": result[1],
            "value": result[2]
        }

    return None


def get_all_memories():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, key, value
        FROM memories
        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "category": row[0],
            "key": row[1],
            "value": row[2]
        }
        for row in rows
    ]


def delete_memory(key):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE key = ?
    """, (key,))

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


# =========================================================
# CONVERSATION MEMORY
# =========================================================

def save_conversation(role, message):
    """
    Save one conversation message.

    role can be:
    - user
    - assistant
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations (role, message)
        VALUES (?, ?)
    """, (role, message))

    conn.commit()
    conn.close()


def get_recent_conversations(limit=10):
    """
    Get the most recent conversation messages.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message
        FROM conversations
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    # Reverse so oldest message comes first
    rows.reverse()

    return [
        {
            "role": row[0],
            "message": row[1]
        }
        for row in rows
    ]


def clear_conversations():
    """
    Delete conversation history.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM conversations
    """)

    conn.commit()
    conn.close()


# Create database/tables when this module loads
initialize_memory()