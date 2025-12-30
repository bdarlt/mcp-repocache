"""
Tests for MCP configuration management.
"""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import yaml
from mcp.models import Repository


class TestConfigurationLoading:
    """Test configuration file loading."""
    
    def test_load_valid_configuration(self, temp_dir):
        """Test loading a valid configuration file."""
        config_content = """
repositories:
  - url: "https://github.com/test/repo1.git"
    name: "repo1"
    branch: "main"
  - url: "https://github.com/test/repo2.git"
    name: "repo2"
    branch: "develop"

paths:
  raw_dir: "data/raw"
  zim_dir: "data/zim"
  sqlite_path: "data/sqlite/docs.db"
  vector_dir: "data/vectors"

settings:
  max_file_size: 1048576
  allowed_extensions: [".md", ".txt", ".rst"]
  timeout: 30
"""
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)
        
        from scripts.index_docs import load_config
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config = load_config()
            
            assert "repositories" in config
            assert "paths" in config
            assert "settings" in config
            assert len(config["repositories"]) == 2
            assert config["repositories"][0]["url"] == "https://github.com/test/repo1.git"
            assert config["paths"]["raw_dir"] == "data/raw"
            assert config["settings"]["max_file_size"] == 1048576
        finally:
            os.chdir(original_cwd)
    
    def test_load_minimal_configuration(self, temp_dir):
        """Test loading minimal configuration."""
        config_content = """
repositories:
  - url: "https://github.com/test/repo.git"

paths:
  raw_dir: "data/raw"
  sqlite_path: "data/sqlite/docs.db"
"""
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)
        
        from scripts.index_docs import load_config
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config = load_config()
            
            assert len(config["repositories"]) == 1
            assert config["repositories"][0]["url"] == "https://github.com/test/repo.git"
            assert config["paths"]["raw_dir"] == "data/raw"
        finally:
            os.chdir(original_cwd)
    
    def test_load_configuration_with_environment_variables(self, temp_dir):
        """Test loading configuration with environment variable substitution."""
        config_content = """
repositories:
  - url: "https://github.com/${GITHUB_ORG}/repo.git"

paths:
  raw_dir: "${DATA_DIR}/raw"
  sqlite_path: "${DATA_DIR}/sqlite/docs.db"
"""
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)
        
        from scripts.index_docs import load_config
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Set environment variables
            with patch.dict(os.environ, {
                'GITHUB_ORG': 'myorg',
                'DATA_DIR': '/app/data'
            }):
                config = load_config()
                
                assert config["repositories"][0]["url"] == "https://github.com/myorg/repo.git"
                assert config["paths"]["raw_dir"] == "/app/data/raw"
        finally:
            os.chdir(original_cwd)
    
    def test_load_configuration_missing_required_fields(self, temp_dir):
        """Test loading configuration with missing required fields."""
        config_content = """
# Missing repositories section
paths:
  raw_dir: "data/raw"
  sqlite_path: "data/sqlite/docs.db"
"""
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)
        
        from scripts.index_docs import load_config
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            with pytest.raises(ValueError, match="Missing required section"):
                load_config()
        finally:
            os.chdir(original_cwd)


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_validate_repository_urls(self):
        """Test validation of repository URLs."""
        from scripts.index_docs import validate_config
        
        valid_config = {
            "repositories": [
                {"url": "https://github.com/user/repo.git"},
                {"url": "https://gitlab.com/user/repo.git"},
                {"url": "https://bitbucket.org/user/repo.git"}
            ],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"}
        }
        
        # Should not raise any exceptions
        validate_config(valid_config)
        
        invalid_config = {
            "repositories": [
                {"url": "not-a-valid-url"},
                {"url": "http://invalid-protocol.com/repo.git"}
            ],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"}
        }
        
        with pytest.raises(ValueError, match="Invalid repository URL"):
            validate_config(invalid_config)
    
    def test_validate_path_permissions(self, temp_dir):
        """Test validation of path permissions."""
        from scripts.index_docs import validate_config
        
        # Create a read-only directory
        readonly_dir = Path(temp_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}],
            "paths": {
                "raw_dir": str(readonly_dir),
                "sqlite_path": "data/db.db"
            }
        }
        
        with pytest.raises(PermissionError, match="No write permission"):
            validate_config(config)
        
        # Reset permissions for cleanup
        readonly_dir.chmod(0o755)
    
    def test_validate_file_size_limits(self):
        """Test validation of file size limits."""
        from scripts.index_docs import validate_config
        
        # Valid size
        valid_config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"},
            "settings": {"max_file_size": 1048576}  # 1MB
        }
        
        validate_config(valid_config)
        
        # Invalid size (negative)
        invalid_config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"},
            "settings": {"max_file_size": -1}
        }
        
        with pytest.raises(ValueError, match="Invalid file size limit"):
            validate_config(invalid_config)
    
    def test_validate_allowed_extensions(self):
        """Test validation of allowed file extensions."""
        from scripts.index_docs import validate_config
        
        valid_config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"},
            "settings": {"allowed_extensions": [".md", ".txt", ".rst"]}
        }
        
        validate_config(valid_config)
        
        # Invalid extensions (no dots)
        invalid_config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"},
            "settings": {"allowed_extensions": ["md", "txt"]}
        }
        
        with pytest.raises(ValueError, match="Invalid file extension format"):
            validate_config(invalid_config)


