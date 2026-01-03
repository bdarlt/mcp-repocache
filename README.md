# MCP Repository Cache

**Centralized Documentation Indexing and Search System**

MCP Repository Cache fetches documentation from multiple Git repositories, stores
it locally, and provides both traditional and semantic search capabilities through
a REST API.

## 🏆 Project Status

<!-- Badges will be added here once CI/CD is fully configured -->
<!-- Example badge format: -->

[![Bandit](https://github.com/bdarlt/mcp-repocache/actions/workflows/bandit.yml/badge.svg)](https://github.com/d/bdarlt/mcp-repocache/actions/workflows/bandit.yml)
[![Pyre](https://github.com/bdarlt/mcp-repocache/actions/workflows/pyre.yml/badge.svg)](https://github.com/bdarlt/mcp-repocache/actions/workflows/pyre.yml)
<!-- [![Code Coverage](https://codecov.io/gh/your-org/mcp-repocache/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/mcp-repocache) -->
<!-- [![Code Quality](https://img.shields.io/lgtm/grade/python/g/your-org/mcp-repocache.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/your-org/mcp-repocache/context:python) -->

**TODO**: Add badges for:
- CI/CD pipeline status
- Test coverage (Codecov)
- Code quality (CodeQL, pylint)
- Docker image status
- License information

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

- ✅ **Multi-repository indexing**: Fetch and cache documentation from
multiple Git repos
- ✅ **Full-text search**: SQLite-based keyword search across all documents
- ✅ **REST API**: FastAPI server for programmatic access
- ✅ **Containerized**: Docker-ready with volume support for persistent storage
- ✅ **Semantic search ready**: Placeholder for future vector-based search

## 🔧 Installation

### Prerequisites

- Python 3.10+ (3.13 recommended)
- Poetry (for dependency management)
- Git
- Docker (for containerized deployment)

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

### GitHub Actions CI/CD

This project includes comprehensive GitHub Actions workflows for:

- **Continuous Integration**: Automated testing on push and pull requests
- **Continuous Delivery**: Docker image building and deployment
- **Security Scanning**: Regular vulnerability scans
- **Documentation**: Automated documentation building

See `.github/workflows/` for detailed workflow configurations.

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

```text
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

- **Status**: ✅ Completed
- **Tasks**:
  - ✅ Create `VersionType` enum with clear version semantics
  - ✅ Update Document model to use enum-based versions
  - ✅ Make database schema NOT NULL with default 'latest'
  - ✅ Add comprehensive tests for version handling
  - ✅ Update git fetcher for proper edge case handling
- **Benefits**: Robust version management, better error handling, type safety

#### Database Schema Improvements

- **Status**: ✅ Completed
- **Tasks**:
  - ✅ Make version field NOT NULL with proper default
  - ✅ Add version validation constraints with semantic version validation
  - ✅ Improve schema documentation with comprehensive docstrings
  - ✅ Add database indexes for performance optimization (6 indexes added)
  - ✅ Add timestamp fields for created_at and updated_at
  - ✅ Add comprehensive test coverage for new functionality
- **Benefits**: Data integrity, better query performance, enhanced version
management, robust error handling

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

This project is licensed under the BSD 3-Clause License - see the
[LICENSE](LICENSE) file for details.

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

### ✅ Completed Features

- [x] **Basic Git repository indexing** - Clone repos and extract Markdown files
- [x] **SQLite storage and search** - Full-text search with comprehensive indexing
- [x] **FastAPI REST server** - REST API for document access
- [x] **Enum-based version system** - Robust version management with VersionType enum
- [x] **Database schema improvements** - NOT NULL constraints, indexes, and validation
- [x] **Comprehensive testing** - Unit and integration tests for all components

### 🚧 Upcoming Features

- [ ] **Vector embeddings generation** - Semantic search preparation
- [ ] **FAISS semantic search** - Vector-based search capabilities
- [ ] **Advanced search endpoints** - Filtering, sorting, and pagination
- [ ] **Authentication and authorization** - API key and OAuth support
- [ ] **Performance optimization** - Caching and query optimization
- [ ] **Monitoring and metrics** - Prometheus integration and health checks
- [ ] **CI/CD pipeline enhancement** - Push Docker images to GitHub Container Registry
- [ ] **GitHub Actions optimization** - Evaluate workflow structure (monolithic vs. modular)
- [ ] **README badges** - Add CI/CD status, coverage, and quality badges
- [ ] **MCP via stdio** - Alternative stdio-based interface instead of REST API

### 🎯 Future Enhancements

- **Multi-tenancy support** - Isolated workspaces for different teams
- **Webhook integration** - Automatic re-indexing on repository updates
- **Advanced analytics** - Usage statistics and search patterns
- **Export/Import functionality** - Data migration and backup capabilities
- **MCP via stdio** - Alternative stdio-based interface for direct integration

### 🔧 Architectural Considerations

#### REST API vs. Stdio Interface

**Current Approach**: REST API with FastAPI

- ✅ **Pros**: Web-standard, language-agnostic, easy to integrate
- ❌ **Cons**: Network overhead, requires HTTP server

**Alternative Approach**: Stdio-based interface

- ✅ **Pros**: Direct integration, no network overhead, better for scripting
- ❌ **Cons**: Language-specific, harder to integrate with web services

**Use Cases for Stdio**:

- CLI tool integration
- Scripting and automation
- Direct process communication
- Embedded system usage

**Implementation Considerations**:

- Protocol design (JSON, protobuf, custom format)
- Error handling and exit codes
- Input/output streaming
- Compatibility with existing API

---

**Built with ❤️ using FastAPI, SQLite, and GitPython**