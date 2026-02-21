from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.database import get_db
from app.engine.combat.respawn import create_replacement, record_death
from app.engine.leveling import check_level_up
from app.engine.leveling import xp_to_next_level as engine_xp_to_next_level
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate, LevelUpData

router = APIRouter(prefix="/campaigns/{campaign_id}/characters", tags=["characters"])


def _to_response(c: Character) -> CharacterResponse:
    return CharacterResponse(
        id=c.id, campaign_id=c.campaign_id,
        name=c.name, character_class=c.character_class,
        subclass=c.subclass, level=c.level,
        ac=c.ac, max_hp=c.max_hp, speed=c.speed,
        saves=c.saves or {}, damage_types=c.damage_types or [],
        capabilities=c.capabilities or {},
        variant_id=c.variant_id, identity_id=c.identity_id,
        weapon_id=c.weapon_id,
        xp_total=c.xp_total, xp_to_next_level=c.xp_to_next_level,
        is_dead=c.is_dead, death_count=c.death_count,
        is_replacement=c.is_replacement,
        original_character_id=c.original_character_id,
        replaced_by_id=c.replaced_by_id,
    )


@router.get("", response_model=list[CharacterResponse])
async def list_characters(campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Character).where(Character.campaign_id == campaign_id)
    )
    return [_to_response(c) for c in result.scalars().all()]


@router.post("", response_model=CharacterResponse)
async def create_character(
    campaign_id: str, data: CharacterCreate, db: AsyncSession = Depends(get_db)
):
    character = Character(
        id=str(ULID()),
        campaign_id=campaign_id,
        name=data.name,
        character_class=data.character_class,
        subclass=data.subclass,
        level=data.level,
        ac=data.ac,
        max_hp=data.max_hp,
        speed=data.speed,
        saves=data.saves,
        damage_types=data.damage_types,
        capabilities=data.capabilities,
    )
    db.add(character)
    await db.flush()
    return _to_response(character)


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    campaign_id: str, character_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Character).where(
            Character.id == character_id, Character.campaign_id == campaign_id
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return _to_response(character)


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    campaign_id: str, character_id: str, data: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Character).where(
            Character.id == character_id, Character.campaign_id == campaign_id
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(character, field, value)

    await db.flush()
    return _to_response(character)


@router.delete("/{character_id}")
async def delete_character(
    campaign_id: str, character_id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Character).where(
            Character.id == character_id, Character.campaign_id == campaign_id
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    await db.delete(character)
    return {"message": "Character deleted"}


@router.post("/{character_id}/level-up", response_model=CharacterResponse)
async def level_up_character(
    campaign_id: str, character_id: str, data: LevelUpData, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Character).where(
            Character.id == character_id, Character.campaign_id == campaign_id
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if not check_level_up(character.level, character.xp_total):
        raise HTTPException(status_code=400, detail="Not enough XP to level up")

    old_required = character.xp_to_next_level

    # Increment level
    character.level = min(character.level + 1, 20)

    # Apply new stats
    character.max_hp = data.new_max_hp
    if data.new_ac is not None:
        character.ac = data.new_ac
    if data.new_saves is not None:
        character.saves = data.new_saves
    if data.new_capabilities is not None:
        character.capabilities = data.new_capabilities

    # Carry over excess XP and recompute threshold for new level
    character.xp_total = max(0, character.xp_total - old_required)
    character.xp_to_next_level = engine_xp_to_next_level(character.level)

    await db.flush()
    return _to_response(character)


@router.post("/{character_id}/award-xp", response_model=CharacterResponse)
async def award_xp(
    campaign_id: str, character_id: str, amount: int, db: AsyncSession = Depends(get_db)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="XP amount must be positive")

    result = await db.execute(
        select(Character).where(
            Character.id == character_id, Character.campaign_id == campaign_id
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    character.xp_total += amount
    await db.flush()
    return _to_response(character)


@router.post("/{character_id}/death")
async def record_character_death(
    campaign_id: str, character_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Record a character death during a run."""
    try:
        return await record_death(character_id, run_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{character_id}/respawn", response_model=CharacterResponse)
async def respawn_character(
    campaign_id: str, character_id: str,
    data: CharacterCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a replacement character for a dead one."""
    try:
        replacement = await create_replacement(
            dead_character_id=character_id,
            campaign_id=campaign_id,
            replacement_data=data.model_dump(),
            db=db,
        )
        return _to_response(replacement)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
