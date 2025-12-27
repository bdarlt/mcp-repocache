"""
Tests for MCP storage module.
"""
import sqlite3
import os
import pytest
from pathlib import Path
from mcp.storage import setup_db, index_docs
from mcp.models import Document


class TestSetupDb:
    """Test database setup functionality."""
    
    def test_setup_db_creates_table(self, temp_dir):
        """Test that setup_db creates the docs table."""
        db_path = os.path.join(temp_dir, "test.db")
        
        # Setup database
        setup_db(db_path)
        
        # Verify table exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if docs table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='docs'"
        )
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == "docs"
        
        conn.close()
    
    def test_setup_db_idempotent(self, temp_dir):
        """Test that setup_db can be called multiple times safely."""
        db_path = os.path.join(temp_dir, "test.db")
        
        # Setup database twice
        setup_db(db_path)
        setup_db(db_path)
        
        # Should not raise any errors
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify table still exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='docs'"
        )
        result = cursor.fetchone()
        
        assert result is not None
        conn.close()


class TestIndexDocs:
    """Test document indexing functionality."""
    
    def test_index_single_document(self, temp_dir):
        """Test indexing a single document."""
        db_path = os.path.join(temp_dir, "test.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        # Create a test document
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test Repository\n\nThis is a test."
        )
        
        # Index the document
        index_docs([doc], zim_dir, db_path)
        
        # Verify document was stored
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docs")
        rows = cursor.fetchall()
        
        assert len(rows) == 1
        row = rows[0]
        assert row[1] == "test-repo"  # repo column
        assert row[2] == "README.md"  # path column
        assert row[3] == "# Test Repository\n\nThis is a test."  # content column
        assert row[4] == "latest"  # version column
        
        conn.close()
    
    def test_index_multiple_documents(self, temp_dir):
        """Test indexing multiple documents."""
        db_path = os.path.join(temp_dir, "test.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        # Create multiple test documents
        docs = [
            Document(
                repo="test-repo",
                path="README.md",
                content="# Main README"
            ),
            Document(
                repo="test-repo",
                path="docs/guide.md",
                content="# User Guide"
            ),
            Document(
                repo="another-repo",
                path="README.md",
                content="# Another README"
            )
        ]
        
        # Index the documents
        index_docs(docs, zim_dir, db_path)
        
        # Verify all documents were stored
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docs ORDER BY repo, path")
        rows = cursor.fetchall()
        
        assert len(rows) == 3
        
        # Check first document
        assert rows[0][1] == "another-repo"
        assert rows[0][2] == "README.md"
        assert rows[0][3] == "# Another README"
        
        # Check second document
        assert rows[1][1] == "test-repo"
        assert rows[1][2] == "README.md"
        assert rows[1][3] == "# Main README"
        
        # Check third document
        assert rows[2][1] == "test-repo"
        assert rows[2][2] == "docs/guide.md"
        assert rows[2][3] == "# User Guide"
        
        conn.close()
    
    def test_index_empty_list(self, temp_dir):
        """Test indexing an empty list of documents."""
        db_path = os.path.join(temp_dir, "test.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        # Index empty list
        index_docs([], zim_dir, db_path)
        
        # Verify no documents were stored
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docs")
        rows = cursor.fetchall()
        
        assert len(rows) == 0
        conn.close()
    
    def test_index_document_with_version(self, temp_dir):
        """Test indexing a document with explicit version."""
        db_path = os.path.join(temp_dir, "test.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        # Create a document with version
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test",
            version="v1.2.3"
        )
        
        # Index the document
        index_docs([doc], zim_dir, db_path)
        
        # Verify version was stored
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docs")
        rows = cursor.fetchall()
        
        assert len(rows) == 1
        assert rows[0][4] == "v1.2.3"  # version column
        
        conn.close()


class TestDatabaseSchema:
    """Test database schema validation."""
    
    def test_database_schema(self, temp_dir):
        """Test that the database has the correct schema."""
        db_path = os.path.join(temp_dir, "test.db")
        
        # Setup database
        setup_db(db_path)
        
        # Get table schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(docs)")
        columns = cursor.fetchall()
        
        # Verify column names and types
        expected_columns = [
            (0, 'id', 'INTEGER', 1, None, 1),  # id column (primary key)
            (1, 'repo', 'TEXT', 1, None, 0),   # repo column (not null)
            (2, 'path', 'TEXT', 1, None, 0),   # path column (not null)
            (3, 'content', 'TEXT', 1, None, 0), # content column (not null)
            (4, 'version', 'TEXT', 0, None, 0)  # version column (nullable)
        ]
        
        assert len(columns) == 5
        
        # Check each column (ignoring some SQLite-specific details)
        for i, expected in enumerate(expected_columns):
            assert columns[i][1] == expected[1]  # column name
            assert columns[i][2] == expected[2]  # data type
            assert columns[i][3] == expected[3]  # not null constraint
        
        conn.close()