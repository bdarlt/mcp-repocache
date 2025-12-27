"""
Tests for MCP models.
"""
import pytest
from mcp.models import Document, Repository


class TestDocument:
    """Test Document model."""
    
    def test_document_creation(self):
        """Test creating a Document instance."""
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test\nContent",
            version="v1.0"
        )
        
        assert doc.repo == "test-repo"
        assert doc.path == "README.md"
        assert doc.content == "# Test\nContent"
        assert doc.version == "v1.0"
    
    def test_document_default_version(self):
        """Test Document with default version."""
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test\nContent"
        )
        
        assert doc.version == "latest"
    
    def test_document_validation(self):
        """Test Document validation."""
        # Valid document
        doc = Document(
            repo="test-repo",
            path="docs/guide.md",
            content="# Guide\nThis is a guide."
        )
        assert doc.repo == "test-repo"
        assert doc.path == "docs/guide.md"
        
        # Test with empty content
        doc_empty = Document(
            repo="test-repo",
            path="empty.md",
            content=""
        )
        assert doc_empty.content == ""


class TestRepository:
    """Test Repository model."""
    
    def test_repository_creation(self):
        """Test creating a Repository instance."""
        repo = Repository(
            url="https://github.com/user/repo.git",
            name="my-repo",
            branch="main"
        )
        
        assert repo.url == "https://github.com/user/repo.git"
        assert repo.name == "my-repo"
        assert repo.branch == "main"
    
    def test_repository_defaults(self):
        """Test Repository with default values."""
        repo = Repository(
            url="https://github.com/user/repo.git"
        )
        
        assert repo.url == "https://github.com/user/repo.git"
        assert repo.name is None
        assert repo.branch == "main"
    
    def test_repository_name_extraction(self):
        """Test repository name extraction from URL."""
        repo = Repository(
            url="https://github.com/user/my-repository.git"
        )
        
        # Name should be None since not explicitly set
        assert repo.name is None
        
        # But we can extract it manually
        extracted_name = repo.url.split("/")[-1].replace(".git", "")
        assert extracted_name == "my-repository"


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_document_serialization(self):
        """Test Document JSON serialization."""
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test\nContent",
            version="v1.0"
        )
        
        doc_dict = doc.model_dump()
        expected = {
            "repo": "test-repo",
            "path": "README.md",
            "content": "# Test\nContent",
            "version": "v1.0"
        }
        assert doc_dict == expected
    
    def test_document_deserialization(self):
        """Test Document creation from dictionary."""
        data = {
            "repo": "test-repo",
            "path": "README.md",
            "content": "# Test\nContent",
            "version": "v1.0"
        }
        
        doc = Document(**data)
        assert doc.repo == "test-repo"
        assert doc.path == "README.md"
        assert doc.content == "# Test\nContent"
        assert doc.version == "v1.0"