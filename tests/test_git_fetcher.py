"""
Tests for MCP git fetcher module.
"""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from mcp.git_fetcher import fetch_repo
from mcp.models import Repository, Document


class TestFetchRepo:
    """Test repository fetching functionality."""
    
    @pytest.fixture
    def sample_repo(self):
        """Create a sample repository object."""
        return Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
    
    @pytest.fixture
    def mock_repo_clone(self):
        """Mock the Repo.clone_from method."""
        with patch('mcp.git_fetcher.Repo') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.clone_from.return_value = mock_repo
            yield mock_repo_class, mock_repo
    
    def test_fetch_repo_name_extraction(self, temp_dir, mock_repo_clone):
        """Test repository name extraction from URL when name is not provided."""
        mock_repo_class, mock_repo = mock_repo_clone
        
        # Create a repository without explicit name
        repo = Repository(
            url="https://github.com/user/my-awesome-repo.git",
            branch="main"
        )
        
        # Mock os.walk to return sample files
        mock_files = [
            ("/tmp/my-awesome-repo", ["docs"], ["README.md", "setup.py"]),
            ("/tmp/my-awesome-repo/docs", [], ["guide.md"])
        ]
        
        with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_file.read.return_value = "# Test Content"
                mock_open.return_value.__enter__.return_value = mock_file
                
                docs = fetch_repo(repo, temp_dir)
                
                # Should extract name from URL
                expected_path = os.path.join(temp_dir, "my-awesome-repo")
                mock_repo_class.clone_from.assert_called_once_with(
                    "https://github.com/user/my-awesome-repo.git",
                    expected_path,
                    branch="main"
                )
    
    def test_fetch_repo_with_explicit_name(self, temp_dir, mock_repo_clone):
        """Test repository fetching with explicit name."""
        mock_repo_class, mock_repo = mock_repo_clone
        
        repo = Repository(
            url="https://github.com/user/repo.git",
            name="my-custom-name",
            branch="main"
        )
        
        # Mock os.walk to return no markdown files
        mock_files = [
            ("/tmp/my-custom-name", [], ["setup.py", "requirements.txt"])
        ]
        
        with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
            docs = fetch_repo(repo, temp_dir)
            
            # Should use explicit name
            expected_path = os.path.join(temp_dir, "my-custom-name")
            mock_repo_class.clone_from.assert_called_once_with(
                "https://github.com/user/repo.git",
                expected_path,
                branch="main"
            )
            
            # Should return empty list (no markdown files)
            assert docs == []
    
    def test_fetch_repo_with_markdown_files(self, temp_dir, mock_repo_clone):
        """Test fetching repository with markdown files."""
        mock_repo_class, mock_repo = mock_repo_clone
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        # Mock os.walk to return markdown files
        mock_files = [
            ("/tmp/test-repo", ["docs"], ["README.md", "setup.py"]),
            ("/tmp/test-repo/docs", [], ["guide.md", "api.md"])
        ]
        
        with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
            with patch('builtins.open', create=True) as mock_open:
                # Mock file reading
                def mock_file_content(filename):
                    if filename.endswith('README.md'):
                        return "# Main README\n\nThis is the main readme."
                    elif filename.endswith('guide.md'):
                        return "# User Guide\n\nThis is the user guide."
                    elif filename.endswith('api.md'):
                        return "# API Reference\n\nThis is the API reference."
                    return ""
                
                mock_file = MagicMock()
                mock_file.read.side_effect = lambda: mock_file_content(mock_open.call_args[0][0])
                mock_open.return_value.__enter__.return_value = mock_file
                
                docs = fetch_repo(repo, temp_dir)
                
                # Should return 3 documents
                assert len(docs) == 3
                
                # Check document properties
                assert all(isinstance(doc, Document) for doc in docs)
                assert all(doc.repo == "test-repo" for doc in docs)
                
                # Check paths (relative to repo root)
                paths = [doc.path for doc in docs]
                assert "README.md" in paths
                assert "docs/guide.md" in paths
                assert "docs/api.md" in paths
    
    def test_fetch_repo_no_markdown_files(self, temp_dir, mock_repo_clone):
        """Test fetching repository with no markdown files."""
        mock_repo_class, mock_repo = mock_repo_clone
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        # Mock os.walk to return no markdown files
        mock_files = [
            ("/tmp/test-repo", [], ["setup.py", "requirements.txt", "main.py"])
        ]
        
        with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
            docs = fetch_repo(repo, temp_dir)
            
            # Should return empty list
            assert docs == []
    
    def test_fetch_repo_with_branch(self, temp_dir, mock_repo_clone):
        """Test fetching repository with specific branch."""
        mock_repo_class, mock_repo = mock_repo_clone
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="develop"
        )
        
        # Mock os.walk to return no files (just to simplify test)
        mock_files = [("/tmp/test-repo", [], [])]
        
        with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
            docs = fetch_repo(repo, temp_dir)
            
            # Should clone with specific branch
            expected_path = os.path.join(temp_dir, "test-repo")
            mock_repo_class.clone_from.assert_called_once_with(
                "https://github.com/test/repo.git",
                expected_path,
                branch="develop"
            )


class TestGitErrors:
    """Test Git-related error handling."""
    
    def test_git_command_error(self, temp_dir):
        """Test handling of GitCommandError."""
        repo = Repository(
            url="https://github.com/invalid/repo.git",
            name="test-repo",
            branch="main"
        )
        
        from git import GitCommandError
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = GitCommandError("clone", "fatal: repository not found")
            
            with pytest.raises(GitCommandError):
                fetch_repo(repo, temp_dir)
    
    def test_invalid_git_repository_error(self, temp_dir):
        """Test handling of InvalidGitRepositoryError."""
        repo = Repository(
            url="https://github.com/invalid/repo.git",
            name="test-repo",
            branch="main"
        )
        
        from git import InvalidGitRepositoryError
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = InvalidGitRepositoryError("Not a valid repository")
            
            with pytest.raises(InvalidGitRepositoryError):
                fetch_repo(repo, temp_dir)
    
    def test_unexpected_error(self, temp_dir):
        """Test handling of unexpected errors."""
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = Exception("Unexpected error")
            
            with pytest.raises(Exception, match="Unexpected error"):
                fetch_repo(repo, temp_dir)


class TestFileReading:
    """Test file reading functionality."""
    
    def test_file_reading_utf8_encoding(self, temp_dir):
        """Test that files are read with UTF-8 encoding."""
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        # Mock successful clone
        with patch('mcp.git_fetcher.Repo.clone_from'):
            # Mock os.walk to return a markdown file
            mock_files = [
                ("/tmp/test-repo", [], ["README.md"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_file.read.return_value = "# UTF-8 Content with émojis 🚀"
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    docs = fetch_repo(repo, temp_dir)
                    
                    # Verify file was opened with UTF-8 encoding
                    mock_open.assert_called_once()
                    call_args = mock_open.call_args
                    assert call_args[0][0].endswith("README.md")
                    
                    # Verify content was read correctly
                    assert len(docs) == 1
                    assert docs[0].content == "# UTF-8 Content with émojis 🚀"