from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class VersionType(str, Enum):

    """Enum for standardized version types"""
    LATEST = "latest"  # Default version when no specific version is available
    MAIN_BRANCH = "main"  # Main branch without tags
    LOCAL = "local"  # Local repository
    ERROR = "error"  # Error determining version
    DETACHED_HEAD = "detached"  # Detached HEAD state
    SHALLOW_CLONE = "shallow"  # Shallow clone
    NO_REMOTE = "no-remote"  # No remote tracking
    INITIAL_COMMIT = "initial"  # Only initial commit
    MULTIPLE_REMOTES = "multi-remote"  # Multiple remotes
    SUBMODULE = "submodule"  # Git submodule
    EMPTY_REPO = "empty"  # Empty repository
    CORRUPTED = "corrupted"  # Corrupted git history


class Document(BaseModel):
    repo: str
    path: str
    content: str
    version: Optional[str] = VersionType.LATEST.value


class Repository(BaseModel):
    url: str
    name: Optional[str] = None
    branch: Optional[str] = "main"
    version_strategy: Optional[str] = None  # Optional version strategy override
