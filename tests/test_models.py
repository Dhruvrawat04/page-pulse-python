# tests/test_models.py
import pytest
from pydantic import ValidationError
from app.models import AuditRequest

class TestModels:
    """Test Pydantic models"""
    
    def test_valid_http_url(self):
        """Test valid HTTP URL passes validation"""
        request = AuditRequest(url="http://example.com")
        # Pydantic automatically adds trailing slash
        assert str(request.url) == "http://example.com/"
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL passes validation"""
        request = AuditRequest(url="https://example.com")
        # Pydantic automatically adds trailing slash
        assert str(request.url) == "https://example.com/"
    
    def test_valid_url_with_path(self):
        """Test URL with path works"""
        request = AuditRequest(url="https://example.com/path/to/page?query=1")
        assert "example.com/path" in str(request.url)
    
    def test_valid_url_with_port(self):
        """Test URL with port works"""
        request = AuditRequest(url="https://example.com:8080")
        assert "example.com:8080" in str(request.url)
    
    def test_invalid_url_missing_scheme(self):
        """Test URL without http/https fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AuditRequest(url="example.com")
        # Pydantic V2 throws validation error for missing scheme
        assert "url" in str(exc_info.value)
    
    def test_invalid_url_malformed(self):
        """Test malformed URL fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            AuditRequest(url="not a url at all")
        assert "url" in str(exc_info.value)
    
    def test_invalid_url_ftp_scheme(self):
        """Test FTP URL fails validation (only http/https allowed)"""
        with pytest.raises(ValidationError) as exc_info:
            AuditRequest(url="ftp://example.com")
        # Pydantic HttpUrl only allows http/https
        assert "url" in str(exc_info.value)
    
    def test_valid_url_with_subdomain(self):
        """Test URL with subdomain works"""
        request = AuditRequest(url="https://sub.example.com")
        assert "sub.example.com" in str(request.url)
    
    def test_valid_url_with_www(self):
        """Test URL with www works"""
        request = AuditRequest(url="https://www.example.com")
        assert "www.example.com" in str(request.url)
    
    def test_valid_url_with_trailing_slash(self):
        """Test URL with trailing slash works"""
        request = AuditRequest(url="https://example.com/")
        assert str(request.url) == "https://example.com/"