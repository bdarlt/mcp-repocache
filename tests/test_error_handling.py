"""
Tests for MCP error handling edge cases.
"""
import os
import tempfile
import shutil
import sqlite3
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import pytest
from git import GitCommandError, InvalidGitRepositoryError
from mcp.models import Document, Repository


class TestNetworkErrorHandling:
    """Test network-related error handling."""
    
    def test_git_clone_network_timeout(self, temp_dir):
        """Test handling of network timeouts during Git clone."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = GitCommandError(
                "clone", 
                "fatal: unable to access 'https://github.com/test/repo.git/': Connection timed out"
            )
            
            with pytest.raises(GitCommandError, match="Connection timed out"):
                fetch_repo(repo, temp_dir)
    
    def test_git_clone_dns_resolution_failure(self, temp_dir):
        """Test handling of DNS resolution failures."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/nonexistent-domain-12345.com/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = GitCommandError(
                "clone",
                "fatal: unable to access 'https://github.com/nonexistent-domain-12345.com/repo.git/': Could not resolve host"
            )
            
            with pytest.raises(GitCommandError, match="Could not resolve host"):
                fetch_repo(repo, temp_dir)
    
    def test_git_clone_ssl_certificate_error(self, temp_dir):
        """Test handling of SSL certificate errors."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://self-signed-cert.com/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = GitCommandError(
                "clone",
                "fatal: unable to access 'https://self-signed-cert.com/repo.git/': SSL certificate problem: self signed certificate"
            )
            
            with pytest.raises(GitCommandError, match="SSL certificate problem"):
                fetch_repo(repo, temp_dir)
    
    def test_git_clone_rate_limiting(self, temp_dir):
        """Test handling of rate limiting during Git operations."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = GitCommandError(
                "clone",
                "fatal: unable to access 'https://github.com/test/repo.git/': Rate limit exceeded"
            )
            
            with pytest.raises(GitCommandError, match="Rate limit exceeded"):
                fetch_repo(repo, temp_dir)


