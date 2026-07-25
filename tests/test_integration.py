# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestIntegration:
    """Integration tests for the full API"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'Page Pulse'
    
    def test_audit_valid_url(self):
        """Test auditing a valid URL"""
        response = client.post(
            "/api/audit",
            json={"url": "https://example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'status' in data
    
    def test_audit_invalid_url_format(self):
        """Test invalid URL format"""
        response = client.post(
            "/api/audit",
            json={"url": "not-a-valid-url"}
        )
        assert response.status_code == 422