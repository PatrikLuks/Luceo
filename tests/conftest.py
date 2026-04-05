"""Shared test fixtures — async SQLite session, authenticated client, mocks."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import Base


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
    with patch("src.services.anthropic_client.anthropic.AsyncAnthropic") as mock_cls:
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client

        # Default response
        mock_response = AsyncMock()
        mock_response.content = [AsyncMock(text="Jsem tu pro tebe. Jak ti mohu pomoci?")]
        mock_response.usage = AsyncMock(input_tokens=50, output_tokens=30)
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        yield mock_client
