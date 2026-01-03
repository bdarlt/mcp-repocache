import logging
import os
from typing import List

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo

from .models import Document, Repository, VersionType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def determine_version(repo_path: str, repo_url: str) -> str:
    """
    Determine the version of a git repository based on various edge cases.

    Args:
        repo_path: Path to the local repository
        repo_url: Original repository URL

    Returns:
        Version string based on VersionType enum
    """
    try:
        repo = Repo(repo_path)

        # Check if repository is empty
        if not repo.heads and not repo.tags:
            return VersionType.EMPTY_REPO.value

        # Check for detached HEAD
        if repo.head.is_detached:
            return VersionType.DETACHED_HEAD.value

        # Check if it's a shallow clone
        if repo.is_shallow():
            return VersionType.SHALLOW_CLONE.value

        # Check for no remote tracking
        if not repo.remotes:
            return VersionType.NO_REMOTE.value

        # Check for initial commit only
        if len(list(repo.iter_commits())) <= 1:
            return VersionType.INITIAL_COMMIT.value

        # Check for multiple remotes
        if len(repo.remotes) > 1:
            return VersionType.MULTIPLE_REMOTES.value

        # Check if it's a local path (not a URL)
        if not repo_url.startswith(("http://", "https://", "git@")):
            return VersionType.LOCAL.value

        # Try to get the latest tag
        try:
            latest_tag = repo.tags[-1] if repo.tags else None
            if latest_tag:
                return str(latest_tag)
        except (IndexError, GitCommandError):
            pass

        # Fall back to branch name or main branch
        current_branch = repo.active_branch.name if repo.active_branch else "main"
        if current_branch == "main" and not repo.tags:
            return VersionType.MAIN_BRANCH.value

        return current_branch

    except (InvalidGitRepositoryError, NoSuchPathError):
        return VersionType.ERROR.value
    except Exception as e:
        logger.warning(f"Error determining version for {repo_path}: {e}")
        return VersionType.ERROR.value


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

                    # Determine version for this document
                    version = determine_version(repo_path, repo.url)

                    docs.append(
                        Document(
                            repo=repo_name,
                            path=rel_path,
                            content=content,
                            version=version,
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
