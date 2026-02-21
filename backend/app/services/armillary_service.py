"""Armillary service - bridges engine and database."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.engine.armillary.roller import (
    DEFAULT_CATEGORY_WEIGHTS,
    ArmillaryRollResult,
    roll_armillary_effect,
)
from app.engine.armillary.weight_adjuster import adjust_weights
from app.models.arena import Arena, ArmillaryEffect
from app.models.snapshot import HealthSnapshot


async def get_recent_effect_keys(db: AsyncSession, arena_id: str) -> list[str]:
    """Get recently used effect keys for this arena."""
    result = await db.execute(
        select(ArmillaryEffect.effect_key)
        .where(ArmillaryEffect.arena_id == arena_id)
        .order_by(ArmillaryEffect.round_number.desc())
        .limit(5)
    )
    return [row[0] for row in result.all()]


async def get_party_state_for_weights(
    db: AsyncSession, floor_id: str
) -> dict:
    """Get party state from latest health snapshot for weight adjustment."""
    result = await db.execute(
        select(HealthSnapshot)
        .where(HealthSnapshot.floor_id == floor_id)
        .order_by(HealthSnapshot.after_arena_number.desc())
    )
    snapshot = result.scalars().first()

    if not snapshot:
        return {
            "average_hp_percentage": 1.0,
            "any_dead": False,
            "cumulative_stress": 0.0,
        }

    return {
        "average_hp_percentage": snapshot.average_hp_percentage,
        "any_dead": snapshot.any_dead,
        "cumulative_stress": snapshot.cumulative_stress,
    }


async def roll_effect_for_arena(
    db: AsyncSession,
    arena: Arena,
    floor_id: str,
    round_number: int,
    floor_number: int = 1,
    armillary_aggression: float = 1.0,
) -> ArmillaryRollResult:
    """Roll an Armillary effect for the current round.

    Args:
        armillary_aggression: Campaign balance setting. >1.0 = more hostile events.
    """
    # Get recent effects to reduce repeats
    recent = await get_recent_effect_keys(db, arena.id)

    # Get party state for weight adjustment
    party_state = await get_party_state_for_weights(db, floor_id)

    # Adjust weights
    adjusted_weights = adjust_weights(
        base_weights=DEFAULT_CATEGORY_WEIGHTS,
        average_hp_percentage=party_state["average_hp_percentage"],
        any_dead=party_state["any_dead"],
        cumulative_stress=party_state["cumulative_stress"],
        arena_number=arena.arena_number,
        floor_number=floor_number,
    )

    # Apply armillary aggression setting
    if armillary_aggression != 1.0:
        adjusted_weights["hostile"] = max(
            5, int(adjusted_weights["hostile"] * armillary_aggression),
        )

    # Roll
    result = roll_armillary_effect(
        round_number=round_number,
        category_weights=adjusted_weights,
        recent_effect_keys=recent,
    )

    return result


async def save_armillary_effect(
    db: AsyncSession,
    arena_id: str,
    round_number: int,
    result: ArmillaryRollResult,
) -> ArmillaryEffect:
    """Save a rolled Armillary effect to the database."""
    effect = ArmillaryEffect(
        id=str(ULID()),
        arena_id=arena_id,
        round_number=round_number,
        category=result.effect.category,
        effect_key=result.effect.key,
        effect_description=result.effect.description,
        xp_cost=result.effect.xp_cost,
        was_rerolled=result.was_rerolled,
    )
    db.add(effect)
    await db.flush()
    return effect
