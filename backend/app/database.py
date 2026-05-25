import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "knowledge_base.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    return any(column["name"] == column_name for column in columns)


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            page_number INTEGER,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            embedding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    if not column_exists(cursor, "chunks", "embedding"):
        cursor.execute("ALTER TABLE chunks ADD COLUMN embedding TEXT")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def insert_chunks(file_name: str, chunks: List[Dict[str, Any]]):
    connection = get_connection()
    cursor = connection.cursor()

    for chunk in chunks:
        embedding = chunk.get("embedding")
        embedding_json = json.dumps(embedding) if embedding else None

        cursor.execute(
            """
            INSERT INTO chunks (file_name, page_number, chunk_index, text, embedding)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                file_name,
                chunk["page_number"],
                chunk["chunk_index"],
                chunk["text"],
                embedding_json,
            ),
        )

    connection.commit()
    connection.close()


def get_all_chunks() -> List[Dict[str, Any]]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, file_name, page_number, chunk_index, text, embedding
        FROM chunks
        ORDER BY id ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    chunks = []

    for row in rows:
        chunk = dict(row)

        if chunk.get("embedding"):
            try:
                chunk["embedding"] = json.loads(chunk["embedding"])
            except json.JSONDecodeError:
                chunk["embedding"] = None
        else:
            chunk["embedding"] = None

        chunks.append(chunk)

    return chunks


def get_document_stats() -> List[Dict[str, Any]]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 
            file_name,
            COUNT(*) AS chunks_count,
            MIN(page_number) AS first_page,
            MAX(page_number) AS last_page
        FROM chunks
        GROUP BY file_name
        ORDER BY file_name ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def delete_all_chunks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM chunks")

    connection.commit()
    connection.close()


def save_chat_message(question: str, answer: str, sources: List[Dict[str, Any]]):
    connection = get_connection()
    cursor = connection.cursor()

    sources_json = json.dumps(sources, ensure_ascii=False)

    cursor.execute(
        """
        INSERT INTO chat_history (question, answer, sources_json)
        VALUES (?, ?, ?)
        """,
        (question, answer, sources_json),
    )

    connection.commit()
    connection.close()


def get_chat_history(limit: int = 20) -> List[Dict[str, Any]]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, question, answer, sources_json, created_at
        FROM chat_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    connection.close()

    history = []

    for row in rows:
        item = dict(row)

        if item.get("sources_json"):
            try:
                item["sources"] = json.loads(item["sources_json"])
            except json.JSONDecodeError:
                item["sources"] = []
        else:
            item["sources"] = []

        del item["sources_json"]

        history.append(item)

    return history


def delete_chat_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM chat_history")

    connection.commit()
    connection.close()