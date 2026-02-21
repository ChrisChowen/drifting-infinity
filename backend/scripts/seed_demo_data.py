"""Seed script for demo data.

Creates a demo campaign ("The Crimson Delvers") with four characters,
meta-progression state, and three completed runs.

Usage:
    python backend/scripts/seed_demo_data.py

Idempotent — skips seeding if the campaign already exists.
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow app imports from the backend directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from ulid import ULID

from app.models.campaign import Campaign
from app.models.campaign_meta import CampaignMeta
from app.models.character import Character
from app.models.run import Run

# Point at the project-root-relative database path
DATABASE_URL = "sqlite+aiosqlite:///backend/data/drifting_infinity.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

CAMPAIGN_NAME = "The Crimson Delvers"


async def seed() -> None:
    async with async_session_factory() as session:
        # ── Idempotency check ────────────────────────────────────────────
        result = await session.execute(
            select(Campaign).where(Campaign.name == CAMPAIGN_NAME)
        )
        if result.scalar_one_or_none() is not None:
            print(f'Campaign "{CAMPAIGN_NAME}" already exists — skipping seed.')
            return

        now = datetime.now(timezone.utc)

        # ── 1. Campaign ──────────────────────────────────────────────────
        campaign_id = str(ULID())
        campaign = Campaign(
            id=campaign_id,
            name=CAMPAIGN_NAME,
            gold_balance=450,
            astral_shard_balance=25,
            total_runs=3,
            party_power_coefficient=1.15,
            settings={},
            created_at=now,
            updated_at=now,
        )
        session.add(campaign)

        # ── 2. Characters ────────────────────────────────────────────────
        common = dict(
            campaign_id=campaign_id,
            is_dead=False,
            death_count=0,
            xp_total=6500,
            xp_to_next_level=14000,
            created_at=now,
        )

        characters = [
            Character(
                id=str(ULID()),
                name="Kael",
                character_class="Fighter",
                subclass=None,
                level=5,
                ac=18,
                max_hp=44,
                speed=30,
                saves={"str": 7, "con": 5, "dex": 2},
                damage_types=["slashing", "bludgeoning"],
                capabilities={
                    "melee": True,
                    "ranged": False,
                    "healing": False,
                    "aoe": True,
                    "crowd_control": False,
                    "support": False,
                },
                **common,
            ),
            Character(
                id=str(ULID()),
                name="Lyra",
                character_class="Cleric",
                subclass="Life Domain",
                level=5,
                ac=16,
                max_hp=38,
                speed=30,
                saves={"wis": 7, "cha": 4, "con": 3},
                damage_types=["radiant", "bludgeoning"],
                capabilities={
                    "melee": False,
                    "ranged": True,
                    "healing": True,
                    "aoe": True,
                    "crowd_control": False,
                    "support": True,
                },
                **common,
            ),
            Character(
                id=str(ULID()),
                name="Theron",
                character_class="Rogue",
                subclass="Assassin",
                level=5,
                ac=15,
                max_hp=33,
                speed=30,
                saves={"dex": 7, "int": 4, "cha": 2},
                damage_types=["piercing", "slashing"],
                capabilities={
                    "melee": True,
                    "ranged": True,
                    "healing": False,
                    "aoe": False,
                    "crowd_control": False,
                    "support": False,
                },
                **common,
            ),
            Character(
                id=str(ULID()),
                name="Zara",
                character_class="Sorcerer",
                subclass="Draconic",
                level=5,
                ac=14,
                max_hp=30,
                speed=30,
                saves={"cha": 7, "con": 4, "dex": 2},
                damage_types=["fire", "lightning", "cold"],
                capabilities={
                    "melee": False,
                    "ranged": True,
                    "healing": False,
                    "aoe": True,
                    "crowd_control": True,
                    "support": False,
                },
                **common,
            ),
        ]
        session.add_all(characters)

        # ── 3. CampaignMeta ──────────────────────────────────────────────
        meta = CampaignMeta(
            id=str(ULID()),
            campaign_id=campaign_id,
            essence_balance=45,
            essence_lifetime=120,
            unlocked_talents=["resilience_1", "insight_1"],
            achievements=["first_blood", "deathless_floor"],
            total_runs_completed=3,
            total_runs_won=2,
            highest_floor_reached=4,
            total_floors_cleared=10,
            total_deaths_all_runs=3,
            lore_fragments_found=["armillary_origin", "korvath_past"],
            created_at=now,
            updated_at=now,
        )
        session.add(meta)

        # ── 4. Runs ──────────────────────────────────────────────────────
        empty_json_defaults = dict(
            difficulty_curve=[],
            death_log=[],
            meta_snapshot={},
            affix_history=[],
            lore_beats_triggered=[],
            secret_events=[],
        )

        runs_data = [
            dict(
                starting_level=3,
                floor_count=4,
                floors_completed=4,
                outcome="completed",
                total_gold_earned=180,
                total_shards_earned=8,
                essence_earned=35,
                lives_remaining=2,
                total_deaths=1,
                started_at=now - timedelta(days=14),
                ended_at=now - timedelta(days=13),
            ),
            dict(
                starting_level=4,
                floor_count=4,
                floors_completed=2,
                outcome="failed",
                total_gold_earned=80,
                total_shards_earned=3,
                essence_earned=15,
                lives_remaining=0,
                total_deaths=3,
                started_at=now - timedelta(days=10),
                ended_at=now - timedelta(days=9),
            ),
            dict(
                starting_level=5,
                floor_count=4,
                floors_completed=4,
                outcome="completed",
                total_gold_earned=250,
                total_shards_earned=12,
                essence_earned=45,
                lives_remaining=1,
                total_deaths=2,
                started_at=now - timedelta(days=3),
                ended_at=now - timedelta(days=2),
            ),
        ]

        for run_data in runs_data:
            run = Run(
                id=str(ULID()),
                campaign_id=campaign_id,
                **run_data,
                **empty_json_defaults,
            )
            session.add(run)

        # ── Commit everything ─────────────────────────────────────────────
        await session.commit()
        print(f'Seeded campaign "{CAMPAIGN_NAME}" with 4 characters, meta, and 3 runs.')


if __name__ == "__main__":
    asyncio.run(seed())
