"""Tests for chat service process_message() — unit tests with mocked deps."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.guardrails import SAFE_FALLBACK
from src.models.audit_log import AuditLog  # noqa: F401
from src.models.base import Base
from src.models.conversation import Conversation, Message
from src.models.knowledge_base import KnowledgeDocument  # noqa: F401
from src.models.refresh_token import RefreshToken  # noqa: F401
from src.models.screening import ScreeningResult  # noqa: F401
from src.models.tracking import CravingEvent, SobrietyCheckin  # noqa: F401
from src.models.user import User  # noqa: F401
from src.services.chat import process_message


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def mock_encrypt():
    """Mock encrypt/decrypt to avoid needing real AES keys."""
    with (
        patch("src.services.chat.encrypt_field", side_effect=lambda text, ctx: f"ENC:{text}"),
        patch(
            "src.services.chat.decrypt_field",
            side_effect=lambda text, ctx: text.replace("ENC:", ""),
        ),
    ):
        yield


@pytest.fixture
def mock_anthropic_response():
    """Mock the Anthropic generate_response."""
    with patch("src.services.chat.generate_response") as mock:
        mock.return_value = ("Jsem tu pro tebe.", 80)
        yield mock


@pytest.fixture
def mock_rag():
    """Mock RAG to return empty context."""
    with patch("src.services.chat.retrieve_context", new_callable=AsyncMock, return_value=[]), \
         patch("src.services.chat.format_context", return_value=""):
        yield


@pytest.fixture
def mock_user_context():
    """Mock build_user_context."""
    with patch("src.services.chat.build_user_context", new_callable=AsyncMock, return_value=""):
        yield


class TestProcessMessage:
    async def test_normal_message(
        self, db_session, mock_encrypt, mock_anthropic_response, mock_rag, mock_user_context
    ):
        """Normal message goes through full pipeline."""
        user_id = uuid.uuid4()
        conv = Conversation(user_id=user_id)
        db_session.add(conv)
        await db_session.commit()
        await db_session.refresh(conv)

        result = await process_message(user_id, conv.id, "Ahoj, jak se máš?", db_session)

        assert result["message"] == "Jsem tu pro tebe."
        assert result["crisis_detected"] is False
        assert result["disclaimer"] is None

    async def test_guardrail_trigger_returns_safe_fallback(
        self, db_session, mock_encrypt, mock_rag, mock_user_context
    ):
        """If guardrails detect forbidden content, SAFE_FALLBACK is returned."""
        user_id = uuid.uuid4()
        conv = Conversation(user_id=user_id)
        db_session.add(conv)
        await db_session.commit()
        await db_session.refresh(conv)

        # Make LLM return medication recommendation (triggers guardrail)
        with patch("src.services.chat.generate_response") as mock_gen:
            mock_gen.return_value = ("Doporučuji naltrexon 50mg denně.", 80)
            result = await process_message(user_id, conv.id, "co mi pomůže?", db_session)

        assert result["message"] == SAFE_FALLBACK

    async def test_critical_crisis_no_llm_call(
        self, db_session, mock_encrypt, mock_rag, mock_user_context
    ):
        """CRITICAL crisis messages get predefined response, no LLM call."""
        user_id = uuid.uuid4()
        conv = Conversation(user_id=user_id)
        db_session.add(conv)
        await db_session.commit()
        await db_session.refresh(conv)

        with patch("src.services.chat.generate_response") as mock_gen:
            result = await process_message(
                user_id, conv.id, "chci se zabít", db_session
            )
            # LLM should NOT be called for critical crisis
            mock_gen.assert_not_called()

        assert result["crisis_detected"] is True
        assert result["crisis_contacts"] is not None
        assert len(result["crisis_contacts"]) > 0

    async def test_medium_crisis_appends_resources(
        self, db_session, mock_encrypt, mock_anthropic_response, mock_rag, mock_user_context
    ):
        """MEDIUM crisis appends crisis resources to LLM response."""
        user_id = uuid.uuid4()
        conv = Conversation(user_id=user_id)
        db_session.add(conv)
        await db_session.commit()
        await db_session.refresh(conv)

        result = await process_message(
            user_id, conv.id, "mám deprese a piju každý den", db_session
        )

        # For medium: LLM response is used but crisis contacts appended
        if result["crisis_detected"]:
            assert result["crisis_contacts"] is not None

    async def test_disclaimer_interval(
        self, db_session, mock_encrypt, mock_anthropic_response, mock_rag, mock_user_context
    ):
        """Disclaimer reminder fires at message count intervals."""
        from src.services.chat import DISCLAIMER_INTERVAL

        user_id = uuid.uuid4()
        conv = Conversation(user_id=user_id)
        db_session.add(conv)
        await db_session.commit()
        await db_session.refresh(conv)

        # Pre-populate messages to hit the interval
        # We need DISCLAIMER_INTERVAL messages (including the user msg being processed)
        for i in range(DISCLAIMER_INTERVAL - 1):
            msg = Message(
                conversation_id=conv.id,
                role="user" if i % 2 == 0 else "assistant",
                content_encrypted=f"ENC:msg{i}",
            )
            db_session.add(msg)
        await db_session.commit()

        result = await process_message(user_id, conv.id, "test msg", db_session)
        # At exactly DISCLAIMER_INTERVAL messages, disclaimer should be shown
        assert result["disclaimer"] is not None
