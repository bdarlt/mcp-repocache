# MCP Quick Start

## 🎯 3-Step Setup

### 1️⃣ Configure Repositories
Edit `config.yaml`:

```yaml
repositories:
  - url: "https://github.com/username/repo.git"
    name: "repo-name"
    branch: "main"
```

### 2️⃣ Index Documents
```bash
poetry run python scripts/index_docs.py
```

### 3️⃣ Start Server
```bash
poetry run python scripts/run_server.py
```

## ✅ Verify

```bash
# Check indexed documents
sqlite3 data/sqlite/docs.db "SELECT COUNT(*) FROM docs;

# View cloned repos
ls data/raw/
```

## 📊 Expected Output

```
Successfully indexed 45 documents from https://github.com/username/repo.git
Server running at http://localhost:8000
```

## 🚨 Troubleshooting

| Issue | Fix |
|-------|-----|
| `GitCommandError` | Check URL/network |
| `ModuleNotFoundError` | Run `poetry install` |
| No documents | Ensure `.md` files exist |

## 🔗 API Access

- **List all docs**: `GET /docs`
- **Filter by repo**: `GET /docs?repo=repo-name`
- **Get specific doc**: `GET /docs/<id>`

**Need more details?** See full documentation in `docs/`