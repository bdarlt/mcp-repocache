# Installation Guide

## 📦 Dependencies

```bash
# Install required packages
pip install fastapi uvicorn[standard] gitpython pydantic pyyaml

# Or use Poetry (recommended)
poetry install
```

## ✅ Verify

```bash
python -c "import fastapi, uvicorn, git, pydantic, yaml; print('✅ Ready!')"
```

## 🐛 Issues

- **GitPython errors**: Install Git first (`sudo apt-get install git`)
- **Permission errors**: Use virtual environment or `pip install --user`
- **Python 3.13**: Use `poetry run pytest -p no:cacheprovider` for tests

**Next**: Configure `config.yaml` and run `poetry run python scripts/index_docs.py`