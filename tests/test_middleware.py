"""Tests for security headers middleware."""

from unittest.mock import patch

from starlette.responses import Response
from starlette.testclient import TestClient

from src.core.middleware import SecurityHeadersMiddleware


def _make_app():
    """Create a SecurityHeadersMiddleware wrapping a dummy app."""
    async def dummy_app(scope, receive, send):
        response = Response("ok")
        await response(scope, receive, send)

    return SecurityHeadersMiddleware(dummy_app)


class TestSecurityHeaders:
    def test_csp_header_present(self):
        client = TestClient(_make_app())
        response = client.get("/")
        assert (
            response.headers["Content-Security-Policy"]
            == "default-src 'none'; frame-ancestors 'none'"
        )

    def test_permissions_policy_present(self):
        client = TestClient(_make_app())
        response = client.get("/")
        assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"

    def test_hsts_in_production(self):
        with patch("src.core.middleware.settings") as mock_settings:
            mock_settings.app_env = "production"
            client = TestClient(_make_app())
            response = client.get("/")
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]

    def test_no_hsts_in_development(self):
        with patch("src.core.middleware.settings") as mock_settings:
            mock_settings.app_env = "development"
            client = TestClient(_make_app())
            response = client.get("/")
        assert "Strict-Transport-Security" not in response.headers

    def test_basic_headers_always_present(self):
        client = TestClient(_make_app())
        response = client.get("/")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_xss_protection_disabled(self):
        """X-XSS-Protection should be 0 (CSP handles XSS protection)."""
        client = TestClient(_make_app())
        response = client.get("/")
        assert response.headers["X-XSS-Protection"] == "0"

    def test_referrer_policy_present(self):
        client = TestClient(_make_app())
        response = client.get("/")
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
