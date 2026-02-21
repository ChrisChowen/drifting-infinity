"""Gacha service - manages pulls, banners, and collection."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.engine.economy.shards import SHARDS_PER_PULL
from app.engine.gacha.banners import get_banner, select_item_from_banner
from app.engine.gacha.duplicate import check_duplicate, compute_duplicate_refund
from app.engine.gacha.pity import update_pity_counters
from app.engine.gacha.pull import determine_rarity
from app.models.campaign import Campaign
from app.models.gacha import (
    GachaBannerState,
    GachaIdentity,
    GachaPull,
    GachaVariant,
    GachaWeapon,
)


async def get_or_create_banner_state(
    db: AsyncSession, campaign_id: str, banner_key: str
) -> GachaBannerState:
    """Get or create banner state for a campaign."""
    result = await db.execute(
        select(GachaBannerState).where(
            GachaBannerState.campaign_id == campaign_id,
            GachaBannerState.banner == banner_key,
        )
    )
    state = result.scalar_one_or_none()
    if not state:
        state = GachaBannerState(
            id=str(ULID()),
            campaign_id=campaign_id,
            banner=banner_key,
        )
        db.add(state)
        await db.flush()
    return state


async def get_owned_item_ids(
    db: AsyncSession, campaign_id: str, item_type: str
) -> set[str]:
    """Get IDs of items already owned."""
    if item_type == "variant":
        result = await db.execute(
            select(GachaVariant.id).where(GachaVariant.campaign_id == campaign_id)
        )
    elif item_type == "weapon":
        result = await db.execute(
            select(GachaWeapon.id).where(GachaWeapon.campaign_id == campaign_id)
        )
    elif item_type == "identity":
        result = await db.execute(
            select(GachaIdentity.id).where(GachaIdentity.campaign_id == campaign_id)
        )
    else:
        return set()

    return {row[0] for row in result.all()}


async def pull_gacha(
    db: AsyncSession, campaign_id: str, banner_key: str
) -> dict:
    """Perform a single gacha pull."""
    # Check campaign and shards
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    if campaign.astral_shard_balance < SHARDS_PER_PULL:
        return {"error": f"Not enough Astral Shards (need {SHARDS_PER_PULL})"}

    # Get banner
    banner = get_banner(banner_key)
    if not banner:
        return {"error": "Banner not found"}

    # Get banner state
    state = await get_or_create_banner_state(db, campaign_id, banner_key)

    # Deduct shards
    campaign.astral_shard_balance -= SHARDS_PER_PULL

    # Determine rarity
    pull_result = determine_rarity(
        pulls_since_rare=state.pulls_since_rare,
        pulls_since_very_rare=state.pulls_since_very_rare,
        pulls_since_legendary=state.pulls_since_legendary,
    )

    # Select item
    item = select_item_from_banner(banner, pull_result.rarity)
    if not item:
        return {"error": "No items available for this rarity"}

    # Check duplicate
    owned = await get_owned_item_ids(db, campaign_id, banner.item_type)
    is_dup = check_duplicate(item.id, owned)

    # Handle duplicate refund
    refund = None
    if is_dup:
        refund = compute_duplicate_refund(pull_result.rarity)
        campaign.astral_shard_balance += refund.refund_shards
        campaign.gold_balance += refund.refund_gold
    else:
        # Create the item
        new_id = str(ULID())
        if banner.item_type == "variant":
            db.add(GachaVariant(
                id=new_id, campaign_id=campaign_id,
                name=item.name, rarity=item.rarity,
                character_class="any", effect=item.effect,
                description=item.description,
            ))
        elif banner.item_type == "weapon":
            db.add(GachaWeapon(
                id=new_id, campaign_id=campaign_id,
                name=item.name, rarity=item.rarity,
                weapon_type="any", effect=item.effect,
                description=item.description,
            ))
        elif banner.item_type == "identity":
            db.add(GachaIdentity(
                id=new_id, campaign_id=campaign_id,
                name=item.name, rarity=item.rarity,
                effect=item.effect, description=item.description,
            ))

    # Record pull
    db.add(GachaPull(
        id=str(ULID()),
        campaign_id=campaign_id,
        banner=banner_key,
        rarity=pull_result.rarity,
        pull_number=state.total_pulls + 1,
        result_type=banner.item_type,
        result_id=item.id,
        result_name=item.name,
        was_pity=pull_result.was_pity,
        was_duplicate=is_dup,
    ))

    # Update pity counters
    new_counters = update_pity_counters(
        {
            "pulls_since_rare": state.pulls_since_rare,
            "pulls_since_very_rare": state.pulls_since_very_rare,
            "pulls_since_legendary": state.pulls_since_legendary,
            "total_pulls": state.total_pulls,
        },
        pull_result.rarity,
    )
    state.total_pulls = new_counters["total_pulls"]
    state.pulls_since_rare = new_counters["pulls_since_rare"]
    state.pulls_since_very_rare = new_counters["pulls_since_very_rare"]
    state.pulls_since_legendary = new_counters["pulls_since_legendary"]

    await db.flush()

    return {
        "item": {
            "id": item.id,
            "name": item.name,
            "rarity": pull_result.rarity,
            "type": banner.item_type,
            "description": item.description,
            "effect": item.effect,
        },
        "was_pity": pull_result.was_pity,
        "was_duplicate": is_dup,
        "duplicate_refund": {
            "shards": refund.refund_shards,
            "gold": refund.refund_gold,
        } if refund else None,
        "shards_remaining": campaign.astral_shard_balance,
        "pity_state": {
            "total_pulls": state.total_pulls,
            "pulls_since_rare": state.pulls_since_rare,
            "pulls_since_very_rare": state.pulls_since_very_rare,
            "pulls_since_legendary": state.pulls_since_legendary,
        },
    }
