# MCP Repository Cache - Synchronization Guide

This guide explains how to synchronize documentation from Git repositories and create local databases for the MCP Repository Cache system.

## Overview

The synchronization process consists of three main steps:
1. **Configure repositories** - Define which Git repositories to index
2. **Fetch documents** - Clone repositories and extract Markdown files
3. **Index documents** - Store documents in SQLite database and prepare for search

## Prerequisites

### 1. Install Dependencies

The project uses Poetry for dependency management. If you don't have Poetry installed:

```bash
# Install Poetry
pip install poetry

# Install project dependencies
poetry install
```

### 2. Verify Configuration File

Make sure your `config.yaml` file is properly configured with the repositories you want to index:

```yaml
repositories:
  - url: "https://github.com/username/repository.git"
    name: "my-repo"
    branch: "main"
  - url: "https://github.com/another/repo.git"
    name: "another-repo"
    branch: "develop"

paths:
  raw_dir: "data/raw"
  zim_dir: "data/zim"
  sqlite_path: "data/sqlite/docs.db"
  vector_dir: "data/vectors"
```

**Important**: Replace the placeholder URLs with actual Git repositories you want to index.

## Running the Synchronization

### Method 1: Using the Index Script (Recommended)

Run the main indexing script that handles the entire synchronization process:

```bash
# Using Poetry (recommended)
poetry run python scripts/index_docs.py

# Or using Python directly (if dependencies are installed)
python scripts/index_docs.py
```

This script will:
1. Read the configuration from `config.yaml`
2. Clone each repository to `data/raw/`
3. Extract all Markdown files (`.md` files)
4. Store documents in the SQLite database
5. Print progress and results

### Method 2: Step-by-Step Manual Process

If you want more control over the process, you can run each step manually:

#### Step 1: Create Data Directories

```bash
# Create necessary directories
mkdir -p data/raw data/zim data/sqlite data/vectors
```

#### Step 2: Configure Repositories

Edit `config.yaml` to add your repositories:

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

#### Step 3: Run the Indexing

```bash
poetry run python scripts/index_docs.py
```

## What Happens During Synchronization

### 1. Repository Cloning
- Each repository is cloned to `data/raw/{repo_name}/`
- Existing clones are overwritten (fresh clone each time)
- Specific branches are checked out as configured

### 2. Document Extraction
- All `.md` files are found recursively in the repository
- File paths are stored relative to the repository root
- Content is read as UTF-8 text

### 3. Database Storage
- SQLite database is created at `data/sqlite/docs.db`
- Documents table schema:
  ```sql
  CREATE TABLE docs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      repo TEXT NOT NULL,        -- Repository name
      path TEXT NOT NULL,        -- File path relative to repo root
      content TEXT NOT NULL,     -- Full markdown content
      version TEXT DEFAULT 'latest'
  );
  ```
- Each document is inserted as a separate row

## Example Output

When you run the synchronization, you should see output like:

```
Successfully indexed 45 documents from https://github.com/fastapi/fastapi.git
Successfully indexed 23 documents from https://github.com/pydantic/pydantic.git
Failed to index https://github.com/private/repo.git: GitCommandError
```

## Verifying the Results

### Check the Database

```bash
# Install sqlite3 if not available
# On Ubuntu/Debian: sudo apt-get install sqlite3
# On macOS: brew install sqlite3

# Query the database
sqlite3 data/sqlite/docs.db "SELECT COUNT(*) as total_docs, repo FROM docs GROUP BY repo;"
```

### Check Raw Files

```bash
# List cloned repositories
ls -la data/raw/

# Check specific repository contents
ls -la data/raw/fastapi/
```

## Troubleshooting

### Common Issues

#### 1. Repository Access Issues
```
Failed to clone repository https://github.com/owner/repo.git: GitCommandError
```
**Solution**: 
- Verify the repository URL is correct
- Check if the repository is public (private repos not supported in current version)
- Ensure you have internet connectivity

#### 2. Permission Errors
```
PermissionError: [Errno 13] Permission denied: 'data/raw'
```
**Solution**:
```bash
# Fix permissions
chmod 755 data/
# Or run with appropriate permissions
```

#### 3. Missing Dependencies
```
ModuleNotFoundError: No module named 'git'
```
**Solution**:
```bash
poetry install
# Or specifically: pip install GitPython
```

#### 4. Configuration Errors
```
KeyError: 'repositories'
```
**Solution**: Verify your `config.yaml` file has the correct structure.

### Debug Mode

For more detailed logging, you can modify the script to enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Usage

### Synchronizing Specific Repositories

To sync only specific repositories, temporarily modify your `config.yaml`:

```yaml
repositories:
  - url: "https://github.com/just/this-one.git"
    name: "this-one"
    branch: "main"
```

### Incremental Updates

The current implementation does a fresh clone each time. For incremental updates, you would need to modify the `git_fetcher.py` to:
1. Check if repository already exists
2. Pull latest changes instead of cloning
3. Handle file deletions and modifications

### Custom File Types

By default, only `.md` files are indexed. To include other file types, modify the condition in `git_fetcher.py`:

```python
# Change this line:
if file.endswith(".md"):

# To include more types:
if file.endswith((".md", ".rst", ".txt")):
```

## Next Steps

After successful synchronization:

1. **Start the server**: `poetry run python scripts/run_server.py`
2. **Test the API**: Visit `http://localhost:8000/docs`
3. **Query documents**: Use the REST API endpoints

For more information, see the main project documentation and API reference.