"""
Tests for MCP semantic indexing module.
"""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import numpy as np
from mcp.models import Document
from fastapi.testclient import TestClient
from mcp.server import app


class TestGenerateEmbeddings:
    """Test embedding generation functionality."""
    
    def test_generate_embeddings_empty_list(self):
        """Test generating embeddings for empty text list."""
        from mcp.semantic import generate_embeddings
        
        result = generate_embeddings([])
        assert result == []
    
    def test_generate_embeddings_single_text(self):
        """Test generating embeddings for a single text."""
        from mcp.semantic import generate_embeddings
        
        texts = ["This is a test document about Python programming."]
        
        # Mock the embedding generation
        with patch('mcp.semantic._create_embeddings') as mock_create:
            mock_create.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
            
            result = generate_embeddings(texts)
            
            assert len(result) == 1
            assert isinstance(result[0], np.ndarray)
            assert result[0].shape == (768,)
    
    def test_generate_embeddings_multiple_texts(self):
        """Test generating embeddings for multiple texts."""
        from mcp.semantic import generate_embeddings
        
        texts = [
            "Python is a programming language.",
            "FastAPI is a web framework.",
            "Machine learning is a subset of AI."
        ]
        
        with patch('mcp.semantic._create_embeddings') as mock_create:
            mock_create.return_value = np.array([
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
                [0.7, 0.8, 0.9]
            ])
            
            result = generate_embeddings(texts)
            
            assert len(result) == 3
            assert all(isinstance(emb, np.ndarray) for emb in result)
            assert all(emb.shape == (768,) for emb in result)
    
    def test_generate_embeddings_large_text(self):
        """Test generating embeddings for large text."""
        from mcp.semantic import generate_embeddings
        
        # Create a large text (10KB)
        large_text = "Python programming. " * 500
        texts = [large_text]
        
        with patch('mcp.semantic._create_embeddings') as mock_create:
            mock_create.return_value = np.array([[0.1] * 768])  # BERT-like embedding size
            
            result = generate_embeddings(texts)
            
            assert len(result) == 1
            assert result[0].shape == (768,)
    
    def test_generate_embeddings_with_special_characters(self):
        """Test generating embeddings for texts with special characters."""
        from mcp.semantic import generate_embeddings
        
        texts = [
            "Code with special chars: @#$%^&*()",
            "Unicode: 你好世界 🌍 émojis",
            "Code blocks: ```python\nprint('hello')\n```"
        ]
        
        with patch('mcp.semantic._create_embeddings') as mock_create:
            mock_create.return_value = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
            
            result = generate_embeddings(texts)
            
            assert len(result) == 3
            assert all(isinstance(emb, np.ndarray) for emb in result)


class TestIndexRepo:
    """Test repository indexing functionality."""
    
    def test_index_repo_basic(self, temp_dir):
        """Test basic repository indexing."""
        from mcp.semantic import index_repo
        
        zim_dir = os.path.join(temp_dir, "zim")
        vector_dir = os.path.join(temp_dir, "vectors")
        os.makedirs(zim_dir, exist_ok=True)
        os.makedirs(vector_dir, exist_ok=True)
        
        repo_name = "test-repo"
        
        # Mock document loading and embedding generation
        with patch('mcp.semantic._load_documents_from_zim') as mock_load:
            mock_docs = [
                Document(repo=repo_name, path="README.md", content="# Test"),
                Document(repo=repo_name, path="docs/guide.md", content="# Guide")
            ]
            mock_load.return_value = mock_docs
            
            with patch('mcp.semantic.generate_embeddings') as mock_gen_emb:
                mock_gen_emb.return_value = [
                    np.array([0.1, 0.2]),
                    np.array([0.3, 0.4])
                ]
                
                with patch('mcp.semantic._save_embeddings') as mock_save:
                    result = index_repo(repo_name, zim_dir, vector_dir)
                    
                    assert result is True
                    mock_load.assert_called_once()
                    mock_gen_emb.assert_called_once()
                    mock_save.assert_called_once()
    
    def test_index_repo_no_documents(self, temp_dir):
        """Test indexing repository with no documents."""
        from mcp.semantic import index_repo
        
        zim_dir = os.path.join(temp_dir, "zim")
        vector_dir = os.path.join(temp_dir, "vectors")
        os.makedirs(zim_dir, exist_ok=True)
        os.makedirs(vector_dir, exist_ok=True)
        
        repo_name = "empty-repo"
        
        with patch('mcp.semantic._load_documents_from_zim') as mock_load:
            mock_load.return_value = []
            
            result = index_repo(repo_name, zim_dir, vector_dir)
            
            assert result is True  # Should succeed even with no docs
            mock_load.assert_called_once()
    
    def test_index_repo_large_repository(self, temp_dir):
        """Test indexing a large repository."""
        from mcp.semantic import index_repo
        
        zim_dir = os.path.join(temp_dir, "zim")
        vector_dir = os.path.join(temp_dir, "vectors")
        os.makedirs(zim_dir, exist_ok=True)
        os.makedirs(vector_dir, exist_ok=True)
        
        repo_name = "large-repo"
        
        # Create 1000 mock documents
        mock_docs = []
        for i in range(1000):
            mock_docs.append(
                Document(
                    repo=repo_name,
                    path=f"docs/file_{i}.md",
                    content=f"# Document {i}\nThis is content for document {i}."
                )
            )
        
        with patch('mcp.semantic._load_documents_from_zim') as mock_load:
            mock_load.return_value = mock_docs
            
            with patch('mcp.semantic.generate_embeddings') as mock_gen_emb:
                # Return embeddings for all documents
                mock_gen_emb.return_value = [
                    np.array([0.1, 0.2, 0.3]) for _ in range(1000)
                ]
                
                with patch('mcp.semantic._save_embeddings') as mock_save:
                    result = index_repo(repo_name, zim_dir, vector_dir)
                    
                    assert result is True
                    assert mock_gen_emb.call_count == 1
                    assert mock_save.call_count == 1
    
    def test_index_repo_with_error(self, temp_dir):
        """Test repository indexing with errors."""
        from mcp.semantic import index_repo
        
        zim_dir = os.path.join(temp_dir, "zim")
        vector_dir = os.path.join(temp_dir, "vectors")
        os.makedirs(zim_dir, exist_ok=True)
        os.makedirs(vector_dir, exist_ok=True)
        
        repo_name = "error-repo"
        
        with patch('mcp.semantic._load_documents_from_zim') as mock_load:
            mock_load.side_effect = Exception("Failed to load documents")
            
            result = index_repo(repo_name, zim_dir, vector_dir)
            
            assert result is False
    
    def test_index_repo_missing_directories(self, temp_dir):
        """Test indexing with missing directories."""
        from mcp.semantic import index_repo
        
        zim_dir = os.path.join(temp_dir, "zim")
        vector_dir = os.path.join(temp_dir, "vectors")
        # Don't create directories
        
        repo_name = "test-repo"
        
        result = index_repo(repo_name, zim_dir, vector_dir)
        
        assert result is False


