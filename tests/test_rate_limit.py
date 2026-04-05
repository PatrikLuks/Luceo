"""Tests for rate limiting key function."""

from unittest.mock import MagicMock

from src.core.rate_limit import _key_func
from src.core.security import create_access_token


class TestRateLimitKeyFunc:
    def test_extracts_user_id_from_jwt(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token({"sub": user_id})

        request = MagicMock()
        request.headers = {"authorization": f"Bearer {token}"}

        key = _key_func(request)
        assert key == f"user:{user_id}"

    def test_falls_back_to_ip_without_auth(self):
        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.1"
        request.scope = {"type": "http"}

        key = _key_func(request)
        assert key == "ip:192.168.1.1"

    def test_falls_back_to_ip_with_invalid_jwt(self):
        request = MagicMock()
        request.headers = {"authorization": "Bearer invalid-token-value"}
        request.client.host = "10.0.0.1"
        request.scope = {"type": "http"}

        key = _key_func(request)
        assert key == "ip:10.0.0.1"
