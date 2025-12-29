# Quick Installation Guide

## 🎯 One-Line Setup

```bash
pip install fastapi uvicorn[standard] gitpython pydantic pyyaml
```

## 🐍 Using Poetry (Recommended)

```bash
# Install Poetry
pip install poetry

# Install dependencies
poetry install
```

## ✅ Verify Installation

```bash
python -c "import fastapi, uvicorn, git, pydantic, yaml; print('✅ All modules ready!')"
```

## 🚀 Next Steps

1. Configure repositories in `config.yaml`
2. Run indexing: `poetry run python scripts/index_docs.py`
3. Start server: `poetry run python scripts/run_server.py`

**That's it!** Now you can access the API at `http://localhost:8000/docs`