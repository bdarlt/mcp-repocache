import logging
import re
import sqlite3
from typing import List

from .models import Document, VersionType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_db(db_path: str):
    """
    Initialize the SQLite database with proper schema constraints and indexes.

    Schema includes:
    - NOT NULL constraints for critical fields
    - Default values for version fields
    - Indexes for performance optimization
    - Comprehensive documentation

    Version constraints:
    - version: Must be either a VersionType enum value or a semantic version string
    - version_category: Must be a VersionType enum value
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create main docs table with NOT NULL constraints
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            path TEXT NOT NULL,
            content TEXT NOT NULL,
            version TEXT NOT NULL DEFAULT 'latest',
            version_category TEXT NOT NULL DEFAULT 'latest',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create indexes for performance optimization
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_docs_repo ON docs(repo)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_docs_version ON docs(version)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_docs_version_category ON docs(version_category)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_docs_repo_version ON docs(repo, version)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_docs_path ON docs(path)
    """)

    # Create a composite index for common query patterns
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_docs_full_search ON docs(repo, version, path)
    """)

    conn.commit()
    conn.close()


def index_docs(docs: List[Document], zim_dir: str, db_path: str):
    """
    Store documents in Zim and SQLite with version validation and timestamp management.

    Args:
        docs: List of Document objects to store
        zim_dir: Directory for Zim storage (future implementation)
        db_path: Path to SQLite database

    Version validation:
        - Ensures version is either a VersionType enum value or semantic version
        - Falls back to 'latest' for invalid versions
        - Maintains version_category for grouping
    """
    setup_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for doc in docs:
        # Validate and normalize version
        version = validate_version(doc.version)

        # Determine version category for grouping
        version_category = determine_version_category(version)

        cursor.execute(
            """
            INSERT INTO docs (repo, path, content, version, version_category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (doc.repo, doc.path, doc.content, version, version_category),
        )

    conn.commit()
    conn.close()


def validate_version(version: str | None) -> str:
    """
    Validate version string and ensure it's either a VersionType enum value or semantic version.

    Args:
        version: Version string to validate

    Returns:
        Validated version string, defaults to 'latest' if invalid

    Version constraints:
        - Must be a VersionType enum value (e.g., 'latest', 'main', 'error')
        - Or a semantic version string (e.g., '1.0.0', 'v2.1.3')
        - Or a git tag/ref (e.g., 'release-1.0')
    """
    if not version:
        return VersionType.LATEST.value

    # Check if it's a VersionType enum value
    if version in [vt.value for vt in VersionType]:
        return version

    # Check if it's a semantic version (basic pattern matching)
    # Semantic version pattern: vX.Y.Z or X.Y.Z where X,Y,Z are numbers
    import re

    # Be strict: exactly 3 version numbers, optional pre-release suffix
    semantic_pattern = r"^(v?\d+\.\d+\.\d+)(?:-[a-zA-Z0-9._-]+)?$"

    # Additional check: must have exactly 3 version components (not 2, not 4)
    version_parts = version.lstrip("v").split(".")
    if len(version_parts) != 3:
        # Wrong number of version components
        logger.warning(
            f"Invalid version format: '{version}'. Expected exactly 3 version components. Using default: '{VersionType.LATEST.value}'"
        )
        return VersionType.LATEST.value

    if re.match(semantic_pattern, version):
        return version

    # Check if it's a reasonable git tag/ref (but not a semantic version)
    # Git tag pattern: alphanumeric with common separators, but not X.Y or X.Y.Z format
    # Exclude versions that look like semantic versions but are incomplete
    # Git tag/branch pattern: alphanumeric with common separators including forward slashes
    git_tag_pattern = r"^[a-zA-Z0-9][a-zA-Z0-9._/-]*$"

    # Exclude X.Y format (incomplete semantic version)
    incomplete_semver_pattern = r"^\d+\.\d+$"
    if re.match(incomplete_semver_pattern, version):
        # This looks like an incomplete semantic version, treat as invalid
        logger.warning(
            f"Invalid version format: '{version}'. Looks like incomplete semantic version. Using default: '{VersionType.LATEST.value}'"
        )
        return VersionType.LATEST.value

    if re.match(git_tag_pattern, version):
        return version

    # If version doesn't match any pattern, log warning and use default
    logger.warning(
        f"Invalid version format: '{version}'. Using default: '{VersionType.LATEST.value}'"
    )
    return VersionType.LATEST.value


def determine_version_category(version: str) -> str:
    """
    Determine version category based on version string.

    Args:
        version: Version string to categorize

    Returns:
        Version category (VersionType enum value)

    Categorization logic:
        - If version is a VersionType enum value, use it directly
        - If version is a semantic version/tag, use 'latest' as category
        - This allows grouping by version type for queries
    """
    if version in [vt.value for vt in VersionType]:
        return version
    else:
        # For specific versions/tags, use 'latest' as the category
        return VersionType.LATEST.value
