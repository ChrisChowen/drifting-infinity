"""Enhancement service - purchase and equip enhancements."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.data.enhancement_definitions import (
    TIER_CAPS,
    get_enhancement,
)
from app.models.campaign import Campaign
from app.models.character import Character, CharacterEnhancement


async def get_character_enhancements(
    db: AsyncSession, character_id: str
) -> list[dict]:
    """Get all enhancements for a character."""
    result = await db.execute(
        select(CharacterEnhancement).where(
            CharacterEnhancement.character_id == character_id
        )
    )
    entries = result.scalars().all()
    return [
        {
            "id": e.id,
            "character_id": e.character_id,
            "enhancement_id": e.enhancement_id,
            "slot_index": e.slot_index,
            "purchased_at": e.purchased_at,
            "definition": get_enhancement(e.enhancement_id),
        }
        for e in entries
    ]


async def purchase_enhancement(
    db: AsyncSession,
    campaign_id: str,
    character_id: str,
    enhancement_id: str,
) -> dict:
    """Purchase and equip an enhancement."""
    # Validate enhancement exists
    enh_def = get_enhancement(enhancement_id)
    if not enh_def:
        return {"error": "Enhancement not found"}

    # Get campaign for gold check
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    # Check gold
    if campaign.gold_balance < enh_def.base_cost:
        return {"error": f"Not enough gold (need {enh_def.base_cost}, have {campaign.gold_balance})"}

    # Get character
    character = await db.get(Character, character_id)
    if not character:
        return {"error": "Character not found"}

    # Check tier cap
    existing = await db.execute(
        select(CharacterEnhancement).where(
            CharacterEnhancement.character_id == character_id
        )
    )
    existing_enhancements = existing.scalars().all()

    tier_count = sum(
        1 for e in existing_enhancements
        if get_enhancement(e.enhancement_id) and get_enhancement(e.enhancement_id).tier == enh_def.tier
    )
    tier_cap = TIER_CAPS.get(enh_def.tier, 3)
    if tier_count >= tier_cap:
        return {"error": f"Tier {enh_def.tier} cap reached ({tier_cap} max)"}

    # Check stack limit
    same_count = sum(
        1 for e in existing_enhancements
        if e.enhancement_id == enhancement_id
    )
    if same_count >= enh_def.max_stacks:
        return {"error": f"Max stacks reached for {enh_def.name} ({enh_def.max_stacks} max)"}

    # Deduct gold
    campaign.gold_balance -= enh_def.base_cost

    # Create enhancement entry
    slot_index = len(existing_enhancements)
    entry = CharacterEnhancement(
        id=str(ULID()),
        character_id=character_id,
        enhancement_id=enhancement_id,
        slot_index=slot_index,
    )
    db.add(entry)
    await db.flush()

    return {
        "success": True,
        "enhancement": {
            "id": entry.id,
            "name": enh_def.name,
            "tier": enh_def.tier,
            "cost": enh_def.base_cost,
        },
        "gold_remaining": campaign.gold_balance,
    }
