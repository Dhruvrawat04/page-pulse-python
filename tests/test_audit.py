# tests/test_audit.py
import pytest
import httpx
from unittest.mock import AsyncMock, patch, Mock
from app.audit import PageAuditor

class TestPageAuditor:
    """Test the core auditing logic"""
    
    @pytest.fixture
    def auditor(self):
        return PageAuditor(timeout=5.0)
    
    @pytest.fixture
    def sample_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page - Awesome Site</title>
            <meta name="description" content="This is a test description for SEO">
        </head>
        <body>
            <h1>Welcome to Test Page</h1>
            <h1>Another H1 Tag</h1>
            <img src="image1.jpg" alt="Beautiful image">
            <img src="image2.jpg">
            <img src="image3.jpg" alt="">
            <p>This is a paragraph with some words for counting.</p>
            <p>Another paragraph with more content.</p>
        </body>
        </html>
        """
    
    # ===== HAPPY PATH TESTS =====
    
    @pytest.mark.asyncio
    async def test_parse_html_happy_path(self, auditor, sample_html):
        """Test HTML parsing works correctly with valid HTML"""
        result = auditor.parse_html(sample_html, "https://example.com")
        
        assert result['page_title'] == "Test Page - Awesome Site"
        assert result['meta_description'] == "This is a test description for SEO"
        assert result['h1_count'] == 2
        assert result['images_missing_alt'] == 2
        assert result['word_count'] > 0
    
    @pytest.mark.asyncio
    async def test_is_html_response_happy_path(self, auditor):
        """Test HTML content detection works"""
        assert auditor.is_html_response("text/html; charset=utf-8") is True
        assert auditor.is_html_response("text/html") is True
    
    # ===== FAILURE CASE 1: Non-HTML Content =====
    
    @pytest.mark.asyncio
    async def test_audit_non_html_content(self, auditor):
        """Test handling of non-HTML content"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.reason_phrase = "OK"
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await auditor.audit("https://api.example.com/data")
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error'] == 'URL does not return HTML content'
    
    # ===== FAILURE CASE 2: Timeout =====
    
    @pytest.mark.asyncio
    async def test_audit_timeout(self, auditor):
        """Test timeout handling"""
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Timeout")
            result = await auditor.audit("https://slow.example.com")
            
            assert result['success'] is False
            assert 'error' in result
            assert 'timed out' in result['error'].lower()
    
    # ===== FAILURE CASE 3: Connection Error =====
    
    @pytest.mark.asyncio
    async def test_audit_connection_error(self, auditor):
        """Test connection error handling"""
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")
            result = await auditor.audit("https://invalid-domain.example")
            
            assert result['success'] is False
            assert 'error' in result
            assert 'connect' in result['error'].lower()