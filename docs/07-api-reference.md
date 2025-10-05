# API Reference

---

## Endpoints

### `GET /docs`
List all documents.

**Query Parameters:**
- `repo` (optional): Filter by repository name.

**Response:**
```json
[
  {
    "repo": "repo1",
    "path": "README.md",
    "content": "# Repository 1\n...",
    "version": "latest"
  }
]
```

---

### `GET /search` (Planned)
Search documents using semantic and traditional methods.

**Query Parameters:**
- `q`: Search query.

**Response:**
```json
{
  "traditional": [
    {
      "repo": "repo1",
      "path": "README.md",
      "content": "# Repository 1\n...",
      "score": 0.95
    }
  ],
  "semantic": [
    {
      "repo": "repo1",
      "path": "README.md",
      "content": "# Repository 1\n...",
      "score": 0.98
    }
  ]
}
```

