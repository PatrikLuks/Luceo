"""Tests for user context builder — personalized LLM system prompt injection."""

from datetime import UTC, date, datetime, timedelta

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import Base
from src.models.screening import ScreeningResult
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.models.user import User
from src.services.user_context import build_user_context


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def user(db: AsyncSession):
    u = User(email="ctx@test.cz", password_hash="!", display_name="Ctx")
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


class TestBuildUserContext:
    async def test_new_user_returns_empty(self, db, user):
        """User with zero data gets empty context (no header either)."""
        ctx = await build_user_context(user.id, db)
        assert ctx == ""

    async def test_full_data(self, db, user):
        """User with streak, mood, cravings, and screening gets full context."""
        today = date.today()

        # Streak: 3 consecutive sober days
        for i in range(3):
            db.add(SobrietyCheckin(
                user_id=user.id,
                date=today - timedelta(days=i),
                is_sober=True,
                mood=4 if i == 0 else None,
                energy_level=3 if i == 0 else None,
            ))

        # Craving event
        db.add(CravingEvent(
            user_id=user.id,
            intensity=7,
            trigger_category="stres",
            outcome="resisted",
        ))

        # AUDIT screening
        db.add(ScreeningResult(
            user_id=user.id,
            questionnaire_type="AUDIT",
            answers={"1": 2},
            total_score=14,
            risk_level="hazardous",
            completed_at=datetime.now(UTC),
        ))

        await db.commit()

        ctx = await build_user_context(user.id, db)
        assert ctx.startswith("KONTEXT UŽIVATELE:")
        assert "3 dní v řadě" in ctx
        assert "Nálada: 4/5" in ctx
        assert "Energie: 3/5" in ctx
        assert "intenzita 7/10" in ctx
        assert "spouštěč: stres" in ctx
        assert "odolal" in ctx
        assert "skóre 14" in ctx
        assert "rizikové pití" in ctx

    async def test_only_streak_no_mood(self, db, user):
        """User with streak but no mood/energy still gets partial context."""
        today = date.today()
        db.add(SobrietyCheckin(
            user_id=user.id, date=today, is_sober=True, mood=None, energy_level=None,
        ))
        await db.commit()

        ctx = await build_user_context(user.id, db)
        assert "1 dní v řadě" in ctx
        assert "Nálada" not in ctx
        assert "Energie" not in ctx

    async def test_craving_without_outcome(self, db, user):
        """Craving with no outcome omits outcome text."""
        db.add(CravingEvent(
            user_id=user.id, intensity=5, trigger_category="social", outcome=None,
        ))
        await db.commit()

        ctx = await build_user_context(user.id, db)
        assert "intenzita 5/10" in ctx
        assert "výsledek" not in ctx

    async def test_gave_in_outcome(self, db, user):
        """outcome='gave_in' renders as 'neodolal'."""
        db.add(CravingEvent(
            user_id=user.id, intensity=8, trigger_category="emotional", outcome="gave_in",
        ))
        await db.commit()

        ctx = await build_user_context(user.id, db)
        assert "neodolal" in ctx

    async def test_screening_only(self, db, user):
        """User with only a screening result gets partial context."""
        db.add(ScreeningResult(
            user_id=user.id,
            questionnaire_type="AUDIT",
            answers={"1": 0},
            total_score=4,
            risk_level="low_risk",
            completed_at=datetime.now(UTC),
        ))
        await db.commit()

        ctx = await build_user_context(user.id, db)
        assert "skóre 4" in ctx
        assert "nízké riziko" in ctx
        assert "Střízlivost" not in ctx

    async def test_max_three_cravings(self, db, user):
        """Only the 3 most recent cravings are included."""
        for i in range(5):
            db.add(CravingEvent(
                user_id=user.id, intensity=i + 1, trigger_category="stress",
            ))
        await db.commit()

        ctx = await build_user_context(user.id, db)
        assert ctx.count("Chuť:") == 3
