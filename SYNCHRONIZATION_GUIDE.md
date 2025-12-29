# Synchronization Guide

## 🎯 Quick Sync

```bash
# Configure repositories in config.yaml
poetry run python scripts/index_docs.py
```

## 📁 What Happens

1. **Clone repos** → `data/raw/`
2. **Extract `.md` files** → SQLite database
3. **Store in** → `data/sqlite/docs.db`

## ✅ Verify

```bash
# Check database
sqlite3 data/sqlite/docs.db "SELECT COUNT(*) FROM docs;

# View cloned repos
ls data/raw/
```

## 🚨 Issues

- **Git errors**: Check repository URLs
- **No documents**: Ensure `.md` files exist in repos
- **Permission denied**: Check `data/` directory permissions

**Next**: Start server with `poetry run python scripts/run_server.py`