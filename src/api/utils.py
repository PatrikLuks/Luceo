"""Shared API utilities."""

from fastapi import Request


def get_client_ip(request: Request) -> str | None:
    """Safely extract client IP — request.client can be None behind some proxies."""
    return request.client.host if request.client else None