class TestDiskSpaceErrorHandling:
    """Test disk space and file system error handling."""
    
    def test_insufficient_disk_space_during_clone(self, temp_dir):
        """Test handling of insufficient disk space during clone."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/large/repo.git",
            name="large-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_clone.side_effect = OSError(28, "No space left on device")
            
            with pytest.raises(OSError, match="No space left on device"):
                fetch_repo(repo, temp_dir)
    
    def test_database_disk_full_error(self, temp_dir):
        """Test handling of disk full errors during database operations."""
        from mcp.storage import index_docs
        
        db_path = os.path.join(temp_dir, "test.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        # Create a document
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test\n" * 1000  # Large content
        )
        
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Simulate disk full error on execute
            mock_cursor.execute.side_effect = sqlite3.OperationalError(
                "database or disk is full"
            )
            
            with pytest.raises(sqlite3.OperationalError, match="database or disk is full"):
                index_docs([doc], zim_dir, db_path)
    
    def test_read_only_file_system(self, temp_dir):
        """Test handling of read-only file system errors."""
        from mcp.storage import index_docs
        
        db_path = os.path.join(temp_dir, "readonly.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test content"
        )
        
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.OperationalError(
                "attempt to write a readonly database"
            )
            
            with pytest.raises(sqlite3.OperationalError, match="readonly database"):
                index_docs([doc], zim_dir, db_path)


class TestMemoryErrorHandling:
    """Test memory-related error handling."""
    
    def test_out_of_memory_during_large_file_read(self, temp_dir):
        """Test handling of out-of-memory errors during large file reads."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        # Mock successful clone
        with patch('mcp.git_fetcher.Repo.clone_from'):
            # Mock finding a very large file
            mock_files = [
                ("/tmp/test-repo", [], ["huge_file.md"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    # Simulate out of memory when reading file
                    mock_file = MagicMock()
                    mock_file.read.side_effect = MemoryError("Out of memory")
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # Should handle gracefully and continue
                    docs = fetch_repo(repo, temp_dir)
                    assert len(docs) == 0  # Should skip the problematic file
    
    def test_memory_error_during_embedding_generation(self, temp_dir):
        """Test handling of memory errors during embedding generation."""
        from mcp.semantic import generate_embeddings
        
        texts = ["Large text content"] * 1000  # Many large texts
        
        with patch('mcp.semantic._create_embeddings') as mock_create:
            mock_create.side_effect = MemoryError("CUDA out of memory")
            
            with pytest.raises(MemoryError, match="CUDA out of memory"):
                generate_embeddings(texts)


class TestConcurrentAccessErrorHandling:
    """Test concurrent access error handling."""
    
    def test_database_locked_error(self, temp_dir):
        """Test handling of database locked errors."""
        from mcp.storage import index_docs
        
        db_path = os.path.join(temp_dir, "locked.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test content"
        )
        
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Simulate database locked error
            mock_cursor.execute.side_effect = [
                sqlite3.OperationalError("database is locked"),
                sqlite3.OperationalError("database is locked"),
                sqlite3.OperationalError("database is locked"),
                None  # Finally succeeds
            ]
            
            # Should retry and eventually succeed
            index_docs([doc], zim_dir, db_path)
            
            # Should have been called 4 times (3 failures + 1 success)
            assert mock_cursor.execute.call_count == 4
    
    def test_concurrent_file_write_errors(self, temp_dir):
        """Test handling of concurrent file write errors."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from'):
            mock_files = [
                ("/tmp/test-repo", [], ["README.md"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    # Simulate file access error
                    mock_open.side_effect = PermissionError("File is being used by another process")
                    
                    docs = fetch_repo(repo, temp_dir)
                    assert len(docs) == 0  # Should handle gracefully


class TestCorruptedDataErrorHandling:
    """Test handling of corrupted data."""
    
    def test_corrupted_sqlite_database(self, temp_dir):
        """Test handling of corrupted SQLite database."""
        from mcp.storage import index_docs
        
        db_path = os.path.join(temp_dir, "corrupted.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        # Create a corrupted database file
        with open(db_path, 'wb') as f:
            f.write(b'This is not a valid SQLite database')
        
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test content"
        )
        
        with pytest.raises(sqlite3.DatabaseError):
            index_docs([doc], zim_dir, db_path)
    
    def test_corrupted_git_repository(self, temp_dir):
        """Test handling of corrupted Git repository."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from'):
            # Create corrupted .git directory
            repo_path = os.path.join(temp_dir, "test-repo")
            os.makedirs(os.path.join(repo_path, ".git"))
            
            with patch('mcp.git_fetcher.os.walk') as mock_walk:
                mock_walk.side_effect = OSError("Corrupted Git repository")
                
                docs = fetch_repo(repo, temp_dir)
                assert len(docs) == 0  # Should handle gracefully
    
    def test_malformed_yaml_configuration(self, temp_dir):
        """Test handling of malformed YAML configuration."""
        from scripts.index_docs import load_config
        
        malformed_yaml = """
repositories:
  - url: "https://github.com/test/repo.git"
    # Missing closing quote
    name: "test-repo

paths:
  raw_dir: "data/raw"
"""
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(malformed_yaml)
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            with pytest.raises(yaml.YAMLError):
                load_config()
        finally:
            os.chdir(original_cwd)


class TestTimeoutErrorHandling:
    """Test timeout-related error handling."""
    
    def test_git_operation_timeout(self, temp_dir):
        """Test handling of Git operation timeouts."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        def slow_clone(*args, **kwargs):
            time.sleep(2)  # Simulate slow operation
            raise GitCommandError("clone", "Operation timed out")
        
        with patch('mcp.git_fetcher.Repo.clone_from', side_effect=slow_clone):
            with pytest.raises(GitCommandError, match="Operation timed out"):
                fetch_repo(repo, temp_dir)
    
    def test_database_query_timeout(self, temp_dir):
        """Test handling of database query timeouts."""
        from mcp.storage import index_docs
        
        db_path = os.path.join(temp_dir, "timeout.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Test content"
        )
        
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Simulate query timeout
            mock_cursor.execute.side_effect = sqlite3.OperationalError(
                "query timeout exceeded"
            )
            
            with pytest.raises(sqlite3.OperationalError, match="query timeout exceeded"):
                index_docs([doc], zim_dir, db_path)


class TestUnicodeAndEncodingErrorHandling:
    """Test Unicode and encoding error handling."""
    
    def test_malformed_unicode_in_markdown(self, temp_dir):
        """Test handling of malformed Unicode in markdown files."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from'):
            mock_files = [
                ("/tmp/test-repo", [], ["README.md"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    # Simulate malformed Unicode
                    mock_file = MagicMock()
                    mock_file.read.side_effect = UnicodeDecodeError(
                        'utf-8',
                        b'invalid utf-8 sequence',
                        0,
                        1,
                        'invalid start byte'
                    )
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    docs = fetch_repo(repo, temp_dir)
                    assert len(docs) == 0  # Should skip malformed file
    
    def test_encoding_detection_fallback(self, temp_dir):
        """Test fallback encoding detection."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from'):
            mock_files = [
                ("/tmp/test-repo", [], ["README.md"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    # First try UTF-8 (fails), then fallback to latin-1
                    mock_file = MagicMock()
                    mock_file.read.side_effect = [
                        UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'invalid start byte'),
                        "Content read with fallback encoding"
                    ]
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    docs = fetch_repo(repo, temp_dir)
                    assert len(docs) == 1  # Should succeed with fallback


class TestRetryMechanismErrorHandling:
    """Test retry mechanisms for transient errors."""
    
    def test_exponential_backoff_for_network_errors(self, temp_dir):
        """Test exponential backoff for network-related errors."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            # Fail twice, then succeed
            mock_clone.side_effect = [
                GitCommandError("clone", "Network timeout"),
                GitCommandError("clone", "Network timeout"),
                Mock()  # Success
            ]
            
            with patch('time.sleep') as mock_sleep:  # Don't actually sleep in tests
                docs = fetch_repo(repo, temp_dir)
                
                # Should have been called 3 times
                assert mock_clone.call_count == 3
                # Should have slept with exponential backoff
                assert mock_sleep.call_count == 2
                # Verify exponential backoff timing
                mock_sleep.assert_has_calls([call(1), call(2)])
    
    def test_max_retry_limit_exceeded(self, temp_dir):
        """Test handling when maximum retry limit is exceeded."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            # Always fail
            mock_clone.side_effect = GitCommandError("clone", "Persistent network error")
            
            with patch('time.sleep'):  # Don't actually sleep
                with pytest.raises(GitCommandError, match="Maximum retry limit exceeded"):
                    fetch_repo(repo, temp_dir)
                
                # Should have tried 5 times (initial + 4 retries)
                assert mock_clone.call_count == 5


class TestGracefulDegradation:
    """Test graceful degradation when errors occur."""
    
    def test_partial_repository_processing(self, temp_dir):
        """Test processing continues when some repositories fail."""
        from scripts.index_docs import main
        
        config = {
            "repositories": [
                {"url": "https://github.com/test/repo1.git", "name": "repo1"},
                {"url": "https://github.com/test/repo2.git", "name": "repo2"},
                {"url": "https://github.com/test/repo3.git", "name": "repo3"}
            ],
            "paths": {
                "raw_dir": "data/raw",
                "zim_dir": "data/zim",
                "sqlite_path": "data/sqlite/docs.db",
                "vector_dir": "data/vectors"
            }
        }
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            with patch('scripts.index_docs.load_config') as mock_load_config:
                mock_load_config.return_value = config
                
                # Make repo2 fail
                def mock_fetch_side_effect(repo, raw_dir):
                    if repo.name == "repo2":
                        raise GitCommandError("clone", "Repository not found")
                    return [Document(repo=repo.name, path="README.md", content=f"# {repo.name}")]
                
                with patch('scripts.index_docs.fetch_repo', side_effect=mock_fetch_side_effect):
                    with patch('scripts.index_docs.index_docs') as mock_index:
                        with patch('builtins.print') as mock_print:
                            main()
                            
                            # Should have processed repo1 and repo3, but not repo2
                            assert mock_fetch.call_count == 3
                            assert mock_index.call_count == 2  # Only successful repos
                            
                            # Should have logged the error
                            error_messages = [call[0][0] for call in mock_print.call_args_list]
                            assert any("Failed to index" in msg for msg in error_messages)
        finally:
            os.chdir(original_cwd)
    
    def test_service_continues_with_database_errors(self, client):
        """Test that API service continues even with database errors."""
        from mcp.server import app
        
        with patch('sqlite3.connect') as mock_connect:
            # First call fails, second succeeds
            mock_connect.side_effect = [
                sqlite3.OperationalError("database is locked"),
                Mock()  # Success
            ]
            
            # First request should fail
            response1 = client.get("/docs")
            assert response1.status_code == 500
            
            # Second request should succeed
            response2 = client.get("/docs")
            assert response2.status_code == 200