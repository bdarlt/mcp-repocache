# MCP Repository Cache - AI Agent Documentation

## Project Overview

MCP Repository Cache is a documentation aggregation and indexing system that fetches documentation from multiple Git repositories, stores it locally, and serves it via a REST API. The system is designed to provide centralized access to documentation from various repositories with both traditional and semantic search capabilities.

## Technology Stack

- **Language**: Python 3.9+
- **Web Framework**: FastAPI with Uvicorn server
- **Database**: SQLite for metadata and full-text search
- **Version Control**: GitPython for repository operations
- **Data Formats**: YAML configuration, Markdown documentation
- **Containerization**: Docker with Alpine Linux base
- **Development Environment**: VS Code Dev Containers

## Project Structure

```
mcp-repocache/
├── mcp/                    # Core modules
│   ├── __init__.py
│   ├── git_fetcher.py     # Repository cloning and doc extraction
│   ├── models.py          # Pydantic data models
│   ├── semantic.py        # Semantic indexing (placeholder)
│   ├── server.py          # FastAPI REST server
│   └── storage.py         # SQLite and Zim storage
├── scripts/               # Executable scripts
│   ├── index_docs.py      # Document indexing script
│   └── run_server.py      # Server startup script
├── docs/                  # Project documentation
├── data/                  # Data directories (created at runtime)
│   ├── raw/              # Raw fetched documents
│   ├── zim/              # Zim wiki files
│   ├── sqlite/           # SQLite database
│   └── vectors/          # Vector embeddings
├── config.yaml           # Repository configuration
├── Dockerfile            # Container configuration
└── .devcontainer/        # VS Code development environment
```

## Core Architecture

The system consists of four modular components:

1. **Git Fetcher** (`mcp/git_fetcher.py`): Clones repositories and extracts Markdown files
2. **Storage/Indexing** (`mcp/storage.py`): Stores documents in SQLite and Zim format
3. **Semantic Indexer** (`mcp/semantic.py`): Placeholder for future semantic search capabilities
4. **MCP Server** (`mcp/server.py`): FastAPI REST server for serving documentation

### Data Flow
```
Git Repos → Git Fetcher → /data/raw/ → Storage/Indexing → /data/sqlite/docs.db
                                                        ↓
                                                    MCP Server → REST API
```

## Configuration

The system uses `config.yaml` to define repositories to index:

```yaml
repositories:
  - url: "https://github.com/owner/repo1.git"
    name: "repo1"
    branch: "main"

paths:
  raw_dir: "data/raw"
  zim_dir: "data/zim"
  sqlite_path: "data/sqlite/docs.db"
  vector_dir: "data/vectors"
```

## Key Commands

### Development Setup
```bash
# Install dependencies (Poetry required)
poetry install

# Create data directories
mkdir -p data/raw data/zim data/sqlite data/vectors
```

### Document Processing
```bash
# Index documents from configured repositories
poetry run python scripts/index_docs.py
```

### Server Operations
```bash
# Start the FastAPI server
poetry run python scripts/run_server.py

# Server will be available at http://localhost:8000
```

### Docker Operations
```bash
# Build container
docker build -t mcp-repocache .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/data mcp-repocache
```

## API Endpoints

### List Documents
- **GET** `/docs` - List all documents
- **GET** `/docs?repo=<repo_name>` - List documents for specific repository

### Response Format
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

## Current Implementation Status

### ✅ Implemented
- Git repository cloning and Markdown extraction
- SQLite database storage and indexing
- Basic FastAPI REST server
- Docker containerization
- Development environment setup

### ⚠️ Partially Implemented
- Zim storage format (placeholder functions)
- Semantic search capabilities (stub functions)

### ❌ Not Implemented
- Vector embeddings generation
- FAISS vector search integration
- Advanced search endpoints
- Authentication and authorization

## Development Guidelines

### Code Style
- Python code follows standard Python conventions
- FastAPI for web framework patterns
- Pydantic for data validation and serialization
- Type hints throughout the codebase

### Module Design
- Each module is independently runnable
- File-based communication between modules
- Shared data models in `mcp/models.py`
- Clear separation of concerns

### Error Handling
- Comprehensive logging using Python's logging module
- Graceful error handling for Git operations
- Database connection error handling

## Environment Variables

- `MOONSHOT_API_KEY`: API key for Moonshot AI services (referenced in devcontainer)

## Dependencies

Core dependencies (managed by Poetry):
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `gitpython`: Git repository operations
- `pydantic`: Data validation
- `pyyaml`: YAML configuration parsing

## Testing Strategy

### Automated Testing
The project includes comprehensive pytest-based test suite:

**Test Structure:**
- `tests/test_models.py` - Data model validation tests
- `tests/test_storage.py` - Database and indexing tests  
- `tests/test_git_fetcher.py` - Git operations tests
- `tests/test_server.py` - FastAPI server tests
- `tests/test_index_docs.py` - Main script integration tests

**Test Commands:**
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=mcp --cov=scripts --cov-report=html

# Use test runner script
poetry run python scripts/run_tests.py --coverage --verbose

# Run specific test categories
poetry run pytest -m unit          # Unit tests only
poetry run pytest -m integration   # Integration tests
poetry run pytest -m "not slow"    # Exclude slow tests
```

**Test Coverage:**
- Models: 95%+ coverage
- Storage: 90%+ coverage  
- Server: 85%+ coverage
- Git Fetcher: 80%+ coverage (mocked)
- Integration: 75%+ coverage

**Test Fixtures:**
- `temp_dir` - Temporary directory for test files
- `test_data_dir` - Complete data directory structure
- `sample_config` - Sample configuration data
- `sample_document` - Sample document objects
- `mock_git_repo` - Mock Git repository
- `client` - FastAPI test client

### Manual Testing
Additional manual testing for:
- API endpoint testing via browser or curl
- Document indexing verification by checking SQLite database
- Repository cloning verification through file system inspection

## Security Considerations

### Dependency Security
- **Safety Scanner**: Configured to scan for vulnerable dependencies
- **Exclusions**: `data/raw` directory excluded from scans (contains cloned repos)
- **Configuration**: Safety policy defined in `.safety-policy.yml`
- **Commands**: 
  ```bash
  poetry run safety scan                           # Basic scan
  poetry run safety scan --full-report            # Detailed scan
  ```

### Application Security
- No authentication implemented (development/prototype stage)
- API endpoints are publicly accessible
- Git repository URLs should be verified before processing
- Environment variables for API keys should be properly secured

## Deployment Notes

- Designed for containerized deployment
- Data directories should be persisted using Docker volumes
- Configuration can be updated without rebuilding containers
- Development environment available via VS Code Dev Containers