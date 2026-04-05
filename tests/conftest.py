"""Shared test fixtures — async SQLite session, authenticated client, mocks."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.audit_log import AuditLog  # noqa: F401
from src.models.base import Base
from src.models.conversation import Conversation, Message  # noqa: F401
from src.models.knowledge_base import KnowledgeDocument  # noqa: F401
from src.models.refresh_token import RefreshToken  # noqa: F401
from src.models.screening import ScreeningResult  # noqa: F401
from src.models.tracking import CravingEvent, SobrietyCheckin  # noqa: F401

# Import all models so Base.metadata is fully populated for SQLite test DB
from src.models.user import User  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """Create an in-memory SQLite async session for testing."""
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
def mock_user_id():
    return uuid.uuid4()


@pytest.fixture
def mock_anthropic():
    """Mock the Anthropic client to avoid real API calls."""
    import src.services.anthropic_client as mod

    mod._client = None  # Reset singleton before test
    with patch("src.services.anthropic_client.anthropic.AsyncAnthropic") as mock_cls:
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client

        # Default response
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock(text="Jsem tu pro tebe. Jak ti mohu pomoci?")]
        mock_response.usage = AsyncMock(input_tokens=50, output_tokens=30)
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        yield mock_client

    mod._client = None  # Reset singleton after test
