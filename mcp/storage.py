import sqlite3
from typing import List

from .models import Document, VersionType


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
            version TEXT DEFAULT 'latest',
            version_category TEXT DEFAULT 'latest'
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
        # Determine version category (this could be moved to a helper function)
        version_category = doc.version
        if doc.version in [vt.value for vt in VersionType]:
            version_category = doc.version
        else:
            # If it's a specific version/tag, use 'latest' as the category
            version_category = VersionType.LATEST.value

        cursor.execute(
            "INSERT INTO docs (repo, path, content, version, version_category) VALUES (?, ?, ?, ?, ?)",
            (doc.repo, doc.path, doc.content, doc.version, version_category),
        )

    conn.commit()
    conn.close()
