# MCP Repository Cache - Installation Guide

This guide covers all the Python dependencies needed to run the MCP Repository Cache system.

## 📦 Required Python Modules

Based on the codebase analysis, here are the required dependencies:

### Core Dependencies

| Module | Version | Purpose |
|--------|---------|---------|
| `fastapi` | ^0.104.0 | Web framework for REST API |
| `uvicorn` | ^0.24.0 | ASGI server to run FastAPI |
| `gitpython` | ^3.1.40 | Git operations (clone repositories) |
| `pydantic` | ^2.5.0 | Data validation and serialization |
| `pyyaml` | ^6.0.1 | YAML configuration file parsing |

### Built-in Python Modules (No installation needed)
- `sqlite3` - Database operations (included in Python standard library)
- `os` - Operating system interface (included in Python standard library)
- `typing` - Type hints (included in Python standard library)
- `logging` - Logging functionality (included in Python standard library)

## 🚀 Installation Methods

### Method 1: Using pip (Recommended for quick start)

```bash

# Install from requirements.txt (if you've created it)
pip install -r requirements.txt
```

### Method 2: Using Poetry (Recommended for development)

```bash
# Install Poetry (if not already installed)
pip install poetry

# Install dependencies using Poetry
poetry install

```

## 📋 Installation Verification

After installation, verify that all modules are properly installed:

```bash
# Check installed versions
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"
python -c "import git; print(f'GitPython: {git.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python -c "import yaml; print(f'PyYAML: {yaml.__version__}')"
```

You should see version numbers for each module without any import errors.


## ⚠️ Version Compatibility

### Python Version Requirements
- **Minimum**: Python 3.10+
- **Recommended**: Python 3.11 or 3.12
- **Tested**: Python 3.13

## 🐛 Common Installation Issues

### 1. GitPython Installation Issues

```bash
# If you get errors about git executable
# Make sure git is installed on your system

# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com/download/win
```

### 2. Uvicorn with Standard Extras

```bash
# If uvicorn[standard] fails, try:
pip install uvicorn
pip install websockets  # for WebSocket support
pip install httptools   # for HTTP parser
```

### 3. Permission Issues

```bash
# If you get permission errors, try:
pip install --user fastapi uvicorn gitpython pydantic pyyaml

# Or use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn gitpython pydantic pyyaml
```

## 📁 Files Created

After running the dependency installation, you'll have:

- ✅ `requirements.txt` - Pip requirements file
- ✅ `pyproject.toml` - Poetry configuration file  
- ✅ Installed Python modules in your environment

## 🎯 Next Steps

After installing dependencies:

1. **Configure repositories** in `config.yaml`
2. **Run synchronization**: `python scripts/index_docs.py`
3. **Start server**: `python scripts/run_server.py`
4. **Test API**: Visit `http://localhost:8000/docs`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## 🔍 Troubleshooting

If you encounter import errors after installation:

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check module location
python -c "import fastapi; print(fastapi.__file__)"

# Reinstall if necessary
pip uninstall fastapi uvicorn gitpython pydantic pyyaml
pip install fastapi uvicorn gitpython pydantic pyyaml
```

For more help, check the main documentation or create an issue in the repository.