class TestConfigurationMerging:
    """Test configuration merging and overrides."""
    
    def test_merge_configurations(self):
        """Test merging multiple configuration sources."""
        from scripts.index_docs import merge_configurations
        
        base_config = {
            "repositories": [{"url": "https://github.com/base/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"},
            "settings": {"timeout": 30}
        }
        
        override_config = {
            "repositories": [{"url": "https://github.com/override/repo.git"}],
            "settings": {"timeout": 60, "max_file_size": 2097152}
        }
        
        merged = merge_configurations(base_config, override_config)
        
        # Should have combined repositories
        assert len(merged["repositories"]) == 2
        # Should have overridden settings
        assert merged["settings"]["timeout"] == 60
        assert merged["settings"]["max_file_size"] == 2097152
        # Should preserve base paths
        assert merged["paths"]["raw_dir"] == "data/raw"
    
    def test_configuration_with_defaults(self):
        """Test applying default values to configuration."""
        from scripts.index_docs import apply_config_defaults
        
        minimal_config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}]
        }
        
        config_with_defaults = apply_config_defaults(minimal_config)
        
        # Should add default paths
        assert "paths" in config_with_defaults
        assert config_with_defaults["paths"]["raw_dir"] == "data/raw"
        assert config_with_defaults["paths"]["sqlite_path"] == "data/sqlite/docs.db"
        
        # Should add default settings
        assert "settings" in config_with_defaults
        assert config_with_defaults["settings"]["timeout"] == 30
        assert config_with_defaults["settings"]["max_file_size"] == 1048576


