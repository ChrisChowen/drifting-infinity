"""Reward service -- builds the post-arena reward screen.

Produces a diverse mix of pool consumables/gold/ability rewards, feat
placeholders, and magic items pulled from the SRD database, scaled by
floor depth and party level.
"""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.reward_pool import RewardDef, generate_reward_choices
from app.models.magic_item import MagicItem

# Rarity weights used when sampling DB magic items so that common items
# appear more frequently than legendary ones.
_RARITY_WEIGHT: dict[str, int] = {
    "common": 50,
    "uncommon": 35,
    "rare": 15,
    "very_rare": 8,
    "legendary": 3,
}


def _pool_reward_to_dict(r: RewardDef) -> dict:
    """Serialise a ``RewardDef`` from the static reward pool."""
    return {
        "id": r.id,
        "name": r.name,
        "rarity": r.rarity,
        "category": r.category,
        "description": r.description,
        "effect": r.effect,
        "source_type": "pool",
    }


def _feat_reward_to_dict(r: RewardDef) -> dict:
    """Serialise a feat ``RewardDef`` (separate source_type for frontend)."""
    return {
        "id": r.id,
        "name": r.name,
        "rarity": r.rarity,
        "category": r.category,
        "description": r.description,
        "effect": r.effect,
        "source_type": "feat",
    }


def _magic_item_to_dict(item: MagicItem) -> dict:
    """Serialise a ``MagicItem`` row from the database."""
    return {
        "id": item.id,
        "name": item.name,
        "rarity": item.rarity,
        "category": item.category,
        "description": item.description,
        "effect": {"type": "magic_item", "item_type": item.type},
        "requires_attunement": item.requires_attunement,
        "source_type": "magic_item",
    }


def _sample_magic_items(
    items: list[MagicItem],
    count: int,
) -> list[MagicItem]:
    """Weighted random sample of *count* magic items (without replacement)."""
    if not items:
        return []

    pool = list(items)
    selected: list[MagicItem] = []
    for _ in range(min(count, len(pool))):
        weights = [_RARITY_WEIGHT.get(i.rarity, 10) for i in pool]
        choice = random.choices(pool, weights=weights, k=1)[0]
        selected.append(choice)
        pool = [i for i in pool if i.id != choice.id]
    return selected


def _pick_feat_reward(
    floor_number: int,
    party_level: int,
    exclude_ids: set[str],
) -> RewardDef | None:
    """Pick one feat reward appropriate for floor and party level."""
    feats = generate_reward_choices(
        floor_number,
        count=1,
        categories=["feat"],
        exclude_ids=exclude_ids,
    )
    # Filter out Epic Boon if the party is too low level.
    feats = [
        f for f in feats
        if not (f.id == "rew_feat_epic_boon" and party_level < 19)
    ]
    return feats[0] if feats else None


async def _fetch_magic_items(
    floor_number: int,
    db: AsyncSession,
) -> list[MagicItem]:
    """Fetch all DB magic items eligible for the current floor."""
    try:
        result = await db.execute(
            select(MagicItem).where(MagicItem.floor_min <= floor_number)
        )
        return list(result.scalars().all())
    except Exception:
        return []


async def generate_arena_rewards(
    floor_number: int,
    party_level: int,
    db: AsyncSession,
) -> list[dict]:
    """Generate 3-4 reward choices for the post-arena selection screen.

    Mix by floor
    -------------
    Floor 1 : 2 consumable/gold/ability  +  1 feat
    Floor 2 : 1 consumable/gold/ability  +  1 feat  +  1 magic item (DB)
    Floor 3+: 1 consumable/gold/ability  +  1 feat  +  2 magic items (DB)

    If no magic items are available in the DB the empty slots are
    back-filled with additional pool rewards so the player always
    receives a full set of choices.
    """
    rewards: list[dict] = []
    used_ids: set[str] = set()

    # ── 1. Determine how many of each type we need ───────────────────
    if floor_number <= 1:
        pool_count = 2
        magic_count = 0
    elif floor_number == 2:
        pool_count = 1
        magic_count = 1
    else:
        pool_count = 1
        magic_count = 2

    # ── 2. Pick pool rewards (consumable / gold / ability) ───────────
    pool_choices = generate_reward_choices(
        floor_number,
        count=pool_count,
        categories=["consumable", "gold", "ability"],
    )
    for r in pool_choices:
        rewards.append(_pool_reward_to_dict(r))
        used_ids.add(r.id)

    # ── 3. Pick one feat reward ──────────────────────────────────────
    feat = _pick_feat_reward(floor_number, party_level, used_ids)
    if feat:
        rewards.append(_feat_reward_to_dict(feat))
        used_ids.add(feat.id)
    else:
        # No eligible feat -- fill with another pool reward instead.
        fallback = generate_reward_choices(
            floor_number,
            count=1,
            categories=["consumable", "gold", "ability"],
            exclude_ids=used_ids,
        )
        for r in fallback:
            rewards.append(_pool_reward_to_dict(r))
            used_ids.add(r.id)

    # ── 4. Pick magic items from DB (floors 2+) ─────────────────────
    if magic_count > 0:
        magic_items = await _fetch_magic_items(floor_number, db)
        sampled = _sample_magic_items(magic_items, magic_count)

        for item in sampled:
            rewards.append(_magic_item_to_dict(item))
            used_ids.add(item.id)

        # Back-fill if the DB didn't have enough magic items.
        shortfall = magic_count - len(sampled)
        if shortfall > 0:
            extras = generate_reward_choices(
                floor_number,
                count=shortfall,
                categories=["consumable", "gold", "ability"],
                exclude_ids=used_ids,
            )
            for r in extras:
                rewards.append(_pool_reward_to_dict(r))
                used_ids.add(r.id)

    return rewards
