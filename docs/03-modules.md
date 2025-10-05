# Modules: Detailed Overview

---

## 1. Git Fetcher (`mcp/git_fetcher.py`)

### Purpose
Fetches documentation from Git repositories (GitHub, Azure Repos) and prepares it for indexing.

### Responsibilities
- Clone Git repositories using `GitPython`
- Extract Markdown (`.md`) files from the repository
- Write raw documentation files to `/data/raw/<repo_name>/`

### Dependencies
- [GitPython](https://gitpython.readthedocs.io/)

### Key Functions
```python
def fetch_repo(repo_url: str, raw_dir: str) -> List[Document]:
    """
    Clone a Git repository and extract all Markdown files.

    Args:
        repo_url: URL of the Git repository
        raw_dir: Directory to store raw documents

    Returns:
        List of `Document` objects
    """
    # Implementation details...
```

### Usage Example
```python
from mcp.git_fetcher import fetch_repo

# Fetch documents from a repository
docs = fetch_repo("https://github.com/owner/repo", "/data/raw")
print(f"Fetched {len(docs)} documents.")
```

### Notes
- Assumes repositories contain Markdown files
- Error handling for failed clones is minimal in the prototype

---

## 2. Storage/Indexing (`mcp/storage.py`)

### Purpose
Stores and indexes documentation in **Zim** and **SQLite**.

### Responsibilities
- Read raw documents from `/data/raw/<repo_name>/`
- Store documents in **Zim** (wiki format) and **SQLite** (metadata + full-text search)
- Write processed documents to `/data/zim/<repo_name>.zim` and `/data/sqlite/docs.db`

### Dependencies
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [zim-py](https://pypi.org/project/zim-py/)

### Key Functions
```python
def setup_db(db_path: str):
    """Initialize the SQLite database."""

def index_docs(docs: List[Document], zim_dir: str, db_path: str):
    """
    Store documents in Zim and SQLite.

    Args:
        docs: List of `Document` objects
        zim_dir: Directory to store Zim files
        db_path: Path to SQLite database
    """
    # Implementation details...
```

### Usage Example
```python
from mcp.storage import index_docs
from mcp.git_fetcher import fetch_repo

# Fetch and index documents
docs = fetch_repo("https://github.com/owner/repo", "/data/raw")
index_docs(docs, "/data/zim", "/data/sqlite/docs.db")
print(f"Indexed {len(docs)} documents.")
```

### Notes
- Zim storage logic is a **placeholder** and needs implementation
- SQLite is used for full-text search and metadata

---

## 3. Semantic Indexer (`mcp/semantic.py`)

### Purpose (Planned)
Generates semantic embeddings for documents using OpenAI/Anthropic.

### Responsibilities
- Read processed documents from `/data/zim/<repo_name>.zim`
- Generate embeddings using OpenAI or Anthropic
- Store embeddings in **FAISS** at `/data/vectors/<repo_name>.faiss`

### Dependencies (Planned)
- [openai](https://pypi.org/project/openai/)
- [faiss-cpu](https://pypi.org/project/faiss-cpu/)

### Key Functions (Planned)
```python
def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI.

    Args:
        texts: List of document texts

    Returns:
        List of embeddings (vectors)
    """
    # Implementation details...

def index_repo(repo_name: str, zim_dir: str, vector_dir: str):
    """
    Generate and store embeddings for a repository.

    Args:
        repo_name: Name of the repository
        zim_dir: Directory containing Zim files
        vector_dir: Directory to store FAISS indices
    """
    # Implementation details...
```

### Usage Example (Planned)
```python
from mcp.semantic import index_repo

# Generate embeddings for a repository
index_repo("repo1", "/data/zim", "/data/vectors")
print("Generated semantic embeddings for repo1.")
```

### Notes
- This module is **not yet implemented**
- Will support swapping between OpenAI and Anthropic models

---

## 4. MCP Server (`mcp/server.py`)

### Purpose
Serves documentation via a **REST API**.

### Responsibilities
- Provide endpoints for listing and searching documents
- Query **SQLite** for traditional search
- Query **FAISS** for semantic search (planned)

### Dependencies
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)

### Key Endpoints
#### List Documents
```python
@app.get("/docs", response_model=List[Document])
def get_docs(repo: str = None):
    """
    List all documents, optionally filtered by repository.

    Args:
        repo: Repository name (optional)

    Returns:
        List of documents
    """
    # Implementation details...
```

#### Search Documents (Planned)
```python
@app.get("/search")
def search(q: str):
    """
    Search documents using semantic and traditional methods.

    Args:
        q: Search query

    Returns:
        Combined search results
    """
    # Implementation details...
```

### Usage Example
```bash
# Run the FastAPI server
poetry run python scripts/run_server.py
```

### API Examples
#### List Documents
```
GET /docs?repo=repo1
```
**Response:**
```json
[
  {
    "repo": "repo1",
    "path": "README.md",
    "content": "# Repository 1\n...",
    "version": "latest"
  }
]
```

#### Search Documents (Planned)
```
GET /search?q=example
```
**Response:**
```json
{
  "traditional": [
    {
      "repo": "repo1",
      "path": "README.md",
      "content": "# Repository 1\n...",
      "score": 0.95
    }
  ],
  "semantic": [
    {
      "repo": "repo1",
      "path": "README.md",
      "content": "# Repository 1\n...",
      "score": 0.98
    }
  ]
}
```

### Notes
- Semantic search is **not yet implemented**
- Currently only supports listing documents from SQLite

---

## Module Interaction

### Data Flow
1. **Git Fetcher** → Writes raw docs to `/data/raw/<repo_name>/`
2. **Storage/Indexing** → Reads from `/data/raw/`, writes to `/data/zim/` and `/data/sqlite/docs.db`
3. **Semantic Indexer** → Reads from `/data/zim/`, writes to `/data/vectors/<repo_name>.faiss`
4. **MCP Server** → Reads from `/data/sqlite/docs.db` and `/data/vectors/`, serves API responses

### Shared Dependencies
- All modules use the `Document` model from `mcp/models.py`
- Modules are designed to run independently for flexibility

