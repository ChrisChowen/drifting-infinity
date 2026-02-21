"""Character death & respawn logic for the Armillary arena.

Rules (per GDD Phase 8):
- 3 lives per run (shared pool)
- Replacement starts at max(1, party_avg_level - 1)
- Inherits 50% of enhancements (random selection)
- Gold penalty: 20% of campaign's gold balance
"""

import random
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.models.campaign import Campaign
from app.models.character import Character, CharacterEnhancement
from app.models.run import Run


async def record_death(
    character_id: str,
    run_id: str,
    db: AsyncSession,
) -> dict:
    """Record a character death during a run."""
    character = await db.get(Character, character_id)
    if not character:
        raise ValueError("Character not found")

    run = await db.get(Run, run_id)
    if not run:
        raise ValueError("Run not found")

    if run.lives_remaining <= 0:
        raise ValueError("No lives remaining — run should end as 'party_wipe'")

    character.is_dead = True
    character.death_count += 1

    run.lives_remaining -= 1
    run.total_deaths += 1

    death_entry = {
        "character_id": character_id,
        "character_name": character.name,
        "death_number": run.total_deaths,
        "lives_remaining": run.lives_remaining,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    run.death_log = [*(run.death_log or []), death_entry]

    await db.flush()

    return {
        "character_name": character.name,
        "death_count": character.death_count,
        "lives_remaining": run.lives_remaining,
        "total_deaths": run.total_deaths,
        "can_respawn": run.lives_remaining > 0,
    }


async def create_replacement(
    dead_character_id: str,
    campaign_id: str,
    replacement_data: dict,
    db: AsyncSession,
) -> Character:
    """Create a replacement character for a dead one.

    The replacement:
    - Starts at max(1, party_avg_level - 1)
    - Inherits 50% of the dead character's enhancements
    - Triggers a 20% gold penalty on the campaign
    """
    dead_char = await db.get(Character, dead_character_id)
    if not dead_char:
        raise ValueError("Dead character not found")

    # Compute party average level (excluding dead characters)
    result = await db.execute(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.is_dead == False,  # noqa: E712
        )
    )
    living = list(result.scalars().all())
    avg_level = (
        max(1, sum(c.level for c in living) // len(living))
        if living
        else dead_char.level
    )
    replacement_level = max(1, avg_level - 1)

    replacement = Character(
        id=str(ULID()),
        campaign_id=campaign_id,
        name=replacement_data.get("name", f"Replacement of {dead_char.name}"),
        character_class=replacement_data.get("character_class", dead_char.character_class),
        subclass=replacement_data.get("subclass"),
        level=replacement_level,
        ac=replacement_data.get("ac", dead_char.ac),
        max_hp=replacement_data.get("max_hp", dead_char.max_hp),
        speed=replacement_data.get("speed", dead_char.speed),
        saves=replacement_data.get("saves", dead_char.saves or {}),
        damage_types=replacement_data.get("damage_types", dead_char.damage_types or []),
        capabilities=replacement_data.get("capabilities", dead_char.capabilities or {}),
        is_replacement=True,
        original_character_id=dead_character_id,
    )
    db.add(replacement)

    dead_char.replaced_by_id = replacement.id

    # Inherit 50% of enhancements
    result = await db.execute(
        select(CharacterEnhancement).where(
            CharacterEnhancement.character_id == dead_character_id
        )
    )
    old_enhancements = list(result.scalars().all())
    if old_enhancements:
        inherit_count = max(1, len(old_enhancements) // 2)
        inherited = random.sample(old_enhancements, min(inherit_count, len(old_enhancements)))
        for i, enh in enumerate(inherited):
            db.add(CharacterEnhancement(
                id=str(ULID()),
                character_id=replacement.id,
                enhancement_id=enh.enhancement_id,
                slot_index=i,
            ))

    # Gold penalty: 20%
    campaign = await db.get(Campaign, campaign_id)
    if campaign and campaign.gold_balance > 0:
        penalty = int(campaign.gold_balance * 0.20)
        campaign.gold_balance = max(0, campaign.gold_balance - penalty)

    await db.flush()
    return replacement


async def get_lives_remaining(run_id: str, db: AsyncSession) -> dict:
    """Get current lives status for a run."""
    run = await db.get(Run, run_id)
    if not run:
        raise ValueError("Run not found")

    return {
        "lives_remaining": run.lives_remaining,
        "total_deaths": run.total_deaths,
        "death_log": run.death_log or [],
        "max_lives": 3,
    }
