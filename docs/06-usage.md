# Usage

---

## Fetching Documentation
To fetch docs from a Git repository:
```bash
poetry run python scripts/fetch_docs.py
```
- Replace the `repo_url` in `scripts/fetch_docs.py` with your repository

---

## Indexing Documentation
To index fetched docs:
```bash
poetry run python scripts/index_docs.py
```

---

## Running the API Server
To start the FastAPI server:
```bash
poetry run python scripts/run_server.py
```
- The API will be available at [http://localhost:8000](http://localhost:8000)

---

## API Endpoints

### List Documents
```
GET /docs?repo=<repo_name>
```
- Returns a list of all documents (optionally filtered by repo)

### Search Documents (Planned)
```
GET /search?q=<query>
```
- Returns semantic and traditional search results

