# MCP Repository Cache - Quick Start Guide

## 🚀 Quick Synchronization

### 1. Configure Repositories
Edit `config.yaml` and add your Git repositories:

```yaml
repositories:
  - url: "https://github.com/username/repo.git"
    name: "repo-name"
    branch: "main"
```

### 2. Install Dependencies
```bash
poetry install
```

### 3. Run Synchronization
```bash
poetry run python scripts/index_docs.py
```

### 4. Verify Results
```bash
# Check database
sqlite3 data/sqlite/docs.db "SELECT COUNT(*) FROM docs;"

# Check cloned repos
ls data/raw/
```

## 📋 Common Commands

| Task | Command |
|------|---------|
| **Install dependencies** | `poetry install` |
| **Index documents** | `poetry run python scripts/index_docs.py` |
| **Start server** | `poetry run python scripts/run_server.py` |
| **Check database** | `sqlite3 data/sqlite/docs.db "SELECT * FROM docs LIMIT 5;"` |
| **View logs** | Check console output during indexing |

## 🔧 Configuration Template

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

## 🎯 What Gets Indexed

- ✅ All `.md` (Markdown) files
- ✅ Repository name and file paths
- ✅ Full document content
- ✅ UTF-8 encoded text

## 📊 Expected Output

```
Successfully indexed 45 documents from https://github.com/fastapi/fastapi.git
Successfully indexed 23 documents from https://github.com/pydantic/pydantic.git
```

## 🚨 Common Issues

| Error | Solution |
|-------|----------|
| `GitCommandError` | Check repository URL and network access |
| `ModuleNotFoundError` | Run `poetry install` |
| `Permission denied` | Check file permissions |
| No documents found | Ensure repositories contain `.md` files |

## 🔗 Next Steps

1. **Start the server**: `poetry run python scripts/run_server.py`
2. **Visit API**: http://localhost:8000/docs
3. **Query documents**: Use GET `/docs` endpoint

For detailed instructions, see `SYNCHRONIZATION_GUIDE.md`