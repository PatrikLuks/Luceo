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
        assert len(resp2.json()) == 1
        assert resp2.json()[0]["trigger_category"] == "stress"

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
        assert resp.json()["status"] == "ok"

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
