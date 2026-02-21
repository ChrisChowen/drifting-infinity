import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select, text

from app.config import settings
from app.database import Base, async_session, create_tables, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    await create_tables()

    # Migrate arena tables if old VTT schema detected
    async with async_session() as session:
        result = await session.execute(text("PRAGMA table_info(arenas)"))
        columns = [row[1] for row in result.fetchall()]
        if "current_round" in columns:
            logger.info(
                "Old VTT schema detected — rebuilding "
                "arena-related tables..."
            )
            await session.execute(
                text("DROP TABLE IF EXISTS armillary_effects")
            )
            await session.execute(
                text("DROP TABLE IF EXISTS arena_creatures")
            )
            await session.execute(
                text("DROP TABLE IF EXISTS health_snapshots")
            )
            await session.execute(
                text("DROP TABLE IF EXISTS arenas")
            )
            await session.commit()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Arena tables rebuilt with new schema")

    # Auto-ingest curated monsters (SRD + Kobold Press) if any sources missing
    from sqlalchemy import distinct

    from app.data.monster_ingest import ingest_curated_monsters
    from app.data.open5e_client import Open5eClient
    from app.models.monster import Monster

    async with async_session() as session:
        existing_sources = (
            await session.execute(select(distinct(Monster.source)))
        ).scalars().all()
        curated = set(Open5eClient.CURATED_DOCUMENT_SLUGS)
        missing = curated - set(existing_sources)
        if missing:
            logger.info(
                f"Missing monster sources: {missing} — "
                f"ingesting curated monsters from Open5e..."
            )
            try:
                ingested = await ingest_curated_monsters(session)
                logger.info(f"Auto-ingested {ingested} curated monsters")
            except Exception as e:
                logger.error(f"Failed to auto-ingest monsters: {e}")

    # Auto-ingest SRD magic items if database is empty
    from app.data.magic_item_ingest import ingest_srd_magic_items
    from app.models.magic_item import MagicItem

    async with async_session() as session:
        count = (await session.execute(select(func.count()).select_from(MagicItem))).scalar() or 0
        if count == 0:
            logger.info("No magic items found — auto-ingesting SRD magic items from Open5e...")
            try:
                ingested = await ingest_srd_magic_items(session)
                logger.info(f"Auto-ingested {ingested} magic items")
            except Exception as e:
                logger.error(f"Failed to auto-ingest magic items: {e}")

    # Auto-ingest SRD spells if database is empty
    from app.data.spell_ingest import ingest_srd_spells
    from app.models.spell import Spell

    async with async_session() as session:
        count = (await session.execute(select(func.count()).select_from(Spell))).scalar() or 0
        if count == 0:
            logger.info("No spells found — auto-ingesting SRD spells from Open5e...")
            try:
                ingested = await ingest_srd_spells(session)
                logger.info(f"Auto-ingested {ingested} spells")
            except Exception as e:
                logger.error(f"Failed to auto-ingest spells: {e}")

    yield
    # Shutdown: cleanup if needed


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import all models so create_tables() sees them
    from app.models import campaign as _m1  # noqa: F401
    from app.models import campaign_meta as _m13  # noqa: F401
    from app.models import gacha as _m9  # noqa: F401
    from app.models import inventory as _m11  # noqa: F401
    from app.models import magic_item as _m10  # noqa: F401
    from app.models import run as _m4  # noqa: F401
    from app.models import snapshot as _m7  # noqa: F401
    from app.models import spell as _m12  # noqa: F401

    # Register routers
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
        secret_events,
        snapshots,
        social,
    )

    app.include_router(campaigns.router, prefix="/api")
    app.include_router(characters.router, prefix="/api")
    app.include_router(monsters.router, prefix="/api")
    app.include_router(runs.router, prefix="/api")
    app.include_router(floors.router, prefix="/api")
    app.include_router(arenas.router, prefix="/api")
    app.include_router(economy.router, prefix="/api")
    app.include_router(snapshots.router, prefix="/api")
    app.include_router(encounters.router, prefix="/api")
    app.include_router(armillary.router, prefix="/api")
    app.include_router(enhancements.router, prefix="/api")
    app.include_router(gacha.router, prefix="/api")
    app.include_router(rewards.router, prefix="/api")
    app.include_router(archive.router, prefix="/api")
    app.include_router(magic_items.router, prefix="/api")
    app.include_router(meta.router, prefix="/api")
    app.include_router(llm.router, prefix="/api")
    app.include_router(prep.router, prefix="/api")
    app.include_router(export.router, prefix="/api")
    app.include_router(social.router, prefix="/api")
    app.include_router(secret_events.router, prefix="/api")

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "app": settings.app_name}

    # Serve frontend static files in production (Docker)
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.is_dir():
        app.mount(
            "/",
            StaticFiles(directory=str(static_dir), html=True),
            name="static",
        )

    return app


app = create_app()
