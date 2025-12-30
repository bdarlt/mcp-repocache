#!/usr/bin/env python3

import os
import sqlite3
import tempfile

from mcp.storage import setup_db

# Create a temporary database
with tempfile.NamedTemporaryFile(delete=False) as f:
    db_path = f.name

try:
    setup_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(docs)")
    columns = cursor.fetchall()

    print("Database schema columns:")
    for i, col in enumerate(columns):
        print(f"  {i}: {col}")

    # Test NOT NULL constraint
    print("\nTesting NOT NULL constraint...")
    try:
        cursor.execute(
            "INSERT INTO docs (repo, path, content, version, version_category) VALUES (?, ?, ?, NULL, ?)",
            ("test-repo", "README.md", "# Test", "latest"),
        )
        print("ERROR: NULL version was allowed (constraint not working)")
    except sqlite3.IntegrityError as e:
        print(f"SUCCESS: NOT NULL constraint working - {e}")

    conn.close()
finally:
    os.unlink(db_path)