class TestConfigurationSecurity:
    """Test configuration security measures."""
    
    def test_prevent_directory_traversal(self):
        """Test preventing directory traversal in paths."""
        from scripts.index_docs import validate_config
        
        malicious_config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}],
            "paths": {
                "raw_dir": "../../../etc/passwd",
                "sqlite_path": "../../../var/lib/db.db"
            }
        }
        
        with pytest.raises(SecurityError, match="Directory traversal detected"):
            validate_config(malicious_config)
    
    def test_validate_repository_url_protocols(self):
        """Test validating allowed repository URL protocols."""
        from scripts.index_docs import validate_config
        
        # Only HTTPS should be allowed
        https_config = {
            "repositories": [{"url": "https://github.com/test/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"}
        }
        
        validate_config(https_config)
        
        # HTTP should be rejected
        http_config = {
            "repositories": [{"url": "http://github.com/test/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"}
        }
        
        with pytest.raises(SecurityError, match="Insecure protocol"):
            validate_config(http_config)
        
        # SSH should be rejected
        ssh_config = {
            "repositories": [{"url": "git@github.com:test/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"}
        }
        
        with pytest.raises(SecurityError, match="SSH protocol not allowed"):
            validate_config(ssh_config)
    
    def test_configuration_file_permissions(self, temp_dir):
        """Test configuration file permission checks."""
        from scripts.index_docs import load_config
        
        # Create config file with overly permissive permissions
        config_content = """
repositories:
  - url: "https://github.com/test/repo.git"

paths:
  raw_dir: "data/raw"
  sqlite_path: "data/sqlite/docs.db"
"""
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)
        config_file.chmod(0o777)  # World-writable
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            with pytest.warns(UserWarning, match="Configuration file has overly permissive permissions"):
                config = load_config()
                assert config is not None
        finally:
            os.chdir(original_cwd)


class TestConfigurationReloading:
    """Test configuration reloading and hot-swapping."""
    
    def test_configuration_file_watching(self, temp_dir):
        """Test watching configuration file for changes."""
        from scripts.index_docs import ConfigWatcher
        
        config_content = """
repositories:
  - url: "https://github.com/test/repo.git"

paths:
  raw_dir: "data/raw"
  sqlite_path: "data/sqlite/docs.db"
"""
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(config_content)
        
        callback_called = False
        
        def config_changed_callback(new_config):
            nonlocal callback_called
            callback_called = True
            assert len(new_config["repositories"]) == 2
        
        watcher = ConfigWatcher(config_file, config_changed_callback)
        
        # Modify the configuration file
        new_config_content = """
repositories:
  - url: "https://github.com/test/repo.git"
  - url: "https://github.com/test/repo2.git"

paths:
  raw_dir: "data/raw"
  sqlite_path: "data/sqlite/docs.db"
"""
        
        config_file.write_text(new_config_content)
        
        # Trigger the watcher (simulate file system event)
        watcher.check_for_changes()
        
        assert callback_called is True
        watcher.stop()
    
    def test_configuration_backup_and_rollback(self, temp_dir):
        """Test configuration backup and rollback functionality."""
        from scripts.index_docs import ConfigManager
        
        original_config = {
            "repositories": [{"url": "https://github.com/original/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"}
        }
        
        config_file = Path(temp_dir) / "config.yaml"
        config_file.write_text(yaml.dump(original_config))
        
        manager = ConfigManager(config_file)
        
        # Create backup
        manager.create_backup()
        
        # Modify configuration
        new_config = {
            "repositories": [{"url": "https://github.com/new/repo.git"}],
            "paths": {"raw_dir": "data/raw", "sqlite_path": "data/db.db"}
        }
        config_file.write_text(yaml.dump(new_config))
        
        # Rollback to backup
        manager.rollback()
        
        # Verify rollback
        restored_config = manager.load_config()
        assert restored_config["repositories"][0]["url"] == "https://github.com/original/repo.git"


class TestConfigurationTemplates:
    """Test configuration template generation."""
    
    def test_generate_basic_template(self):
        """Test generating basic configuration template."""
        from scripts.index_docs import generate_config_template
        
        template = generate_config_template("basic")
        
        assert "repositories" in template
        assert "paths" in template
        assert template["repositories"] == [
            {"url": "https://github.com/example/repo.git", "name": "example", "branch": "main"}
        ]
    
    def test_generate_advanced_template(self):
        """Test generating advanced configuration template."""
        from scripts.index_docs import generate_config_template
        
        template = generate_config_template("advanced")
        
        assert "repositories" in template
        assert "paths" in template
        assert "settings" in template
        assert "features" in template
        assert template["settings"]["max_file_size"] == 1048576
        assert template["features"]["semantic_search"] is True
    
    def test_generate_minimal_template(self):
        """Test generating minimal configuration template."""
        from scripts.index_docs import generate_config_template
        
        template = generate_config_template("minimal")
        
        # Should only contain essential fields
        assert "repositories" in template
        assert "paths" in template
        assert "settings" not in template
        assert "features" not in template