# Architecture

## High-Level Overview
The MCP Server is divided into **four modular components**:

1. **Git Fetcher**: Clones Git repositories and extracts documentation.
2. **Storage/Indexing**: Stores docs in Zim and SQLite, and updates indices.
3. **Semantic Indexer**: Generates embeddings for semantic search.
4. **MCP Server**: Serves documentation via a REST API.

## Component Interaction
Git Repos -> [Git Fetcher] -> /data/raw/ -> [Storage/Indexing] -> /data/zim/, /data/sqlite/
|
V
[Semantic Indexer] -> /data/vectors/
|
V
[MCP Server] -> REST API


## Data Flow
1. **Git Fetcher** clones repos and writes raw docs to `/data/raw/<repo_name>/`.
2. **Storage/Indexing** reads raw docs, stores them in Zim and SQLite, and writes to `/data/zim/` and `/data/sqlite/docs.db`.
3. **Semantic Indexer** reads from `/data/zim/`, generates embeddings, and writes to `/data/vectors/`.
4. **MCP Server** reads from SQLite and FAISS, and serves results via API.

## File Structure
/data
├── raw/          # Raw docs from Git
├── zim/          # Zim wiki files
├── sqlite/       # SQLite DB
└── vectors/      # FAISS vector index

## Modularity
Each component is a **separate Python module** in the `mcp/` directory and can be run independently:
- `git_fetcher.py`: Fetches docs from Git.
- `storage.py`: Stores and indexes docs.
- `semantic.py`: Generates semantic embeddings.
- `server.py`: Serves the API.
