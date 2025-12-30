"""
Semantic indexing and search functionality for MCP Repository Cache.
"""
import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from mcp.models import Document


def generate_embeddings(texts: list) -> List[np.ndarray]:
    """Generate embeddings for a list of texts."""
    if not texts:
        return []
    
    # Placeholder implementation - in real implementation, 
    # this would use a proper embedding model like BERT, Sentence-BERT, etc.
    # For now, return random embeddings for testing
    embeddings = []
    for text in texts:
        # Create a random embedding vector (768 dimensions like BERT)
        embedding = np.random.randn(768).astype(np.float32)
        embeddings.append(embedding)
    
    return embeddings


def _create_embeddings(texts: List[str]) -> np.ndarray:
    """Internal function to create embeddings array."""
    embeddings = generate_embeddings(texts)
    return np.array(embeddings)


def index_repo(repo_name: str, zim_dir: str, vector_dir: str) -> bool:
    """Generate and store embeddings for a repository."""
    try:
        # Create directories if they don't exist
        os.makedirs(vector_dir, exist_ok=True)
        
        # Load documents from zim directory
        docs = _load_documents_from_zim(repo_name, zim_dir)
        if not docs:
            return True  # Success even with no documents
        
        # Generate embeddings
        texts = [doc.content for doc in docs]
        embeddings = generate_embeddings(texts)
        
        # Save embeddings
        _save_embeddings(repo_name, embeddings, vector_dir)
        
        return True
    except Exception as e:
        print(f"Error indexing repository {repo_name}: {e}")
        return False


def _load_documents_from_zim(repo_name: str, zim_dir: str) -> List[Document]:
    """Load documents from zim directory for a repository."""
    # Placeholder implementation
    # In real implementation, this would read from zim files
    return []


def _save_embeddings(repo_name: str, embeddings: List[np.ndarray], vector_dir: str):
    """Save embeddings to disk."""
    embedding_file = os.path.join(vector_dir, f"{repo_name}.pkl")
    with open(embedding_file, 'wb') as f:
        pickle.dump(embeddings, f)


def _load_embeddings_from_repo(repo_name: str, vector_dir: str) -> List[np.ndarray]:
    """Load embeddings for a repository."""
    embedding_file = os.path.join(vector_dir, f"{repo_name}.pkl")
    if not os.path.exists(embedding_file):
        return []
    
    with open(embedding_file, 'rb') as f:
        return pickle.load(f)


def calculate_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Calculate cosine similarity between two embeddings."""
    # Normalize embeddings
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
    return float(similarity)


def search_similar_documents(query: str, repo_name: str, vector_dir: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar documents in a repository."""
    # Generate query embedding
    query_embedding = generate_embeddings([query])[0]
    
    # Load document embeddings
    doc_embeddings = _load_embeddings_from_repo(repo_name, vector_dir)
    
    if not doc_embeddings:
        return []
    
    # Calculate similarities
    similarities = []
    for i, doc_embedding in enumerate(doc_embeddings):
        similarity = calculate_similarity(query_embedding, doc_embedding)
        similarities.append({
            'index': i,
            'score': similarity
        })
    
    # Sort by similarity and return top k
    similarities.sort(key=lambda x: x['score'], reverse=True)
    return similarities[:top_k]

