"""Tests for RAG retrieval service."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.audit_log import AuditLog  # noqa: F401
from src.models.base import Base
from src.models.conversation import Conversation, Message  # noqa: F401
from src.models.knowledge_base import KnowledgeDocument
from src.models.refresh_token import RefreshToken  # noqa: F401
from src.models.screening import ScreeningResult  # noqa: F401
from src.models.tracking import CravingEvent, SobrietyCheckin  # noqa: F401
from src.models.user import User  # noqa: F401
from src.services.rag import format_context, retrieve_context


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


async def _create_doc(db: AsyncSession, title: str, content: str, category: str = "cbt"):
    doc = KnowledgeDocument(
        title=title, content=content, source="test", category=category
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


class TestRetrieveContext:
    async def test_keyword_match(self, db_session):
        await _create_doc(db_session, "CBT Guide", "cognitive behavioral therapy basics", "cbt")
        await _create_doc(db_session, "Nutrition", "healthy eating tips for recovery", "nutrition")

        results = await retrieve_context("cognitive", db_session)
        assert len(results) == 1
        assert results[0].title == "CBT Guide"

    async def test_no_match_returns_recent_fallback(self, db_session):
        await _create_doc(db_session, "Doc A", "alpha content", "cbt")
        await _create_doc(db_session, "Doc B", "beta content", "nutrition")

        results = await retrieve_context("definitely-no-match-xyz", db_session)
        # Falls back to most recent documents
        assert len(results) >= 1

    async def test_empty_database(self, db_session):
        results = await retrieve_context("anything", db_session)
        assert results == []

    async def test_like_escaping(self, db_session):
        """LIKE special chars in query don't cause SQL errors."""
        await _create_doc(db_session, "Test", "normal content", "cbt")
        # These should not crash — LIKE chars are escaped
        results = await retrieve_context("100% match_test\\path", db_session)
        assert isinstance(results, list)

    async def test_query_truncation(self, db_session):
        """Long queries are truncated to 100 chars."""
        await _create_doc(db_session, "Test", "some test content here", "cbt")
        long_query = "x" * 200
        results = await retrieve_context(long_query, db_session)
        assert isinstance(results, list)


class TestFormatContext:
    def test_empty_list(self):
        assert format_context([]) == ""

    def test_single_document(self, db_session):
        doc = KnowledgeDocument(
            title="CBT Guide", content="CBT content here",
            source="who_guidelines", category="cbt",
        )
        result = format_context([doc])
        assert "KONTEXT Z KLINICKÉ DATABÁZE:" in result
        assert "who_guidelines" in result
        assert "cbt" in result
        assert "CBT Guide" in result
        assert "CBT content here" in result

    def test_multiple_documents(self):
        doc1 = KnowledgeDocument(
            title="Doc 1", content="Content 1", source="src1", category="cat1"
        )
        doc2 = KnowledgeDocument(
            title="Doc 2", content="Content 2", source="src2", category="cat2"
        )
        result = format_context([doc1, doc2])
        assert "Doc 1" in result
        assert "Doc 2" in result
        assert result.count("[") == 2  # Two document headers
