"""
Tests for MCP security measures.
"""
import os
import tempfile
import shutil
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from mcp.models import Document, Repository


class TestInputSanitization:
    """Test input sanitization and validation."""
    
    def test_sql_injection_prevention(self, temp_dir):
        """Test prevention of SQL injection attacks."""
        from mcp.storage import index_docs
        
        db_path = os.path.join(temp_dir, "test.db")
        zim_dir = os.path.join(temp_dir, "zim")
        os.makedirs(zim_dir, exist_ok=True)
        
        # Attempt SQL injection through repository name
        malicious_doc = Document(
            repo="test'; DROP TABLE docs; --",
            path="README.md",
            content="# Test content"
        )
        
        # Should sanitize the input and not execute the injection
        index_docs([malicious_doc], zim_dir, db_path)
        
        # Verify the table still exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='docs'")
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "docs"
        conn.close()
    
    def test_path_traversal_prevention(self, temp_dir):
        """Test prevention of path traversal attacks."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="../../../etc/passwd",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
            mock_files = [
                ("/tmp/../../../../etc", [], ["passwd"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_file.read.return_value = "root:x:0:0:root:/root:/bin/bash"
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # Should sanitize paths and not access system files
                    docs = fetch_repo(repo, temp_dir)
                    
                    # Should not have accessed the system file
                    assert not any(call[0][0].endswith('/etc/passwd') 
                                 for call in mock_open.call_args_list)
    
    def test_malformed_repository_urls(self, temp_dir):
        """Test handling of malformed repository URLs."""
        from mcp.git_fetcher import fetch_repo
        
        # Test various malicious URLs
        malicious_urls = [
            "https://github.com/test/repo.git; rm -rf /",
            "https://github.com/test/repo.git && cat /etc/passwd",
            "https://github.com/test/repo.git`whoami`",
            "https://github.com/test/repo.git$(id)",
            "https://github.com/test/repo.git; python -c 'import os; os.system(\"id\")'"
        ]
        
        for url in malicious_urls:
            repo = Repository(url=url, name="test-repo", branch="main")
            
            with patch('mcp.git_fetcher.Repo.clone_from') as mock_clone:
                # Should sanitize the URL before using it
                try:
                    fetch_repo(repo, temp_dir)
                except GitCommandError:
                    pass  # Expected for invalid URLs
                
                # Verify the URL was sanitized
                if mock_clone.called:
                    called_url = mock_clone.call_args[0][0]
                    assert ';' not in called_url
                    assert '`' not in called_url
                    assert '$' not in called_url
                    assert '&&' not in called_url
    
    def test_command_injection_prevention(self, temp_dir):
        """Test prevention of command injection attacks."""
        from mcp.server import app
        
        client = TestClient(app)
        
        # Test command injection in query parameters
        injection_payloads = [
            "test; cat /etc/passwd",
            "test && rm -rf /",
            "test`whoami`,",
            "test$(id)",
            "test; python -c 'import os; os.system(\"id\")'"
        ]
        
        for payload in injection_payloads:
            response = client.get(f"/docs?repo={payload}")
            
            # Should not execute commands, should either return empty results or 400
            assert response.status_code in [200, 400]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)  # Should return valid JSON, not command output


class TestAuthenticationAndAuthorization:
    """Test authentication and authorization measures."""
    
    def test_api_key_authentication(self, client):
        """Test API key authentication."""
        # Mock API key validation
        with patch('mcp.server.validate_api_key') as mock_validate:
            # Test without API key
            response = client.get("/docs")
            # Should require API key
            assert response.status_code == 401
            
            # Test with invalid API key
            mock_validate.return_value = False
            response = client.get("/docs", headers={"X-API-Key": "invalid-key"})
            assert response.status_code == 401
            
            # Test with valid API key
            mock_validate.return_value = True
            response = client.get("/docs", headers={"X-API-Key": "valid-key"})
            assert response.status_code == 200
    
    def test_rate_limiting(self, client):
        """Test rate limiting to prevent abuse."""
        with patch('mcp.server.check_rate_limit') as mock_rate_limit:
            # First few requests should succeed
            mock_rate_limit.return_value = True
            
            for i in range(5):
                response = client.get("/docs")
                assert response.status_code == 200
            
            # After rate limit is exceeded
            mock_rate_limit.return_value = False
            response = client.get("/docs")
            assert response.status_code == 429  # Too Many Requests
    
    def test_permission_based_access_control(self, client):
        """Test permission-based access control."""
        with patch('mcp.server.get_user_permissions') as mock_permissions:
            # User with read permissions
            mock_permissions.return_value = ["read"]
            
            response = client.get("/docs")
            assert response.status_code == 200
            
            # User without write permissions
            response = client.post("/docs", json={"some": "data"})
            assert response.status_code == 403  # Forbidden
            
            # User with admin permissions
            mock_permissions.return_value = ["read", "write", "admin"]
            response = client.post("/docs", json={"some": "data"})
            assert response.status_code == 200


class TestDataValidation:
    """Test data validation and sanitization."""
    
    def test_document_content_validation(self):
        """Test validation of document content."""
        from mcp.models import Document
        
        # Valid document
        valid_doc = Document(
            repo="test-repo",
            path="README.md",
            content="# Valid content"
        )
        assert valid_doc.content == "# Valid content"
        
        # Document with potentially dangerous content
        dangerous_content = """
        # Normal content
        <script>alert('XSS')</script>
        <?php system('id'); ?>
        `rm -rf /`
        $(cat /etc/passwd)
        """
        
        dangerous_doc = Document(
            repo="test-repo",
            path="README.md",
            content=dangerous_content
        )
        
        # Should sanitize dangerous content
        assert "<script>" not in dangerous_doc.content
        assert "<?php" not in dangerous_doc.content
        assert "`" not in dangerous_doc.content
    
    def test_file_size_limits(self, temp_dir):
        """Test enforcement of file size limits."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from'):
            # Mock finding a very large file (10MB)
            mock_files = [
                ("/tmp/test-repo", [], ["huge_file.md"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_file.read.return_value = "# " + "Large content " * 1000000
                    mock_file.__len__.return_value = 10 * 1024 * 1024  # 10MB
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # Should skip files that exceed size limit
                    docs = fetch_repo(repo, temp_dir)
                    assert len(docs) == 0  # Large file should be skipped
    
    def test_file_extension_whitelist(self, temp_dir):
        """Test file extension whitelist enforcement."""
        from mcp.git_fetcher import fetch_repo
        
        repo = Repository(
            url="https://github.com/test/repo.git",
            name="test-repo",
            branch="main"
        )
        
        with patch('mcp.git_fetcher.Repo.clone_from'):
            # Mix of allowed and disallowed files
            mock_files = [
                ("/tmp/test-repo", [], ["README.md", "script.py", "data.json", "config.exe"])
            ]
            
            with patch('mcp.git_fetcher.os.walk', return_value=mock_files):
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_file.read.return_value = "# Content"
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    docs = fetch_repo(repo, temp_dir)
                    
                    # Should only process .md files
                    processed_files = [doc.path for doc in docs]
                    assert "README.md" in processed_files
                    assert "script.py" not in processed_files
                    assert "data.json" not in processed_files
                    assert "config.exe" not in processed_files


class TestSecureCommunication:
    """Test secure communication measures."""
    
    def test_https_enforcement(self, client):
        """Test enforcement of HTTPS for all communications."""
        # Mock HTTPS redirect
        with patch('mcp.server.enforce_https') as mock_https:
            # HTTP request should be redirected
            response = client.get("http://localhost/docs", allow_redirects=False)
            assert response.status_code == 308  # Permanent Redirect
            assert response.headers["location"].startswith("https://")
    
    def test_security_headers(self, client):
        """Test security headers are properly set."""
        response = client.get("/docs")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Strict-Transport-Security" in response.headers
        assert "max-age" in response.headers["Strict-Transport-Security"]
    
    def test_cors_configuration(self, client):
        """Test CORS configuration for security."""
        # Test with allowed origin
        response = client.get("/docs", headers={"Origin": "https://trusted-domain.com"})
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        
        # Test with disallowed origin
        response = client.get("/docs", headers={"Origin": "https://malicious-site.com"})
        assert response.status_code == 200
        # Should not include CORS headers for untrusted origins
        assert "Access-Control-Allow-Origin" not in response.headers


class TestAuditLogging:
    """Test audit logging for security events."""
    
    def test_security_event_logging(self):
        """Test logging of security events."""
        from mcp.server import log_security_event
        
        with patch('mcp.server.logger') as mock_logger:
            # Log authentication failure
            log_security_event(
                event_type="authentication_failure",
                user_id="unknown",
                ip_address="192.168.1.100",
                details="Invalid API key"
            )
            
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            assert "authentication_failure" in call_args
            assert "192.168.1.100" in call_args
    
    def test_access_logging(self, client):
        """Test access logging for API endpoints."""
        with patch('mcp.server.logger') as mock_logger:
            # Make API request
            response = client.get("/docs?repo=test")
            
            assert response.status_code == 200
            # Should log the access
            mock_logger.info.assert_called()
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("GET /docs" in log for log in log_calls)


class TestVulnerabilityProtection:
    """Test protection against common vulnerabilities."""
    
    def test_xss_prevention(self, client):
        """Test XSS prevention in API responses."""
        # Mock database with potentially dangerous content
        with patch('mcp.server.get_documents') as mock_get_docs:
            mock_get_docs.return_value = [
                {
                    "repo": "test",
                    "path": "README.md",
                    "content": "<script>alert('XSS')</script>",
                    "version": "latest"
                }
            ]
            
            response = client.get("/docs")
            assert response.status_code == 200
            
            data = response.json()
            # Content should be escaped
            assert "<script>" not in json.dumps(data)
            assert "&lt;script&gt;" in json.dumps(data)
    
    def test_json_injection_prevention(self, client):
        """Test prevention of JSON injection attacks."""
        # Try to inject malformed JSON
        response = client.post("/search/semantic", json={
            "query": 'test", "malicious": "injection"}',
            "repo": "test-repo"
        })
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_header_injection_prevention(self, client):
        """Test prevention of HTTP header injection."""
        # Try header injection in query parameters
        response = client.get("/docs?repo=test\r\nX-Injected: header")
        
        assert response.status_code == 200
        # Should not contain injected header
        assert "X-Injected" not in response.headers


class TestEnvironmentSecurity:
    """Test security of environment and configuration."""
    
    def test_sensitive_data_redaction(self):
        """Test redaction of sensitive data in logs."""
        from mcp.server import sanitize_for_logging
        
        # Test API key redaction
        sensitive_data = {
            "api_key": "secret-key-12345",
            "password": "my-password",
            "token": "bearer-token-abc",
            "normal_field": "normal-value"
        }
        
        sanitized = sanitize_for_logging(sensitive_data)
        
        assert sanitized["api_key"] == "***REDACTED***"
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["token"] == "***REDACTED***"
        assert sanitized["normal_field"] == "normal-value"
    
    def test_environment_variable_security(self):
        """Test secure handling of environment variables."""
        from mcp.server import get_secure_environment_variable
        
        with patch.dict(os.environ, {'SECRET_API_KEY': 'secret-value'}):
            # Should retrieve the value
            value = get_secure_environment_variable('SECRET_API_KEY')
            assert value == 'secret-value'
            
            # Non-existent variable should return None, not raise error
            value = get_secure_environment_variable('NON_EXISTENT')
            assert value is None
    
    def test_configuration_encryption(self, temp_dir):
        """Test encryption of sensitive configuration values."""
        from mcp.server import encrypt_config_value, decrypt_config_value
        
        sensitive_value = "super-secret-api-key"
        
        # Encrypt the value
        encrypted = encrypt_config_value(sensitive_value)
        assert encrypted != sensitive_value
        assert len(encrypted) > len(sensitive_value)
        
        # Decrypt the value
        decrypted = decrypt_config_value(encrypted)
        assert decrypted == sensitive_value