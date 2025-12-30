# MCP Repository Cache

**Centralized Documentation Indexing and Search System**

MCP Repository Cache fetches documentation from multiple Git repositories, stores
it locally, and provides both traditional and semantic search capabilities through
a REST API.

## 🚀 Quick Start

```bash
# Install dependencies
poetry install

# Index documents from configured repositories
poetry run python scripts/index_docs.py

# Start the FastAPI server
poetry run python scripts/run_server.py

# Access API at http://localhost:8000/docs
```

## 📦 Features

- ✅ **Multi-repository indexing**: Fetch and cache documentation from multiple Git repos
- ✅ **Full-text search**: SQLite-based keyword search across all documents
- ✅ **REST API**: FastAPI server for programmatic access
- ✅ **Containerized**: Docker-ready with volume support for persistent storage
- ✅ **Semantic search ready**: Placeholder for future vector-based search

## 🔧 Installation

### Prerequisites
- Python 3.10+ (3.13 recommended)
- Poetry (for dependency management)
- Git

### Setup
```bash
# Clone this repository
git clone https://github.com/your-org/mcp-repocache.git
cd mcp-repocache

# Install dependencies
poetry install

# Create data directories
mkdir -p data/raw data/zim data/sqlite data/vectors
```

## 📝 Configuration

Edit `config.yaml` to specify repositories:

```yaml
repositories:
  - url: "https://github.com/fastapi/fastapi.git"
    name: "fastapi"
    branch: "main"
  - url: "https://github.com/pydantic/pydantic.git"
    name: "pydantic"
    branch: "main"

paths:
  raw_dir: "data/raw"
  zim_dir: "data/zim"
  sqlite_path: "data/sqlite/docs.db"
  vector_dir: "data/vectors"
```

## 🎯 Usage

### Index Documents
```bash
poetry run python scripts/index_docs.py
```

### Start Server
```bash
poetry run python scripts/run_server.py
```

### API Endpoints
- **GET `/docs`** - List all documents
- **GET `/docs?repo=<name>`** - Filter by repository
- **GET `/docs/<id>`** - Get specific document

## 🐳 Docker Deployment

```bash
# Build container
docker build -t mcp-repocache .

# Run with volume mounting
docker run -p 8000:8000 -v $(pwd)/data:/data mcp-repocache
```

## 🔍 Search Capabilities

### Traditional Search
- SQLite full-text search
- Keyword-based filtering
- Repository-specific queries

### Future: Semantic Search
- Vector embeddings (placeholder)
- FAISS integration (planned)
- Context-aware results

## 📂 Project Structure

```
mcp-repocache/
├── mcp/                    # Core modules
│   ├── git_fetcher.py     # Repository operations
│   ├── models.py          # Data models
│   ├── server.py          # FastAPI server
│   └── storage.py         # Database & indexing
├── scripts/               # Executable scripts
├── data/                  # Runtime data (created automatically)
├── config.yaml            # Configuration
└── Dockerfile             # Container setup
```

## 🧪 Testing

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=mcp --cov-report=html

# Fix Python 3.13 Windows issues
poetry run pytest -p no:cacheprovider
```

## 🗺️ Roadmap

### 🚧 Upcoming Features

#### Enum-Based Version System (High Priority)
- **Status**: Planned for next implementation
- **Tasks**:
  - Create `VersionType` enum with clear version semantics
  - Update Document model to use enum-based versions
  - Make database schema NOT NULL with default 'latest'
  - Add comprehensive tests for version handling
  - Update git fetcher for proper edge case handling
- **Benefits**: Robust version management, better error handling, type safety

#### Database Schema Improvements
- **Status**: In progress
- **Tasks**:
  - Make version field NOT NULL with proper default
  - Add version validation constraints
  - Improve schema documentation
- **Benefits**: Data integrity, better query performance

### 🎯 Future Enhancements

- **Semantic Search**: Vector embeddings and FAISS integration
- **Authentication**: API key and OAuth support
- **Advanced Querying**: Full-text search improvements
- **Performance**: Caching and optimization

## 🔒 Security

- Dependency scanning with Safety 3.7
- No authentication (development stage)
- Secure API key handling for future features

## 📄 License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request
4. Follow existing code style and patterns

## 📞 Contact

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Support**: Open an issue with detailed information

## 🚀 Roadmap

- [x] Basic Git repository indexing
- [x] SQLite storage and search
- [x] FastAPI REST server
- [ ] Vector embeddings generation
- [ ] FAISS semantic search
- [ ] Advanced search endpoints
- [ ] Authentication and authorization

---

**Built with ❤️ using FastAPI, SQLite, and GitPython**