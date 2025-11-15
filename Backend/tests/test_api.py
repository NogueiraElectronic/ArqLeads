"""
Tests for API endpoints.
"""
import pytest
from fastapi import status


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data


class TestChatEndpoint:
    """Test chat message endpoint."""

    @pytest.mark.skip(reason="Requires AI provider setup")
    def test_send_message_creates_lead(self, client):
        """Test that sending a message creates a lead."""
        payload = {
            "session_id": "test-new-session",
            "message": "Hola, quiero reformar mi baño",
            "language": "es",
            "channel": "web"
        }

        response = client.post("/api/v1/chat/message", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "lead_score" in data
        assert data["lead_score"] >= 0

    def test_send_message_requires_session_id(self, client):
        """Test that session_id is required."""
        payload = {
            "message": "Hola",
            "language": "es",
            "channel": "web"
        }

        response = client.post("/api/v1/chat/message", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_send_empty_message_fails(self, client):
        """Test that empty messages are rejected."""
        payload = {
            "session_id": "test-session",
            "message": "",
            "language": "es",
            "channel": "web"
        }

        response = client.post("/api/v1/chat/message", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLeadsEndpoint:
    """Test leads management endpoints."""

    def test_get_all_leads(self, client, sample_lead):
        """Test retrieving all leads."""
        response = client.get("/api/v1/leads/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Juan Pérez"

    def test_get_lead_by_id(self, client, sample_lead):
        """Test retrieving a specific lead by ID."""
        response = client.get(f"/api/v1/leads/{sample_lead.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_lead.id
        assert data["email"] == "juan@example.com"

    def test_get_nonexistent_lead_returns_404(self, client):
        """Test that getting non-existent lead returns 404."""
        response = client.get("/api/v1/leads/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_hot_leads(self, client):
        """Test filtering hot leads."""
        response = client.get("/api/v1/leads/hot")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # All returned leads should be hot (score >= 70)
        for lead in data:
            assert lead["score"] >= 70

    def test_get_leads_stats(self, client, sample_lead):
        """Test leads statistics endpoint."""
        response = client.get("/api/v1/leads/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_leads" in data
        assert "hot_leads" in data
        assert "warm_leads" in data
        assert "cold_leads" in data
        assert data["total_leads"] >= 1


class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.skip(reason="Rate limiting tests need special setup")
    def test_rate_limit_blocks_excessive_requests(self, client):
        """Test that rate limiting blocks excessive requests."""
        # Send 200 requests rapidly
        responses = []
        for _ in range(200):
            response = client.get("/health")
            responses.append(response.status_code)

        # At least one should be rate limited (429)
        assert status.HTTP_429_TOO_MANY_REQUESTS in responses


class TestCORS:
    """Test CORS configuration."""

    def test_cors_allows_configured_origins(self, client):
        """Test that CORS headers are set correctly."""
        response = client.options(
            "/api/v1/leads/",
            headers={"Origin": "http://localhost:5173"}
        )

        assert "access-control-allow-origin" in response.headers.keys()
