# Data Flow and File Structure

---

## Shared Directories
All modules communicate via shared directories mounted at `/data`:

| Directory       | Purpose                              | Example Content                     |
|-----------------|--------------------------------------|-------------------------------------|
| `/data/raw/`    | Raw docs from Git repos              | `/data/raw/repo1/README.md`         |
| `/data/zim/`    | Processed docs in Zim format         | `/data/zim/repo1.zim`               |
| `/data/sqlite/` | SQLite database for metadata         | `/data/sqlite/docs.db`              |
| `/data/vectors/`| FAISS index for semantic search      | `/data/vectors/repo1.faiss`         |

---

## Example Workflow
1. **Git Fetcher** clones `https://github.com/owner/repo1` and writes files to `/data/raw/repo1/`
2. **Storage/Indexing** reads `/data/raw/repo1/`, stores docs in `/data/zim/repo1.zim` and `/data/sqlite/docs.db`
3. **Semantic Indexer** reads `/data/zim/repo1.zim`, generates embeddings, and writes to `/data/vectors/repo1.faiss`
4. **MCP Server** reads from SQLite and FAISS to serve API responses

---

## File Naming Conventions
- Raw docs: `<repo_name>/<path_in_repo>.md`
- Zim files: `<repo_name>.zim`
- FAISS indices: `<repo_name>.faiss`

