import sqlite3
import os
from typing import List
from .models import Document

def setup_db(db_path: str):
    """Initialize the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            path TEXT NOT NULL,
            content TEXT NOT NULL,
            version TEXT DEFAULT 'latest'
        )
        """
    )
    conn.commit()
    conn.close()

def index_docs(docs: List[Document], zim_dir: str, db_path: str):
    """Store documents in Zim and SQLite."""
    setup_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for doc in docs:
        cursor.execute(
            "INSERT INTO docs (repo, path, content) VALUES (?, ?, ?)",
            (doc.repo, doc.path, doc.content),
        )

    conn.commit()
    conn.close()

