"""Tests for sobriety tracking service — streak calculation, summaries."""

from datetime import date, timedelta

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import Base
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.models.user import User
from src.services.tracking import get_sobriety_streak, get_tracking_summary


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
    u = User(
        email="test@test.cz",
        password_hash="!",
        display_name="Test",
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


class TestSobrietyStreak:
    async def test_no_checkins_returns_zero(self, db, user):
        streak = await get_sobriety_streak(user.id, db)
        assert streak == 0

    async def test_single_sober_today(self, db, user):
        db.add(SobrietyCheckin(user_id=user.id, date=date.today(), is_sober=True))
        await db.commit()
        streak = await get_sobriety_streak(user.id, db)
        assert streak == 1

    async def test_consecutive_sober_days(self, db, user):
        today = date.today()
        for i in range(5):
            db.add(SobrietyCheckin(user_id=user.id, date=today - timedelta(days=i), is_sober=True))
        await db.commit()
        streak = await get_sobriety_streak(user.id, db)
        assert streak == 5

    async def test_streak_breaks_on_non_sober(self, db, user):
        today = date.today()
        db.add(SobrietyCheckin(user_id=user.id, date=today, is_sober=True))
        db.add(SobrietyCheckin(user_id=user.id, date=today - timedelta(days=1), is_sober=False))
        db.add(SobrietyCheckin(user_id=user.id, date=today - timedelta(days=2), is_sober=True))
        await db.commit()
        streak = await get_sobriety_streak(user.id, db)
        assert streak == 1

    async def test_streak_breaks_on_gap(self, db, user):
        today = date.today()
        db.add(SobrietyCheckin(user_id=user.id, date=today, is_sober=True))
        # Skip yesterday
        db.add(SobrietyCheckin(user_id=user.id, date=today - timedelta(days=2), is_sober=True))
        await db.commit()
        streak = await get_sobriety_streak(user.id, db)
        assert streak == 1

    async def test_streak_zero_when_today_not_sober(self, db, user):
        db.add(SobrietyCheckin(user_id=user.id, date=date.today(), is_sober=False))
        await db.commit()
        streak = await get_sobriety_streak(user.id, db)
        assert streak == 0

    async def test_streak_zero_when_no_today_checkin(self, db, user):
        """No checkin today means streak is zero even with past sober days."""
        yesterday = date.today() - timedelta(days=1)
        db.add(SobrietyCheckin(user_id=user.id, date=yesterday, is_sober=True))
        await db.commit()
        streak = await get_sobriety_streak(user.id, db)
        assert streak == 0


class TestTrackingSummary:
    async def test_empty_data(self, db, user):
        summary = await get_tracking_summary(user.id, 30, db)
        assert summary["sober_days"] == 0
        assert summary["total_days"] == 0
        assert summary["average_mood"] is None
        assert summary["total_cravings"] == 0
        assert summary["top_trigger"] is None
        assert summary["current_streak"] == 0

    async def test_with_checkins(self, db, user):
        today = date.today()
        db.add(SobrietyCheckin(user_id=user.id, date=today, is_sober=True, mood=4))
        db.add(
            SobrietyCheckin(
                user_id=user.id, date=today - timedelta(days=1), is_sober=True, mood=3
            )
        )
        db.add(
            SobrietyCheckin(
                user_id=user.id, date=today - timedelta(days=2), is_sober=False, mood=2
            )
        )
        await db.commit()

        summary = await get_tracking_summary(user.id, 30, db)
        assert summary["sober_days"] == 2
        assert summary["total_days"] == 3
        assert summary["average_mood"] == 3.0

    async def test_top_trigger(self, db, user):
        for _ in range(3):
            db.add(CravingEvent(user_id=user.id, intensity=5, trigger_category="stress"))
        db.add(CravingEvent(user_id=user.id, intensity=3, trigger_category="social"))
        await db.commit()

        summary = await get_tracking_summary(user.id, 30, db)
        assert summary["top_trigger"] == "stress"
        assert summary["total_cravings"] == 4
