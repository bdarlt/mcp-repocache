# MCP Server: Overview

## Purpose
The MCP Server is a **documentation aggregation and indexing system** that:
- Fetches documentation from multiple Git repositories (GitHub, Azure Repos).
- Stores and indexes documentation in **Zim** (for local wiki-style storage) and **SQLite** (for metadata and full-text search).
- Provides **semantic search** capabilities using OpenAI/Anthropic embeddings.
- Serves documentation via a **REST API** (FastAPI).

## Key Features
- **Modular design**: Separates Git fetching, storage, indexing, and API serving.
- **File-based communication**: Uses shared directories for inter-module communication.
- **Prototype-friendly**: Easy to extend, test, and deploy.

## Current Status
- **Git Fetcher**: Implemented (clones repos, extracts Markdown files).
- **Storage/Indexing**: Partially implemented (SQLite storage, Zim placeholder).
- **Semantic Indexer**: Not yet implemented.
- **MCP Server**: Basic API implemented (serves docs from SQLite).

## Technologies
- **Language**: Python 3.9+
- **Dependencies**: FastAPI, Uvicorn, GitPython, OpenAI, FAISS, Zim
- **Data Storage**: Zim, SQLite, FAISS (for vectors)
- **Deployment**: Docker (planned)

