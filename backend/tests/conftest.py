"""Shared fixtures for the Drifting Infinity test suite."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db


@pytest_asyncio.fixture
async def db():
    """Create an in-memory SQLite database for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    """Create an async test client with an in-memory database.

    Overrides get_db to use a fresh in-memory SQLite DB for each test.
    Skips the lifespan (monster ingestion, etc.) for fast tests.
    """
    from fastapi import FastAPI

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False,
    )

    # Import all models so tables are registered
    import app.models.arena  # noqa: F401
    import app.models.campaign  # noqa: F401
    import app.models.campaign_meta  # noqa: F401
    import app.models.character  # noqa: F401
    import app.models.floor  # noqa: F401
    import app.models.gacha  # noqa: F401
    import app.models.inventory  # noqa: F401
    import app.models.magic_item  # noqa: F401
    import app.models.monster  # noqa: F401
    import app.models.run  # noqa: F401
    import app.models.snapshot  # noqa: F401
    import app.models.spell  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Build app without lifespan to avoid Open5e ingestion
    app = FastAPI(title="Test")

    # Register all routers the same way as create_app
    from app.routers import (
        archive,
        arenas,
        armillary,
        campaigns,
        characters,
        economy,
        encounters,
        enhancements,
        export,
        floors,
        gacha,
        llm,
        magic_items,
        meta,
        monsters,
        prep,
        rewards,
        runs,
        snapshots,
    )

    for r in [
        campaigns, characters, monsters, runs, floors, arenas,
        economy, snapshots, encounters, armillary, enhancements,
        gacha, rewards, archive, magic_items, meta, llm, prep, export,
    ]:
        app.include_router(r.router, prefix="/api")

    async def override_get_db():
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def party_4_level_3():
    """Standard party fixture: 4 characters at level 3."""
    return {
        "size": 4,
        "level": 3,
        "characters": [
            {"name": "Fighter", "class": "fighter", "level": 3, "ac": 18, "max_hp": 28},
            {"name": "Wizard", "class": "wizard", "level": 3, "ac": 13, "max_hp": 16},
            {"name": "Cleric", "class": "cleric", "level": 3, "ac": 18, "max_hp": 24},
            {"name": "Rogue", "class": "rogue", "level": 3, "ac": 15, "max_hp": 21},
        ],
    }


@pytest.fixture
def party_3_level_10():
    """Mid-tier party fixture: 3 characters at level 10."""
    return {
        "size": 3,
        "level": 10,
        "characters": [
            {"name": "Paladin", "class": "paladin", "level": 10, "ac": 20, "max_hp": 76},
            {"name": "Sorcerer", "class": "sorcerer", "level": 10, "ac": 14, "max_hp": 52},
            {"name": "Ranger", "class": "ranger", "level": 10, "ac": 17, "max_hp": 68},
        ],
    }
