import os
import tempfile
from pathlib import Path

import pytest
from git import Repo

from mcp.git_fetcher import determine_version
from mcp.models import Document, VersionType


class TestVersionHandling:
    """Test version handling for various edge cases"""

    def test_version_enum_values(self):
        """Test that VersionType enum has all expected values"""
        expected_values = {
            "latest",
            "main",
            "local",
            "error",
            "detached",
            "shallow",
            "no-remote",
            "initial",
            "multi-remote",
            "submodule",
            "empty",
            "corrupted",
        }
        actual_values = {vt.value for vt in VersionType}
        assert actual_values == expected_values

    def test_empty_repository_version(self):
        """Test version detection for empty repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = os.path.join(tmpdir, "empty_repo")
            os.makedirs(repo_path)

            # Initialize empty git repo
            repo = Repo.init(repo_path)

            version = determine_version(repo_path, "https://github.com/test/empty.git")
            assert version == VersionType.EMPTY_REPO.value

    def test_detached_head_version(self):
        """Test version detection for detached HEAD"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = os.path.join(tmpdir, "detached_repo")

            # Create a repo with a commit and checkout detached HEAD
            repo = Repo.init(repo_path)

            # Create initial commit
            test_file = os.path.join(repo_path, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            repo.index.add([test_file])
            repo.index.commit("Initial commit")

            # Get the commit hash and checkout detached
            commit_hash = repo.head.commit.hexsha
            repo.head.reset(commit_hash, working_tree=True)

            version = determine_version(
                repo_path, "https://github.com/test/detached.git"
            )
            assert version == VersionType.DETACHED_HEAD.value

    def test_local_repository_version(self):
        """Test version detection for local repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = os.path.join(tmpdir, "local_repo")

            # Create a local repo
            repo = Repo.init(repo_path)

            # Create initial commit
            test_file = os.path.join(repo_path, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            repo.index.add([test_file])
            repo.index.commit("Initial commit")

            # Test with local path (not URL)
            version = determine_version(repo_path, "/local/path/to/repo")
            assert version == VersionType.LOCAL.value

    def test_main_branch_no_tags_version_category(self):
        """Test version category detection for main branch without tags"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = os.path.join(tmpdir, "main_branch_repo")

            # Create a repo on main branch
            repo = Repo.init(repo_path)

            # Create initial commit
            test_file = os.path.join(repo_path, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            repo.index.add([test_file])
            repo.index.commit("Initial commit")

            version = determine_version(repo_path, "https://github.com/test/main.git")
            assert version == VersionType.MAIN_BRANCH.value

    def test_error_version_handling(self):
        """Test version detection for invalid repository"""
        version = determine_version(
            "/non/existent/path", "https://github.com/test/invalid.git"
        )
        assert version == VersionType.ERROR.value

    def test_document_version_defaults(self):
        """Test that Document model uses correct default version"""
        doc = Document(repo="test_repo", path="test.md", content="# Test")
        assert doc.version == VersionType.LATEST.value

    def test_document_version_explicit(self):
        """Test that Document model accepts explicit versions"""
        for version_type in VersionType:
            doc = Document(
                repo="test_repo",
                path="test.md",
                content="# Test",
                version=version_type.value,
            )
            assert doc.version == version_type.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