class TestEmbeddingOperations:
    """Test embedding-related operations."""
    
    def test_embedding_similarity(self):
        """Test calculating similarity between embeddings."""
        from mcp.semantic import calculate_similarity
        
        emb1 = np.array([0.1, 0.2, 0.3])
        emb2 = np.array([0.1, 0.2, 0.3])  # Same embedding
        emb3 = np.array([0.9, 0.8, 0.7])  # Different embedding
        
        similarity_same = calculate_similarity(emb1, emb2)
        similarity_different = calculate_similarity(emb1, emb3)
        
        assert similarity_same == 1.0  # Perfect similarity
        assert 0 <= similarity_different <= 1.0
        assert similarity_same > similarity_different
    
    def test_search_similar_documents(self):
        """Test searching for similar documents."""
        from mcp.semantic import search_similar_documents
        
        query_embedding = np.array([0.1, 0.2, 0.3])
        document_embeddings = [
            np.array([0.1, 0.2, 0.3]),  # Very similar
            np.array([0.5, 0.6, 0.7]),  # Somewhat similar
            np.array([0.9, 0.8, 0.9])   # Not very similar
        ]
        
        with patch('mcp.semantic._load_embeddings_from_repo') as mock_load:
            mock_load.return_value = document_embeddings
            
            results = search_similar_documents(
                query="test query",
                repo_name="test-repo",
                vector_dir="vectors",
                top_k=2
            )
            
            assert len(results) == 2
            assert results[0]['score'] >= results[1]['score']


class TestEmbeddingPersistence:
    """Test embedding storage and retrieval."""
    
    def test_save_and_load_embeddings(self, temp_dir):
        """Test saving and loading embeddings."""
        from mcp.semantic import _save_embeddings, _load_embeddings_from_repo
        
        vector_dir = os.path.join(temp_dir, "vectors")
        os.makedirs(vector_dir, exist_ok=True)
        
        repo_name = "test-repo"
        embeddings = [
            np.array([0.1, 0.2, 0.3]),
            np.array([0.4, 0.5, 0.6])
        ]
        
        # Save embeddings
        _save_embeddings(repo_name, embeddings, vector_dir)
        
        # Load embeddings
        loaded_embeddings = _load_embeddings_from_repo(repo_name, vector_dir)
        
        assert len(loaded_embeddings) == 2
        assert np.array_equal(loaded_embeddings[0], embeddings[0])
        assert np.array_equal(loaded_embeddings[1], embeddings[1])
    
    def test_load_nonexistent_embeddings(self, temp_dir):
        """Test loading embeddings from non-existent repository."""
        from mcp.semantic import _load_embeddings_from_repo
        
        vector_dir = os.path.join(temp_dir, "vectors")
        os.makedirs(vector_dir, exist_ok=True)
        
        result = _load_embeddings_from_repo("nonexistent-repo", vector_dir)
        
        assert result == []


class TestSemanticSearchAPI:
    """Test semantic search API endpoints."""
    
    def test_semantic_search_endpoint(self):
        """Test semantic search API endpoint."""
        client = TestClient(app)
        with patch('mcp.semantic.search_similar_documents') as mock_search:
            mock_search.return_value = [
                {
                    'document': Document(repo="test", path="README.md", content="# Test"),
                    'score': 0.95
                }
            ]
            
            response = client.post("/search/semantic", json={
                "query": "python programming",
                "repo": "test-repo",
                "top_k": 5
            })
            
            assert response.status_code == 200
            data = response.json()
            assert len(data['results']) == 1
            assert data['results'][0]['score'] == 0.95
    
    def test_semantic_search_no_results(self):
        """Test semantic search with no results."""
        client = TestClient(app)
        with patch('mcp.semantic.search_similar_documents') as mock_search:
            mock_search.return_value = []
            
            response = client.post("/search/semantic", json={
                "query": "nonexistent topic",
                "repo": "test-repo"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data['results'] == []
    
    def test_semantic_search_invalid_request(self):
        """Test semantic search with invalid request."""
        client = TestClient(app)
        response = client.post("/search/semantic", json={
            "invalid_field": "test"
        })
        
        assert response.status_code == 422  # Validation error