import yaml
import os
from mcp.storage import index_docs
from mcp.git_fetcher import fetch_repo
from mcp.models import Repository

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    raw_dir = config["paths"]["raw_dir"]
    zim_dir = config["paths"]["zim_dir"]
    sqlite_path = config["paths"]["sqlite_path"]

    os.makedirs(zim_dir, exist_ok=True)
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    for repo_config in config["repositories"]:
        repo = Repository(**repo_config)
        try:
            docs = fetch_repo(repo, raw_dir)
            if docs:
                index_docs(docs, zim_dir, sqlite_path)
                print(f"Successfully indexed {len(docs)} documents from {repo.url}")
        except Exception as e:
            print(f"Failed to index {repo.url}: {e}")

if __name__ == "__main__":
    import yaml
    main()

