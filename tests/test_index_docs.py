"""
Tests for the main index_docs script.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from mcp.models import Document


class TestLoadConfig:
    """Test configuration loading functionality."""

    def test_load_config_valid(self, temp_dir):
        """Test loading a valid configuration file."""
        config_content = """
repositories:
  - url: "https://github.com/test/repo.git"
    name: "test-repo"
    branch: "main"

paths:
  raw_dir: "data/raw"
  zim_dir: "data/zim"
  sqlite_path: "data/sqlite/docs.db"
  vector_dir: "data/vectors"
"""

        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)

        # Change to temp directory to load config
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            # Import and test the load_config function
            from scripts.index_docs import load_config

            config = load_config()

            assert "repositories" in config
            assert "paths" in config
            assert len(config["repositories"]) == 1
            assert (
                config["repositories"][0]["url"] == "https://github.com/test/repo.git"
            )
        finally:
            os.chdir(original_cwd)

    def test_load_config_missing_file(self, temp_dir):
        """Test loading configuration from missing file."""
        from scripts.index_docs import load_config

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            # Ensure no config file exists
            config_file = Path(temp_dir) / "config.yaml"
            if config_file.exists():
                config_file.unlink()

            with pytest.raises(FileNotFoundError):
                load_config()
        finally:
            os.chdir(original_cwd)

    def test_load_config_invalid_yaml(self, temp_dir):
        """Test loading invalid YAML configuration."""
        config_content = """
