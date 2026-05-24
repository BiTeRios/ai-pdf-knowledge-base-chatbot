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
        cursor.execute(
            """
            INSERT INTO chunks (file_name, page_number, chunk_index, text)
            VALUES (?, ?, ?, ?)
            """,
            (
                file_name,
                chunk["page_number"],
                chunk["chunk_index"],
                chunk["text"],
            ),
        )

    connection.commit()
    connection.close()


def get_all_chunks() -> List[Dict[str, Any]]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, file_name, page_number, chunk_index, text
        FROM chunks
        ORDER BY id ASC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


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