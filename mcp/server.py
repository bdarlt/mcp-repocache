from fastapi import FastAPI
from typing import List
from .models import Document
import sqlite3
import os

app = FastAPI()

@app.get("/docs", response_model=List[Document])
def get_docs(repo: str = None):
    db_path = os.path.join(os.path.dirname(__file__), "../../data/sqlite/docs.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if repo:
        cursor.execute("SELECT * FROM docs WHERE repo = ?", (repo,))
    else:
        cursor.execute("SELECT * FROM docs")

    rows = cursor.fetchall()
    docs = [Document(**dict(row)) for row in rows]
    conn.close()
    return docs

