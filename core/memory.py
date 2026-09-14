import re
import sqlite3
from pathlib import Path


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "aria_memory.db"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

def initialize_memory():

    conn = get_connection()
    cursor = conn.cursor()

    # ------------------------------------------------------
    # LONG-TERM MEMORIES
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # CONVERSATIONS
    # ------------------------------------------------------

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


# ==========================================================
# SAVE MEMORY
# ==========================================================

def save_memory(category, key, value):

    category = str(category).strip()
    key = str(key).strip()
    value = str(value).strip()

    if not category or not key or not value:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM memories
        WHERE category = ? AND key = ?
    """, (category, key))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE memories
            SET value = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (value, existing[0]))

    else:

        cursor.execute("""
            INSERT INTO memories (
                category,
                key,
                value
            )
            VALUES (?, ?, ?)
        """, (
            category,
            key,
            value
        ))

    conn.commit()
    conn.close()


# ==========================================================
# GET ONE MEMORY
# ==========================================================

def get_memory(key):

    if not key:
        return None

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


# ==========================================================
# GET ALL MEMORIES
# ==========================================================

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


# ==========================================================
# NORMALIZE TEXT
# ==========================================================

def _normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================================
# EXTRACT KEYWORDS
# ==========================================================

def _extract_keywords(query):

    normalized = _normalize_text(query)

    if not normalized:
        return []

    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "what",
        "which",
        "where",
        "when",
        "who",
        "how",
        "why",
        "can",
        "could",
        "would",
        "should",
        "does",
        "did",
        "have",
        "has",
        "had",
        "are",
        "was",
        "were",
        "you",
        "your",
        "about",
        "tell",
        "know",
        "please",
        "from",
        "into",
        "want",
        "need",
        "like",
        "love",
        "really",
        "very",
        "mere",
        "meri",
        "mera",
        "mujhe",
        "main",
        "hai",
        "hain",
        "hoon",
        "kya",
        "ka",
        "ki",
        "ke",
        "ko",
        "se",
        "me",
        "par",
        "aur",
        "bhi",
        "toh",
        "to",
        "ye",
        "yeh",
        "woh",
        "vo",
        "is",
        "us",
        "my",
        "i"
    }

    words = normalized.split()

    keywords = []

    for word in words:

        if len(word) < 3:
            continue

        if word in stop_words:
            continue

        if word not in keywords:
            keywords.append(word)

    return keywords


# ==========================================================
# SEARCH LONG-TERM MEMORIES
# ==========================================================

def search_memories(query, limit=5):

    if not query:
        return []

    try:

        limit = int(limit)

    except (TypeError, ValueError):

        limit = 5

    if limit <= 0:
        return []

    keywords = _extract_keywords(query)

    if not keywords:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            category,
            key,
            value,
            updated_at
        FROM memories
        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    scored_memories = []

    for row in rows:

        memory_id = row[0]
        category = row[1]
        key = row[2]
        value = row[3]
        updated_at = row[4]

        category_text = _normalize_text(
            category
        )

        key_text = _normalize_text(
            key
        )

        value_text = _normalize_text(
            value
        )

        combined_text = (
            f"{category_text} "
            f"{key_text} "
            f"{value_text}"
        )

        score = 0

        matched_keywords = []

        for keyword in keywords:

            if keyword in key_text.split():

                score += 5

                matched_keywords.append(
                    keyword
                )

                continue

            if keyword in category_text.split():

                score += 3

                matched_keywords.append(
                    keyword
                )

                continue

            if keyword in value_text.split():

                score += 3

                matched_keywords.append(
                    keyword
                )

                continue

            if keyword in combined_text:

                score += 1

                matched_keywords.append(
                    keyword
                )

        if score > 0:

            scored_memories.append({
                "id": memory_id,
                "category": category,
                "key": key,
                "value": value,
                "updated_at": updated_at,
                "score": score,
                "matched_keywords": len(
                    set(matched_keywords)
                )
            })

    scored_memories.sort(
        key=lambda memory: (
            memory["score"],
            memory["matched_keywords"],
            memory["updated_at"] or ""
        ),
        reverse=True
    )

    return [
        {
            "category": memory["category"],
            "key": memory["key"],
            "value": memory["value"]
        }
        for memory in scored_memories[:limit]
    ]


# ==========================================================
# DELETE MEMORY
# ==========================================================

def delete_memory(key):

    if not key:
        return False

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


# ==========================================================
# SAVE CONVERSATION
# ==========================================================

def save_conversation(role, message):

    if not role or not message:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations (
            role,
            message
        )
        VALUES (?, ?)
    """, (
        role,
        message
    ))

    conn.commit()
    conn.close()


# ==========================================================
# GET RECENT CONVERSATIONS
# ==========================================================

def get_recent_conversations(limit=10):

    try:

        limit = int(limit)

    except (TypeError, ValueError):

        limit = 10

    if limit <= 0:
        return []

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

    rows.reverse()

    return [
        {
            "role": row[0],
            "message": row[1]
        }
        for row in rows
    ]


# ==========================================================
# SEARCH CONVERSATIONS
# ==========================================================

def search_conversations(
    query,
    limit=5
):

    if not query:
        return []

    try:

        limit = int(limit)

    except (TypeError, ValueError):

        limit = 5

    if limit <= 0:
        return []

    keywords = _extract_keywords(query)

    if not keywords:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            role,
            message,
            created_at
        FROM conversations
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    scored_conversations = []

    for row in rows:

        conversation_id = row[0]
        role = row[1]
        message = row[2]
        created_at = row[3]

        normalized_message = _normalize_text(
            message
        )

        message_words = set(
            normalized_message.split()
        )

        score = 0
        matched_keywords = []

        for keyword in keywords:

            if keyword in message_words:

                score += 4

                matched_keywords.append(
                    keyword
                )

            elif keyword in normalized_message:

                score += 2

                matched_keywords.append(
                    keyword
                )

        if score > 0:

            scored_conversations.append({
                "id": conversation_id,
                "role": role,
                "message": message,
                "created_at": created_at,
                "score": score,
                "matched_keywords": len(
                    set(matched_keywords)
                )
            })

    scored_conversations.sort(
        key=lambda conversation: (
            conversation["score"],
            conversation["matched_keywords"],
            conversation["id"]
        ),
        reverse=True
    )

    return [
        {
            "role": conversation["role"],
            "message": conversation["message"],
            "created_at": conversation["created_at"]
        }
        for conversation in scored_conversations[:limit]
    ]


# ==========================================================
# CLEAR CONVERSATIONS
# ==========================================================

def clear_conversations():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM conversations
    """)

    conn.commit()
    conn.close()


# ==========================================================
# INITIALIZE
# ==========================================================

initialize_memory()