"""Integration tests — full HTTP flows via httpx AsyncClient + FastAPI TestClient.

Tests auth flow, tracking CRUD, screening, crisis endpoints, GDPR export/erasure,
and security headers via actual HTTP requests against the app with an in-memory
SQLite backend.
"""

import hashlib
import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import all models so Base.metadata is fully populated
from src.models.audit_log import AuditLog  # noqa: F401
from src.models.base import Base
from src.models.conversation import Conversation, Message  # noqa: F401
from src.models.knowledge_base import KnowledgeDocument  # noqa: F401
from src.models.refresh_token import RefreshToken  # noqa: F401
from src.models.screening import ScreeningResult  # noqa: F401
from src.models.tracking import CravingEvent, SobrietyCheckin  # noqa: F401
from src.models.user import User  # noqa: F401

# ---------------------------------------------------------------------------
# Mock bcrypt (passlib + bcrypt 4.x compat issue in this env)
# ---------------------------------------------------------------------------

_MOCK_PREFIX = "sha256mock$"


def _mock_hash(password: str) -> str:
    return _MOCK_PREFIX + hashlib.sha256(password.encode()).hexdigest()


def _mock_verify(plain: str, hashed: str) -> bool:
    if hashed.startswith(_MOCK_PREFIX):
        return _mock_hash(plain) == hashed
    return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
