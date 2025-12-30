"""
Tests for MCP storage module.
"""

import os
import sqlite3
from pathlib import Path

import pytest

from mcp.models import Document
from mcp.storage import index_docs, setup_db


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


class TestVersionValidation:
    """Test version validation functionality."""

    from mcp.models import VersionType
    from mcp.storage import determine_version_category, validate_version

    def test_validate_version_enum_values(self):
        """Test validation of VersionType enum values."""
        from mcp.models import VersionType
        from mcp.storage import validate_version

        # Test all VersionType enum values
        for version_type in VersionType:
            result = validate_version(version_type.value)
            assert result == version_type.value

    def test_validate_version_semantic_versions(self):
        """Test validation of semantic version strings."""
        from mcp.storage import validate_version

        test_cases = ["1.0.0", "v1.2.3", "2.1.0-beta", "v3.0.0-alpha.1"]

        for version in test_cases:
            result = validate_version(version)
            assert result == version

    def test_validate_version_git_tags(self):
        """Test validation of git tag/ref strings."""
        from mcp.storage import validate_version

        test_cases = ["release-1.0", "v2.1.3", "hotfix-branch", "feature_new_ui"]

        for version in test_cases:
            result = validate_version(version)
            assert result == version

    def test_validate_version_invalid_formats(self):
        """Test validation of invalid version formats."""
        from mcp.models import VersionType
        from mcp.storage import validate_version

        test_cases = [
            "",
            None,
            "invalid version",
            "1.2",  # Missing patch version
            "v1.2.3.4",  # Too many parts
            "@#$%^&*()",  # Invalid characters
        ]

        for version in test_cases:
            result = validate_version(version)
            assert result == VersionType.LATEST.value

    def test_determine_version_category(self):
        """Test version category determination."""
        # Test VersionType enum values
        from mcp.models import VersionType
        from mcp.storage import determine_version_category

        for version_type in VersionType:
            category = determine_version_category(version_type.value)
            assert category == version_type.value

        # Test semantic versions (should return 'latest')
        semantic_versions = ["1.0.0", "v2.1.3", "3.0.0-beta"]
        for version in semantic_versions:
            category = determine_version_category(version)
            assert category == VersionType.LATEST.value

        # Test git tags (should return 'latest')
        git_tags = ["release-1.0", "hotfix-branch"]
        for version in git_tags:
            category = determine_version_category(version)
            assert category == VersionType.LATEST.value


class TestVersionConstraints:
    """Test version constraints and edge cases."""

    def test_version_not_null_constraint(self, temp_dir):
        """Test that version field has NOT NULL constraint."""
        db_path = os.path.join(temp_dir, "test.db")

        # Setup database
        setup_db(db_path)

        # Try to insert a document with NULL version (should fail)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO docs (repo, path, content, version, version_category) VALUES (?, ?, ?, NULL, ?)",
                ("test-repo", "README.md", "# Test", "latest"),
            )
            conn.commit()
            # If we get here, the constraint is not working
            assert False, "NOT NULL constraint should have prevented NULL version"
        except sqlite3.IntegrityError:
            # Expected behavior - NOT NULL constraint working
            pass
        finally:
            conn.close()

    def test_version_default_value(self, temp_dir):
        """Test that version field has correct default value."""
        db_path = os.path.join(temp_dir, "test.db")

        # Setup database
        setup_db(db_path)

        # Insert document without specifying version (should use default)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO docs (repo, path, content, version_category) VALUES (?, ?, ?, ?)",
            ("test-repo", "README.md", "# Test", "latest"),
        )

        # Check that default version was used
        cursor.execute("SELECT version FROM docs WHERE repo = ?", ("test-repo",))
        result = cursor.fetchone()

        assert result[0] == "latest"

        conn.commit()
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
            content="# Test Repository\n\nThis is a test.",
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
            Document(repo="test-repo", path="README.md", content="# Main README"),
            Document(repo="test-repo", path="docs/guide.md", content="# User Guide"),
            Document(repo="another-repo", path="README.md", content="# Another README"),
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
            repo="test-repo", path="README.md", content="# Test", version="v1.2.3"
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

        # Verify column names and types (updated for new schema)
        expected_columns = [
            (0, "id", "INTEGER", 0, None, 1),  # id column (primary key)
            (1, "repo", "TEXT", 1, None, 0),  # repo column (not null)
            (2, "path", "TEXT", 1, None, 0),  # path column (not null)
            (3, "content", "TEXT", 1, None, 0),  # content column (not null)
            (
                4,
                "version",
                "TEXT",
                1,
                "'latest'",
                0,
            ),  # version column (not null with default)
            (
                5,
                "version_category",
                "TEXT",
                1,
                "'latest'",
                0,
            ),  # version_category (not null with default)
            (
                6,
                "created_at",
                "TIMESTAMP",
                0,
                "CURRENT_TIMESTAMP",
                0,
            ),  # created_at timestamp
            (
                7,
                "updated_at",
                "TIMESTAMP",
                0,
                "CURRENT_TIMESTAMP",
                0,
            ),  # updated_at timestamp
        ]

        assert len(columns) == 8

        # Check each column (ignoring some SQLite-specific details)
        for i, expected in enumerate(expected_columns):
            assert columns[i][1] == expected[1]  # column name
            assert columns[i][2] == expected[2]  # data type
            assert columns[i][3] == expected[3]  # not null constraint

        conn.close()

    def test_database_indexes(self, temp_dir):
        """Test that the database has the correct indexes."""
        db_path = os.path.join(temp_dir, "test.db")

        # Setup database
        setup_db(db_path)

        # Get indexes
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA index_list(docs)")
        indexes = cursor.fetchall()

        # Verify expected indexes exist
        expected_index_names = [
            "idx_docs_repo",
            "idx_docs_version",
            "idx_docs_version_category",
            "idx_docs_repo_version",
            "idx_docs_path",
            "idx_docs_full_search",
        ]

        actual_index_names = [index[1] for index in indexes]

        # Check that all expected indexes are present
        for expected_name in expected_index_names:
            assert expected_name in actual_index_names, (
                f"Index {expected_name} not found"
            )

        conn.close()
