"""Tests for refresh token create/verify/revoke/rotation."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.core.security import (
    _hash_token,
    create_refresh_token,
    revoke_refresh_token,
    verify_refresh_token,
)
from src.models.refresh_token import RefreshToken


class TestRefreshTokens:
    async def test_create_returns_nonempty_string(self, db_session):
        user_id = uuid.uuid4()
        raw = await create_refresh_token(user_id, db_session)
        assert isinstance(raw, str)
        assert len(raw) > 20

    async def test_verify_valid_token(self, db_session):
        user_id = uuid.uuid4()
        raw = await create_refresh_token(user_id, db_session)
        await db_session.commit()

        entry = await verify_refresh_token(raw, db_session)
        assert entry.user_id == user_id
        assert entry.revoked_at is None

    async def test_verify_wrong_token_raises(self, db_session):
        user_id = uuid.uuid4()
        await create_refresh_token(user_id, db_session)
        await db_session.commit()

        with pytest.raises(ValueError, match="Invalid or expired"):
            await verify_refresh_token("bogus-token-value", db_session)

    async def test_verify_expired_token_raises(self, db_session):
        user_id = uuid.uuid4()
        # Create a token manually with expired timestamp
        raw = "test-expired-token"
        entry = RefreshToken(
            user_id=user_id,
            token_hash=_hash_token(raw),
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        db_session.add(entry)
        await db_session.commit()

        with pytest.raises(ValueError, match="Invalid or expired"):
            await verify_refresh_token(raw, db_session)

    async def test_verify_revoked_token_raises(self, db_session):
        user_id = uuid.uuid4()
        raw = await create_refresh_token(user_id, db_session)
        await db_session.commit()

        entry = await verify_refresh_token(raw, db_session)
        await revoke_refresh_token(entry)
        await db_session.commit()

        with pytest.raises(ValueError, match="Invalid or expired"):
            await verify_refresh_token(raw, db_session)

    async def test_token_rotation(self, db_session):
        """Old token revoked, new token works."""
        user_id = uuid.uuid4()
        raw_old = await create_refresh_token(user_id, db_session)
        await db_session.commit()

        # Verify + revoke old
        old_entry = await verify_refresh_token(raw_old, db_session)
        await revoke_refresh_token(old_entry)

        # Create new
        raw_new = await create_refresh_token(user_id, db_session)
        await db_session.commit()

        # Old should fail
        with pytest.raises(ValueError):
            await verify_refresh_token(raw_old, db_session)

        # New should work
        new_entry = await verify_refresh_token(raw_new, db_session)
        assert new_entry.user_id == user_id

    def test_hash_token_deterministic(self):
        """SHA-256 hash is consistent for same input."""
        token = "some-random-token-value"
        assert _hash_token(token) == _hash_token(token)
        assert len(_hash_token(token)) == 64  # SHA-256 hex length