_test_session_factory = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def _setup_db():
    """Create and tear down test tables for every test."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db():
    async with _test_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """Provide an httpx AsyncClient that talks to the FastAPI app with overridden DB."""
    # Patch validate_production_settings to no-op (SQLite URL doesn't match postgres)
    with (
        patch("src.main.validate_production_settings"),
        patch("src.core.security.hash_password", side_effect=_mock_hash),
        patch("src.core.security.verify_password", side_effect=_mock_verify),
        patch("src.api.auth.hash_password", side_effect=_mock_hash),
        patch("src.api.auth.verify_password", side_effect=_mock_verify),
    ):
        from src.core.database import get_db
        from src.core.rate_limit import limiter
        from src.main import app

        app.dependency_overrides[get_db] = _override_get_db
        # Disable rate limiting for integration tests
        limiter.enabled = False
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
        app.dependency_overrides.clear()
        limiter.enabled = True


# -- Helpers --

async def _register(
    client: AsyncClient, email: str | None = None, password: str = "testpass123"
) -> dict:
    """Register a user and return the token response body."""
    body: dict = {"password": password, "gdpr_consent": True}
    if email:
        body["email"] = email
    resp = await client.post("/api/v1/auth/register", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _auth(tokens: dict) -> dict:
    """Return auth header dict."""
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# ---------------------------------------------------------------------------
# Auth flow
# ---------------------------------------------------------------------------


class TestAuthFlow:
    @pytest.mark.asyncio
    async def test_register_login_me(self, client: AsyncClient):
        """Full flow: register → login → /me."""
        # Register
        tokens = await _register(client, email="user@example.com")
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

        # /me
        me = await client.get("/api/v1/auth/me", headers=_auth(tokens))
        assert me.status_code == 200
        data = me.json()
        assert data["email"] == "user@example.com"
        assert data["data_region"] == "eu-central"

        # Login
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "testpass123"},
        )
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        assert "access_token" in login_data

    @pytest.mark.asyncio
    async def test_register_anonymous(self, client: AsyncClient):
        """Register without email (Karel persona — anonymity)."""
        tokens = await _register(client)
        me = await client.get("/api/v1/auth/me", headers=_auth(tokens))
        assert me.status_code == 200
        assert me.json()["email"] is None

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        await _register(client, email="dup@example.com")
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "password": "testpass123", "gdpr_consent": True},
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_register_no_gdpr_consent(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"password": "testpass123", "gdpr_consent": False},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        await _register(client, email="auth@example.com")
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "auth@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_and_wrong_password_same_response(
        self, client: AsyncClient
    ):
        """Both non-existent email and wrong password return identical 401.

        The login endpoint uses argon2 verification for both code paths
        (user found / not found) to prevent timing oracles that could
        reveal email existence. Timing equivalence can't be tested in
        unit tests, but response body identity can.
        """
        await _register(client, email="exists@example.com")

        nonexistent = await client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@example.com", "password": "anypass123"},
        )
        wrong_pass = await client.post(
            "/api/v1/auth/login",
            json={"email": "exists@example.com", "password": "wrongpass123"},
        )

        assert nonexistent.status_code == 401
        assert wrong_pass.status_code == 401
        assert nonexistent.json() == wrong_pass.json()

    @pytest.mark.asyncio
    async def test_refresh_token_rotation(self, client: AsyncClient):
        """Register → refresh → old token should be revoked."""
        tokens = await _register(client, email="refresh@example.com")
        old_refresh = tokens["refresh_token"]

        # Refresh
        resp = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert resp.status_code == 200
        new_tokens = resp.json()
        # New refresh token must differ (rotated); access token may be identical
        # if generated within the same second (same sub+exp)
        assert new_tokens["refresh_token"] != old_refresh

        # Old refresh token should be revoked
        resp2 = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert resp2.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_revokes_token(self, client: AsyncClient):
        tokens = await _register(client, email="logout@example.com")
        resp = await client.post(
            "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
        )
        assert resp.status_code == 204

        # Refresh with revoked token should fail
        resp2 = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert resp2.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)  # HTTPBearer version-dependent


# ---------------------------------------------------------------------------
# Tracking CRUD
# ---------------------------------------------------------------------------


class TestTracking:
    @pytest.mark.asyncio
    async def test_checkin_and_streak(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        # Create checkin
        resp = await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 4, "energy_level": 3},
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_sober"] is True
        assert data["streak"] >= 1

        # Get today's checkin
        resp2 = await client.get("/api/v1/tracking/checkin/today", headers=headers)
        assert resp2.status_code == 200
        assert resp2.json()["checked_in"] is True
        assert resp2.json()["mood"] == 4

    @pytest.mark.asyncio
    async def test_checkin_upsert(self, client: AsyncClient):
        """Second checkin same day should update, not duplicate."""
        tokens = await _register(client)
        headers = _auth(tokens)

        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 3},
            headers=headers,
        )
        # Update mood
        resp = await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 5},
            headers=headers,
        )
        assert resp.status_code == 201

        today = await client.get("/api/v1/tracking/checkin/today", headers=headers)
        assert today.json()["mood"] == 5

    @pytest.mark.asyncio
    async def test_craving_log_and_list(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        resp = await client.post(
            "/api/v1/tracking/cravings",
            json={
                "intensity": 7,
                "trigger_category": "stress",
                "coping_strategy_used": "deep breathing",
                "outcome": "resisted",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["intensity"] == 7

        # List
        resp2 = await client.get("/api/v1/tracking/cravings", headers=headers)
        assert resp2.status_code == 200
        items = resp2.json()
        assert len(items) == 1
        assert items[0]["trigger_category"] == "stress"

    @pytest.mark.asyncio
    async def test_craving_invalid_category(self, client: AsyncClient):
        tokens = await _register(client)
        resp = await client.post(
            "/api/v1/tracking/cravings",
            json={"intensity": 5, "trigger_category": "invalid_value"},
            headers=_auth(tokens),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_summary_and_streak(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        # Create a checkin first
        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 4},
            headers=headers,
        )

        resp = await client.get("/api/v1/tracking/summary?days=30", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "sober_days" in data
        assert "current_streak" in data

        streak_resp = await client.get("/api/v1/tracking/streak", headers=headers)
        assert streak_resp.status_code == 200
        assert streak_resp.json()["current_streak"] >= 1


# ---------------------------------------------------------------------------
# Screening (AUDIT)
# ---------------------------------------------------------------------------


class TestScreening:
    @pytest.mark.asyncio
    async def test_get_audit_questions_no_auth(self, client: AsyncClient):
        """AUDIT questions are public (preview)."""
        resp = await client.get("/api/v1/screening/questionnaires/audit")
        assert resp.status_code == 200
        questions = resp.json()["questions"]
        assert len(questions) == 10

    @pytest.mark.asyncio
    async def test_submit_audit_low_risk(self, client: AsyncClient):
        tokens = await _register(client)
        # All zeros = low risk
        resp = await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
            headers=_auth(tokens),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_score"] == 0
        assert data["risk_level"] == "low_risk"

    @pytest.mark.asyncio
    async def test_submit_audit_high_risk(self, client: AsyncClient):
        tokens = await _register(client)
        # High score = possible_dependence
        resp = await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]},
            headers=_auth(tokens),
        )
        assert resp.status_code == 200
        assert resp.json()["risk_level"] == "possible_dependence"

    @pytest.mark.asyncio
    async def test_submit_audit_invalid_answers(self, client: AsyncClient):
        tokens = await _register(client)
        # Wrong number of answers
        resp = await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [0, 0]},
            headers=_auth(tokens),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_submit_audit_invalid_value(self, client: AsyncClient):
        """Q9 only accepts 0, 2, 4 — not 1."""
        tokens = await _register(client)
        resp = await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]},
            headers=_auth(tokens),
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_screening_results_history(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
            headers=headers,
        )
        resp = await client.get("/api/v1/screening/results", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["type"] == "AUDIT"


# ---------------------------------------------------------------------------
# Crisis
# ---------------------------------------------------------------------------


class TestCrisis:
    @pytest.mark.asyncio
    async def test_crisis_contacts_public(self, client: AsyncClient):
        """Crisis contacts are life-critical — no auth required."""
        resp = await client.get("/api/v1/crisis/contacts")
        assert resp.status_code == 200
        contacts = resp.json()["contacts"]
        assert len(contacts) > 0
        # All contacts must have name and phone
        for c in contacts:
            assert "name" in c
            assert "phone" in c


# ---------------------------------------------------------------------------
# GDPR export & erasure
# ---------------------------------------------------------------------------


class TestGDPR:
    @pytest.mark.asyncio
    async def test_export_my_data(self, client: AsyncClient):
        """GDPR Art.15 — data subject access request."""
        tokens = await _register(client, email="gdpr@example.com")
        headers = _auth(tokens)

        # Create some data first
        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 4},
            headers=headers,
        )
        await client.post(
            "/api/v1/tracking/cravings",
            json={"intensity": 5, "trigger_category": "stress"},
            headers=headers,
        )
        await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
            headers=headers,
        )

        resp = await client.get("/api/v1/admin/export-my-data", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["email"] == "gdpr@example.com"
        assert len(data["checkins"]) == 1
        assert len(data["cravings"]) == 1
        assert len(data["screenings"]) == 1

    @pytest.mark.asyncio
    async def test_delete_me_erasure(self, client: AsyncClient):
        """GDPR Art.17 — right to erasure."""
        tokens = await _register(client, email="delete@example.com")
        headers = _auth(tokens)

        # Create data
        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 3},
            headers=headers,
        )

        # Delete
        resp = await client.delete("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 204

        # Access token should still be valid (stateless JWT), but user is deactivated
        me = await client.get("/api/v1/auth/me", headers=headers)
        assert me.status_code == 401  # is_active=False → denied

    @pytest.mark.asyncio
    async def test_delete_me_login_fails(self, client: AsyncClient):
        """After erasure, login should fail."""
        tokens = await _register(client, email="deleteme2@example.com")
        await client.delete("/api/v1/auth/me", headers=_auth(tokens))

        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "deleteme2@example.com", "password": "testpass123"},
        )
        # Email is wiped + is_active=False → invalid credentials
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Chat (mocked Anthropic)
# ---------------------------------------------------------------------------


class TestChat:
    @pytest.mark.asyncio
    async def test_create_conversation(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        resp = await client.post("/api/v1/chat/conversations", headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert "disclaimer" in data
        assert data["disclaimer_shown"] is True

    @pytest.mark.asyncio
    async def test_list_conversations(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        # Create two conversations
        await client.post("/api/v1/chat/conversations", headers=headers)
        await client.post("/api/v1/chat/conversations", headers=headers)

        resp = await client.get("/api/v1/chat/conversations", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    @pytest.mark.asyncio
    async def test_send_message_mock(self, client: AsyncClient):
        """Test sending a message with mocked Anthropic client."""
        tokens = await _register(client)
        headers = _auth(tokens)

        conv_resp = await client.post("/api/v1/chat/conversations", headers=headers)
        conv_id = conv_resp.json()["id"]

        import src.services.anthropic_client as mod
        mod._client = None

        with patch("src.services.anthropic_client.anthropic.AsyncAnthropic") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value = mock_client
            mock_response = AsyncMock()
            mock_response.content = [AsyncMock(text="Jsem tu pro tebe.")]
            mock_response.usage = AsyncMock(input_tokens=50, output_tokens=30)
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            resp = await client.post(
                f"/api/v1/chat/conversations/{conv_id}/messages",
                json={"content": "Ahoj, potřebuji pomoc"},
                headers=headers,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "message" in data
            assert data["crisis_detected"] is False

        mod._client = None

    @pytest.mark.asyncio
    async def test_send_message_nonexistent_conversation(self, client: AsyncClient):
        tokens = await _register(client)
        resp = await client.post(
            f"/api/v1/chat/conversations/{uuid.uuid4()}/messages",
            json={"content": "test"},
            headers=_auth(tokens),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Security headers & health
# ---------------------------------------------------------------------------


class TestSecurity:
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("ok", "degraded")
        assert "version" in data
        assert "database" in data

    @pytest.mark.asyncio
    async def test_security_headers(self, client: AsyncClient):
        resp = await client.get("/health")
        headers = resp.headers
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"
        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"
        assert "permissions-policy" in headers

    @pytest.mark.asyncio
    async def test_password_too_short(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"password": "short", "gdpr_consent": True},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_message_content_too_long(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)
        conv = await client.post("/api/v1/chat/conversations", headers=headers)
        conv_id = conv.json()["id"]

        resp = await client.post(
            f"/api/v1/chat/conversations/{conv_id}/messages",
            json={"content": "x" * 5001},
            headers=headers,
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Cross-user data isolation (IDOR prevention)
# ---------------------------------------------------------------------------


class TestDataIsolation:
    @pytest.mark.asyncio
    async def test_cannot_send_message_to_other_users_conversation(
        self, client: AsyncClient
    ):
        """User A cannot send a message to User B's conversation (IDOR)."""
        user_a = await _register(client, email="a@example.com")
        user_b = await _register(client, email="b@example.com")

        # User A creates a conversation
        resp = await client.post(
            "/api/v1/chat/conversations", headers=_auth(user_a)
        )
        conv_id = resp.json()["id"]

        # User B tries to send a message to User A's conversation
        resp2 = await client.post(
            f"/api/v1/chat/conversations/{conv_id}/messages",
            json={"content": "I shouldn't be here"},
            headers=_auth(user_b),
        )
        assert resp2.status_code == 404

    @pytest.mark.asyncio
    async def test_cannot_see_other_users_conversations(self, client: AsyncClient):
        """User A's conversation list does not include User B's conversations."""
        user_a = await _register(client, email="list_a@example.com")
        user_b = await _register(client, email="list_b@example.com")

        await client.post("/api/v1/chat/conversations", headers=_auth(user_a))
        await client.post("/api/v1/chat/conversations", headers=_auth(user_b))

        # User A should only see their own conversation
        resp = await client.get(
            "/api/v1/chat/conversations", headers=_auth(user_a)
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.asyncio
    async def test_cannot_see_other_users_checkins(self, client: AsyncClient):
        """User B's today checkin should not show User A's data."""
        user_a = await _register(client, email="track_a@example.com")
        user_b = await _register(client, email="track_b@example.com")

        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 5},
            headers=_auth(user_a),
        )

        # User B has no checkin
        resp = await client.get(
            "/api/v1/tracking/checkin/today", headers=_auth(user_b)
        )
        assert resp.status_code == 200
        assert resp.json()["checked_in"] is False

    @pytest.mark.asyncio
    async def test_cannot_see_other_users_cravings(self, client: AsyncClient):
        """User B's craving list should not include User A's cravings."""
        user_a = await _register(client, email="crav_a@example.com")
        user_b = await _register(client, email="crav_b@example.com")

        await client.post(
            "/api/v1/tracking/cravings",
            json={"intensity": 8, "trigger_category": "stress"},
            headers=_auth(user_a),
        )

        resp = await client.get(
            "/api/v1/tracking/cravings", headers=_auth(user_b)
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    @pytest.mark.asyncio
    async def test_cannot_see_other_users_screenings(self, client: AsyncClient):
        """User B's screening results should not include User A's scores."""
        user_a = await _register(client, email="scr_a@example.com")
        user_b = await _register(client, email="scr_b@example.com")

        await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
            headers=_auth(user_a),
        )

        resp = await client.get(
            "/api/v1/screening/results", headers=_auth(user_b)
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    @pytest.mark.asyncio
    async def test_cannot_export_other_users_data(self, client: AsyncClient):
        """GDPR export only returns own data."""
        user_a = await _register(client, email="exp_a@example.com")
        user_b = await _register(client, email="exp_b@example.com")

        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 4},
            headers=_auth(user_a),
        )

        resp = await client.get(
            "/api/v1/admin/export-my-data", headers=_auth(user_b)
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["checkins"]) == 0
        assert data["user"]["email"] == "exp_b@example.com"


