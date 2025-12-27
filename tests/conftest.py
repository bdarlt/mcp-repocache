"""
Pytest configuration and shared fixtures for MCP Repository Cache tests.
"""
import os
import tempfile
import shutil
import pytest
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def test_data_dir():
    """Create a test data directory structure."""
    temp_path = tempfile.mkdtemp()
    data_dirs = {
        'raw': Path(temp_path) / 'raw',
        'zim': Path(temp_path) / 'zim', 
        'sqlite': Path(temp_path) / 'sqlite',
        'vectors': Path(temp_path) / 'vectors'
    }
    
    for dir_path in data_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    yield temp_path, data_dirs
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """Provide a sample configuration for testing."""
    return {
        'repositories': [
            {
                'url': 'https://github.com/test/repo1.git',
                'name': 'repo1',
                'branch': 'main'
            }
        ],
        'paths': {
            'raw_dir': 'data/raw',
            'zim_dir': 'data/zim',
            'sqlite_path': 'data/sqlite/docs.db',
            'vector_dir': 'data/vectors'
        }
    }


@pytest.fixture
def sample_document():
    """Provide a sample document for testing."""
    return {
        'repo': 'test-repo',
        'path': 'README.md',
        'content': '# Test Repository\n\nThis is a test document.',
        'version': 'latest'
    }


@pytest.fixture
def mock_git_repo(temp_dir):
    """Create a mock git repository with sample files."""
    repo_path = Path(temp_dir) / 'test-repo'
    repo_path.mkdir(parents=True)
    
    # Create sample markdown files
    (repo_path / 'README.md').write_text('# Test Repository\n\nThis is a test.')
    (repo_path / 'docs').mkdir()
    (repo_path / 'docs' / 'guide.md').write_text('# Guide\n\nThis is a guide.')
    
    return str(repo_path)