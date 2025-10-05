import os
import logging
from typing import List
from git import Repo, GitCommandError, InvalidGitRepositoryError
from .models import Document, Repository

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_repo(repo: Repository, raw_dir: str) -> List[Document]:
    """
    Clone a Git repository and extract all Markdown files.

    Args:
        repo: Repository object containing URL and other metadata
        raw_dir: Directory to store raw documents

    Returns:
        List of Document objects
    """
    repo_name = repo.name or repo.url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(raw_dir, repo_name)

    try:
        logger.info(f"Cloning repository: {repo.url}")
        Repo.clone_from(repo.url, repo_path, branch=repo.branch)

        docs = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    docs.append(
                        Document(
                            repo=repo_name,
                            path=rel_path,
                            content=content
                        )
                    )

        logger.info(f"Fetched {len(docs)} documents from {repo.url}")
        return docs

    except GitCommandError as e:
        logger.error(f"Failed to clone repository {repo.url}: {e}")
        raise
    except InvalidGitRepositoryError as e:
        logger.error(f"Invalid Git repository {repo.url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching {repo.url}: {e}")
        raise