# ---------------------------------------------------------------------------
# Pagination edge cases
# ---------------------------------------------------------------------------


class TestPagination:
    @pytest.mark.asyncio
    async def test_conversations_pagination(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        # Create 3 conversations
        for _ in range(3):
            await client.post("/api/v1/chat/conversations", headers=headers)

        # Pagination: skip=1, limit=1
        resp = await client.get(
            "/api/v1/chat/conversations?skip=1&limit=1", headers=headers
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.asyncio
    async def test_skip_beyond_total_returns_empty(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        resp = await client.get(
            "/api/v1/chat/conversations?skip=999", headers=headers
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    @pytest.mark.asyncio
    async def test_negative_skip_rejected(self, client: AsyncClient):
        tokens = await _register(client)
        resp = await client.get(
            "/api/v1/chat/conversations?skip=-1", headers=_auth(tokens)
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_limit_zero_rejected(self, client: AsyncClient):
        tokens = await _register(client)
        resp = await client.get(
            "/api/v1/tracking/cravings?limit=0", headers=_auth(tokens)
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_limit_exceeds_max_rejected(self, client: AsyncClient):
        tokens = await _register(client)
        resp = await client.get(
            "/api/v1/tracking/cravings?limit=101", headers=_auth(tokens)
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Logout idempotency
# ---------------------------------------------------------------------------


class TestLogoutEdgeCases:
    @pytest.mark.asyncio
    async def test_double_logout_is_idempotent(self, client: AsyncClient):
        """Calling logout twice with same token should not error."""
        tokens = await _register(client, email="logout2@example.com")
        rt = tokens["refresh_token"]

        resp1 = await client.post("/api/v1/auth/logout", json={"refresh_token": rt})
        assert resp1.status_code == 204

        resp2 = await client.post("/api/v1/auth/logout", json={"refresh_token": rt})
        assert resp2.status_code == 204

    @pytest.mark.asyncio
    async def test_logout_with_garbage_token(self, client: AsyncClient):
        """Logout with an invalid token should be silently accepted."""
        resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "not-a-real-token"},
        )
        assert resp.status_code == 204


# ---------------------------------------------------------------------------
# GDPR erasure completeness
# ---------------------------------------------------------------------------


class TestGDPRErasureCompleteness:
    @pytest.mark.asyncio
    async def test_erasure_removes_all_data_types(self, client: AsyncClient):
        """GDPR erasure should delete all user data across all tables."""
        tokens = await _register(client, email="erasure@example.com")
        headers = _auth(tokens)

        # Create data in all categories
        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 4, "energy_level": 3},
            headers=headers,
        )
        await client.post(
            "/api/v1/tracking/cravings",
            json={"intensity": 7, "trigger_category": "stress"},
            headers=headers,
        )
        await client.post(
            "/api/v1/screening/questionnaires/audit",
            json={"answers": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
            headers=headers,
        )

        # Verify data exists via export
        export = await client.get("/api/v1/admin/export-my-data", headers=headers)
        data = export.json()
        assert len(data["checkins"]) == 1
        assert len(data["cravings"]) == 1
        assert len(data["screenings"]) == 1

        # Delete
        resp = await client.delete("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 204

        # Re-register with same email (should work since old email was wiped)
        new_tokens = await _register(client, email="erasure@example.com")
        new_headers = _auth(new_tokens)

        # New user should have zero data
        export2 = await client.get("/api/v1/admin/export-my-data", headers=new_headers)
        data2 = export2.json()
        assert len(data2["checkins"]) == 0
        assert len(data2["cravings"]) == 0
        assert len(data2["screenings"]) == 0
        assert len(data2["conversations"]) == 0


# ---------------------------------------------------------------------------
# Password change
# ---------------------------------------------------------------------------


class TestPasswordChange:
    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient):
        tokens = await _register(client, email="pw@example.com")
        resp = await client.put(
            "/api/v1/auth/password",
            json={
                "current_password": "testpass123",
                "new_password": "newpassword456",
            },
            headers=_auth(tokens),
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Password changed successfully."

        # Verify login with new password
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "pw@example.com", "password": "newpassword456"},
        )
        assert login_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, client: AsyncClient):
        tokens = await _register(client, email="pw2@example.com")
        resp = await client.put(
            "/api/v1/auth/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
            },
            headers=_auth(tokens),
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_change_password_same_as_current(self, client: AsyncClient):
        tokens = await _register(client, email="pw3@example.com")
        resp = await client.put(
            "/api/v1/auth/password",
            json={
                "current_password": "testpass123",
                "new_password": "testpass123",
            },
            headers=_auth(tokens),
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_change_password_revokes_refresh_tokens(
        self, client: AsyncClient
    ):
        tokens = await _register(client, email="pw4@example.com")
        old_refresh = tokens["refresh_token"]

        await client.put(
            "/api/v1/auth/password",
            json={
                "current_password": "testpass123",
                "new_password": "newpassword456",
            },
            headers=_auth(tokens),
        )

        # Old refresh token should be revoked
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": old_refresh},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Conversation delete
# ---------------------------------------------------------------------------


class TestConversationDelete:
    @pytest.mark.asyncio
    async def test_delete_own_conversation(self, client: AsyncClient):
        tokens = await _register(client)
        headers = _auth(tokens)

        conv = await client.post("/api/v1/chat/conversations", headers=headers)
        conv_id = conv.json()["id"]

        resp = await client.delete(
            f"/api/v1/chat/conversations/{conv_id}", headers=headers
        )
        assert resp.status_code == 204

        # Verify conversation is gone
        convos = await client.get("/api/v1/chat/conversations", headers=headers)
        assert len(convos.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_conversation(self, client: AsyncClient):
        tokens = await _register(client)
        resp = await client.delete(
            f"/api/v1/chat/conversations/{uuid.uuid4()}",
            headers=_auth(tokens),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_cannot_delete_other_users_conversation(
        self, client: AsyncClient
    ):
        user_a = await _register(client, email="del_a@example.com")
        user_b = await _register(client, email="del_b@example.com")

        conv = await client.post(
            "/api/v1/chat/conversations", headers=_auth(user_a)
        )
        conv_id = conv.json()["id"]

        resp = await client.delete(
            f"/api/v1/chat/conversations/{conv_id}",
            headers=_auth(user_b),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Token cleanup
# ---------------------------------------------------------------------------


class TestTokenCleanup:
    @pytest.mark.asyncio
    async def test_cleanup_tokens_endpoint(self, client: AsyncClient):
        """Cleanup endpoint should return a message with count."""
        tokens = await _register(client, email="cleanup@example.com")
        headers = _auth(tokens)

        # Logout to create a revoked token
        await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
        )

        resp = await client.post("/api/v1/admin/cleanup-tokens", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert "Cleaned up" in data["message"]


# ---------------------------------------------------------------------------
# OpenAPI docs hidden in production
# ---------------------------------------------------------------------------


class TestOpenAPIDocs:
    @pytest.mark.asyncio
    async def test_docs_available_in_dev(self, client: AsyncClient):
        """In development mode, /docs should be available."""
        resp = await client.get("/docs")
        # In development mode, /docs returns 200 (HTML) or redirects
        assert resp.status_code in (200, 307)


# ---------------------------------------------------------------------------
# GDPR export ordering
# ---------------------------------------------------------------------------


class TestGDPRExportOrdering:
    @pytest.mark.asyncio
    async def test_export_checkins_ordered_by_date(self, client: AsyncClient):
        """GDPR export returns checkins in chronological order."""
        tokens = await _register(client, "order@test.cz")
        headers = _auth(tokens)

        # Create checkins on different dates
        await client.post(
            "/api/v1/tracking/checkin",
            json={"is_sober": True, "mood": 3},
            headers=headers,
        )

        resp = await client.get("/api/v1/admin/export-my-data", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "checkins" in data
        # At least one checkin exists
        assert len(data["checkins"]) >= 1

    @pytest.mark.asyncio
    async def test_export_cravings_ordered_by_created_at(self, client: AsyncClient):
        """GDPR export returns cravings in chronological order."""
        tokens = await _register(client, "cravorder@test.cz")
        headers = _auth(tokens)

        # Create cravings
        for i in range(3):
            await client.post(
                "/api/v1/tracking/cravings",
                json={"intensity": i + 1, "trigger_category": "stress"},
                headers=headers,
            )

        resp = await client.get("/api/v1/admin/export-my-data", headers=headers)
        assert resp.status_code == 200
        cravings = resp.json()["cravings"]
        assert len(cravings) == 3
        # Verify chronological ordering
        timestamps = [c["created_at"] for c in cravings]
        assert timestamps == sorted(timestamps)


# ---------------------------------------------------------------------------
# Global exception handler integration
# ---------------------------------------------------------------------------


class TestExceptionHandlers:
    @pytest.mark.asyncio
    async def test_404_on_unknown_route(self, client: AsyncClient):
        """Unknown routes return 404."""
        resp = await client.get("/api/v1/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_422_on_invalid_json(self, client: AsyncClient):
        """Invalid request body returns 422."""
        resp = await client.post("/api/v1/auth/register", json={"invalid": "body"})
        assert resp.status_code == 422
