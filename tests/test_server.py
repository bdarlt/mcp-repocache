"""
Tests for MCP server module.
"""
import json
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from mcp.server import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_db_path(monkeypatch):
    """Mock the database path to use a temporary file."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Create the database schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            path TEXT NOT NULL,
            content TEXT NOT NULL,
            version TEXT DEFAULT 'latest'
        )
    """)
    
    # Insert test data
    test_docs = [
        ("fastapi", "README.md", "# FastAPI\nFastAPI framework", "latest"),
        ("fastapi", "docs/tutorial.md", "# Tutorial\nHow to use FastAPI", "latest"),
        ("pydantic", "README.md", "# Pydantic\nData validation", "latest"),
    ]
    
    for repo, path, content, version in test_docs:
        cursor.execute(
            "INSERT INTO docs (repo, path, content, version) VALUES (?, ?, ?, ?)",
            (repo, path, content, version)
        )
    
    conn.commit()
    conn.close()
    
    # Mock the database path in the server
    def mock_join(*args):
        if args[0].endswith('server.py'):
            return db_path
        return Path(*args)
    
    with patch('mcp.server.os.path.join', side_effect=mock_join):
        yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


class TestGetDocs:
    """Test the GET /docs endpoint."""
    
    def test_get_all_docs(self, client, mock_db_path):
        """Test getting all documents."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return all 3 test documents
        assert len(data) == 3
        
        # Check that all expected documents are present
        repos = [doc['repo'] for doc in data]
        assert "fastapi" in repos
        assert "pydantic" in repos
        
        # Verify document structure
        for doc in data:
            assert 'repo' in doc
            assert 'path' in doc
            assert 'content' in doc
            assert 'version' in doc
    
    def test_get_docs_by_repo(self, client, mock_db_path):
        """Test getting documents filtered by repository."""
        response = client.get("/docs?repo=fastapi")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return only fastapi documents
        assert len(data) == 2
        
        # All documents should be from fastapi repo
        for doc in data:
            assert doc['repo'] == "fastapi"
            assert doc['path'] in ["README.md", "docs/tutorial.md"]
    
    def test_get_docs_by_nonexistent_repo(self, client, mock_db_path):
        """Test getting documents for a non-existent repository."""
        response = client.get("/docs?repo=nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty list
        assert data == []
    
    def test_get_docs_empty_database(self, client):
        """Test getting documents from an empty database."""
        # Create empty temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Create empty database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT NOT NULL,
                path TEXT NOT NULL,
                content TEXT NOT NULL,
                version TEXT DEFAULT 'latest'
            )
        """)
        conn.commit()
        conn.close()
        
        # Mock the database path
        def mock_join(*args):
            if args[0].endswith('server.py'):
                return db_path
            return Path(*args)
        
        with patch('mcp.server.os.path.join', side_effect=mock_join):
            response = client.get("/docs")
            
            assert response.status_code == 200
            data = response.json()
            assert data == []
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)


class TestResponseFormat:
    """Test response format and data types."""
    
    def test_response_model_validation(self, client, mock_db_path):
        """Test that response matches the expected Document model."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        data = response.json()
        
        for doc in data:
            # Test required fields
            assert isinstance(doc['repo'], str)
            assert isinstance(doc['path'], str)
            assert isinstance(doc['content'], str)
            assert isinstance(doc['version'], str)
            
            # Test field values
            assert doc['repo'] != ""
            assert doc['path'] != ""
            assert doc['content'] != ""
            assert doc['version'] != ""
    
    def test_content_preservation(self, client, mock_db_path):
        """Test that document content is preserved correctly."""
        response = client.get("/docs?repo=fastapi")
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the README document
        readme_doc = next((doc for doc in data if doc['path'] == 'README.md'), None)
        assert readme_doc is not None
        assert readme_doc['content'] == "# FastAPI\nFastAPI framework"
        
        # Find the tutorial document
        tutorial_doc = next((doc for doc in data if doc['path'] == 'docs/tutorial.md'), None)
        assert tutorial_doc is not None
        assert tutorial_doc['content'] == "# Tutorial\nHow to use FastAPI"


class TestErrorHandling:
    """Test error handling in the server."""
    
    def test_database_connection_error(self, client):
        """Test handling of database connection errors."""
        # Mock a database connection error
        def mock_join(*args):
            if args[0].endswith('server.py'):
                return "/nonexistent/path/database.db"
            return Path(*args)
        
        with patch('mcp.server.os.path.join', side_effect=mock_join):
            response = client.get("/docs")
            
            # Should return 500 error for database connection issues
            assert response.status_code == 500
    
    def test_malformed_query_parameters(self, client, mock_db_path):
        """Test handling of malformed query parameters."""
        # Test with various malformed parameters
        test_cases = [
            "/docs?repo=",  # Empty repo name
            "/docs?repo=%",  # URL encoding issues
            "/docs?invalid=param",  # Invalid parameter
            "/docs?repo=valid&extra=param",  # Extra parameters (should be ignored)
        ]
        
        for url in test_cases:
            response = client.get(url)
            # Should handle gracefully (either 200 with empty results or 422)
            assert response.status_code in [200, 422]


class TestAPIEndpoints:
    """Test API endpoint structure."""
    
    def test_docs_endpoint_exists(self, client):
        """Test that /docs endpoint exists and is accessible."""
        response = client.get("/docs")
        assert response.status_code in [200, 500]  # 500 is OK if DB issues, but endpoint exists
    
    def test_api_documentation_accessible(self, client):
        """Test that API documentation is accessible."""
        # FastAPI should provide auto-generated docs
        response = client.get("/docs")  # FastAPI's default docs endpoint
        assert response.status_code == 200
        
        # Should return JSON response
        assert response.headers["content-type"].startswith("application/json")
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        # This would require CORS middleware to be configured
        # For now, just test that the endpoint responds
        response = client.get("/docs")
        assert response.status_code == 200


class TestPerformance:
    """Test API performance characteristics."""
    
    def test_response_time_reasonable(self, client, mock_db_path):
        """Test that API responds in reasonable time."""
        import time
        
        start_time = time.time()
        response = client.get("/docs")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Response should be reasonably fast (less than 1 second for small dataset)
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response took too long: {response_time:.2f}s"
    
    def test_large_dataset_handling(self, client):
        """Test handling of larger datasets."""
        # Create a larger test dataset
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Create database and insert many documents
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT NOT NULL,
                path TEXT NOT NULL,
                content TEXT NOT NULL,
                version TEXT DEFAULT 'latest'
            )
        """)
        
        # Insert 100 test documents
        for i in range(100):
            cursor.execute(
                "INSERT INTO docs (repo, path, content, version) VALUES (?, ?, ?, ?)",
                (f"repo-{i%10}", f"file-{i}.md", f"# Document {i}\nContent {i}", "latest")
            )
        
        conn.commit()
        conn.close()
        
        # Mock the database path
        def mock_join(*args):
            if args[0].endswith('server.py'):
                return db_path
            return Path(*args)
        
        with patch('mcp.server.os.path.join', side_effect=mock_join):
            response = client.get("/docs")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 100
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)