invalid: yaml: content: [
  missing: brackets
"""

        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            from scripts.index_docs import load_config

            with pytest.raises(yaml.YAMLError):
                load_config()
        finally:
            os.chdir(original_cwd)


class TestMainFunction:
    """Test the main function of index_docs script."""

    @pytest.fixture
    def sample_config(self):
        """Provide a sample configuration."""
        return {
            "repositories": [
                {
                    "url": "https://github.com/test/repo1.git",
                    "name": "repo1",
                    "branch": "main",
                }
            ],
            "paths": {
                "raw_dir": "data/raw",
                "zim_dir": "data/zim",
                "sqlite_path": "data/sqlite/docs.db",
                "vector_dir": "data/vectors",
            },
        }

    def test_main_successful_indexing(self, temp_dir, sample_config):
        """Test successful document indexing."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Mock the load_config function
            with patch("scripts.index_docs.load_config") as mock_load_config:
                mock_load_config.return_value = sample_config

                # Mock fetch_repo to return sample documents
                with patch("scripts.index_docs.fetch_repo") as mock_fetch_repo:
                    sample_docs = [
                        Document(
                            repo="repo1",
                            path="README.md",
                            content="# Test Repo\nThis is a test.",
                        )
                    ]
                    mock_fetch_repo.return_value = sample_docs

                    # Mock index_docs function
                    with patch("scripts.index_docs.index_docs") as mock_index_docs:
                        # Run main function
                        from scripts.index_docs import main

                        main()

                        # Verify functions were called
                        mock_load_config.assert_called_once()
                        mock_fetch_repo.assert_called_once()
                        mock_index_docs.assert_called_once_with(
                            sample_docs, "data/zim", "data/sqlite/docs.db"
                        )
        finally:
            os.chdir(original_cwd)

    def test_main_with_multiple_repositories(self, temp_dir):
        """Test indexing multiple repositories."""
        config = {
            "repositories": [
                {
                    "url": "https://github.com/test/repo1.git",
                    "name": "repo1",
                    "branch": "main",
                },
                {
                    "url": "https://github.com/test/repo2.git",
                    "name": "repo2",
                    "branch": "develop",
                },
            ],
            "paths": {
                "raw_dir": "data/raw",
                "zim_dir": "data/zim",
                "sqlite_path": "data/sqlite/docs.db",
                "vector_dir": "data/vectors",
            },
        }

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            with patch("scripts.index_docs.load_config") as mock_load_config:
                mock_load_config.return_value = config

                # Mock fetch_repo to return different documents for each repo
                def mock_fetch_side_effect(repo, raw_dir):
                    if repo.name == "repo1":
                        return [
                            Document(repo="repo1", path="README.md", content="# Repo1")
                        ]
                    elif repo.name == "repo2":
                        return [
                            Document(repo="repo2", path="README.md", content="# Repo2")
                        ]
                    return []

                with patch(
                    "scripts.index_docs.fetch_repo", side_effect=mock_fetch_side_effect
                ) as mock_fetch_repo:
                    with patch("scripts.index_docs.index_docs") as mock_index_docs:
                        from scripts.index_docs import main

                        main()

                        # Verify both repositories were processed
                        assert mock_load_config.call_count == 1
                        assert mock_fetch_repo.call_count == 2
                        assert mock_index_docs.call_count == 2
        finally:
            os.chdir(original_cwd)

    def test_main_with_fetch_error(self, temp_dir, sample_config):
        """Test handling of fetch_repo errors."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            with patch("scripts.index_docs.load_config") as mock_load_config:
                mock_load_config.return_value = sample_config

                # Mock fetch_repo to raise an exception
                with patch("scripts.index_docs.fetch_repo") as mock_fetch_repo:
                    from git import GitCommandError

                    mock_fetch_repo.side_effect = GitCommandError(
                        "clone", "fatal: repository not found"
                    )

                    # Mock index_docs (should not be called)
                    with patch("scripts.index_docs.index_docs") as mock_index_docs:
                        # Mock print to capture error messages
                        with patch("builtins.print") as mock_print:
                            from scripts.index_docs import main

                            main()

                            # Verify error was printed
                            mock_print.assert_called()
                            call_args = mock_print.call_args[0][0]
                            assert "Failed to index" in call_args
                            assert "https://github.com/test/repo1.git" in call_args

                            # Verify index_docs was not called due to error
                            mock_index_docs.assert_not_called()
        finally:
            os.chdir(original_cwd)

    def test_main_empty_repositories(self, temp_dir):
        """Test with empty repositories list."""
        config = {
            "repositories": [],
            "paths": {
                "raw_dir": "data/raw",
                "zim_dir": "data/zim",
                "sqlite_path": "data/sqlite/docs.db",
                "vector_dir": "data/vectors",
            },
        }

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            with patch("scripts.index_docs.load_config") as mock_load_config:
                mock_load_config.return_value = config

                with patch("scripts.index_docs.fetch_repo") as mock_fetch_repo:
                    with patch("scripts.index_docs.index_docs") as mock_index_docs:
                        from scripts.index_docs import main

                        main()

                        # Verify no repositories were processed
                        mock_fetch_repo.assert_not_called()
                        mock_index_docs.assert_not_called()
        finally:
            os.chdir(original_cwd)

    def test_main_directory_creation(self, temp_dir, sample_config):
        """Test that necessary directories are created."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            with patch("scripts.index_docs.load_config") as mock_load_config:
                mock_load_config.return_value = sample_config

                # Mock successful repo fetching
                with patch("scripts.index_docs.fetch_repo") as mock_fetch_repo:
                    mock_fetch_repo.return_value = [
                        Document(repo="repo1", path="README.md", content="# Test")
                    ]

                    # Mock index_docs
                    with patch("scripts.index_docs.index_docs"):
                        from scripts.index_docs import main

                        main()

                        # Verify directories were created
                        assert os.path.exists("data/zim")
                        assert os.path.exists("data/sqlite")
        finally:
            os.chdir(original_cwd)


class TestIntegration:
    """Integration tests for the index_docs script."""

    def test_full_indexing_workflow(self, temp_dir):
        """Test the complete indexing workflow."""
        # Create a real config file
        config_content = """
repositories:
  - url: "https://github.com/test/repo.git"
    name: "test-repo"
    branch: "main"

paths:
  raw_dir: "data/raw"
  zim_dir: "data/zim"
  sqlite_path: "data/sqlite/docs.db"
  vector_dir: "data/vectors"
"""

        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Mock the entire workflow
            with patch("scripts.index_docs.fetch_repo") as mock_fetch_repo:
                sample_docs = [
                    Document(
                        repo="test-repo",
                        path="README.md",
                        content="# Test\nThis is a test repository.",
                    ),
                    Document(
                        repo="test-repo",
                        path="docs/guide.md",
                        content="# Guide\nThis is a user guide.",
                    ),
                ]
                mock_fetch_repo.return_value = sample_docs

                # Mock index_docs but let the real storage functions run
                with patch("scripts.index_docs.index_docs") as mock_index_docs:
                    from scripts.index_docs import main

                    main()

                    # Verify the workflow completed
                    assert mock_fetch_repo.call_count == 1
                    assert mock_index_docs.call_count == 1

                    # Verify the correct data was passed to index_docs
                    call_args = mock_index_docs.call_args
                    docs_arg = call_args[0][0]  # First positional argument
                    zim_dir_arg = call_args[0][1]  # Second positional argument
                    sqlite_path_arg = call_args[0][2]  # Third positional argument

                    assert len(docs_arg) == 2
                    assert all(isinstance(doc, Document) for doc in docs_arg)
                    assert zim_dir_arg == "data/zim"
                    assert sqlite_path_arg == "data/sqlite/docs.db"
        finally:
            os.chdir(original_cwd)
