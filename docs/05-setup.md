# Setup and Installation

---

## Prerequisites
- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Docker (optional, for containerized deployment)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/bdarlt/mcp-repocache.git
cd mcp-repocache
```

### 2. Install Dependencies
```bash
poetry install
```

### 3. Create Data Directories
```bash
mkdir -p data/raw data/zim data/sqlite data/vectors
```

---

## Configuration
Edit the `pyproject.toml` file to add or remove dependencies as needed.

---

## Running the Project

### Fetch and Index Documents
```bash
poetry run python scripts/fetch_docs.py
poetry run python scripts/index_docs.py
```

### Run the Server
```bash
poetry run python scripts/run_server.py
```

The API will be available at [http://localhost:8000](http://localhost:8000).

---

## Docker Deployment (Planned)

### Build the Docker Image
```bash
docker build -t mcp-repocache .
```

### Run the Container
```bash
docker run -p 8000:8000 -v \$(pwd)/data:/data mcp-repocache
```

---

## Notes
- Ensure the `data/` directory is writable by the Docker container when using Docker.
- Replace repository URLs and paths in the scripts as needed for your environment.

