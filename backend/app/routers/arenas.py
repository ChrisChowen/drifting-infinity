from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.database import get_db
from app.engine.economy.gold import compute_arena_gold
from app.engine.leveling import check_level_up, compute_arena_xp_award
from app.models.arena import Arena, ArenaCreatureStatus
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.floor import Floor
from app.models.run import Run
from app.schemas.arena import (
    ArenaCompleteResponse,
    ArenaCreatureStatusResponse,
    ArenaResponse,
    CreatureStatusUpdate,
)
from app.schemas.campaign import CampaignSettings

router = APIRouter(prefix="/floors/{floor_id}/arenas", tags=["arenas"])


def _to_response(a: Arena) -> ArenaResponse:
    return ArenaResponse(
        id=a.id,
        floor_id=a.floor_id,
        arena_number=a.arena_number,
        encounter_template=a.encounter_template,
        difficulty_target=a.difficulty_target,
        xp_budget=a.xp_budget,
        adjusted_xp=a.adjusted_xp,
        actual_difficulty=a.actual_difficulty,
        gold_earned_per_player=a.gold_earned_per_player,
        tactical_brief=a.tactical_brief,
        map_id=a.map_id,
        environment=a.environment,
        is_active=a.is_active,
        is_complete=a.is_complete,
        momentum_bonus_earned=a.momentum_bonus_earned,
        is_social=a.is_social,
        social_encounter_id=a.social_encounter_id,
        social_encounter_result=a.social_encounter_result,
        secret_event_id=a.secret_event_id,
        dm_notes=a.dm_notes,
        custom_read_aloud=a.custom_read_aloud,
        narrative_content=a.narrative_content,
    )


@router.get("", response_model=list[ArenaResponse])
async def list_arenas(floor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Arena).where(Arena.floor_id == floor_id).order_by(Arena.arena_number)
    )
    return [_to_response(a) for a in result.scalars().all()]


@router.post("", response_model=ArenaResponse)
async def start_arena(floor_id: str, db: AsyncSession = Depends(get_db)):
    # Get floor
    floor_result = await db.execute(select(Floor).where(Floor.id == floor_id))
    floor = floor_result.scalar_one_or_none()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    if floor.is_complete:
        raise HTTPException(status_code=400, detail="Floor already complete")

    # Calculate arena number
    existing = await db.execute(select(Arena).where(Arena.floor_id == floor_id))
    arena_number = len(existing.scalars().all()) + 1

    if arena_number > floor.arena_count:
        raise HTTPException(
            status_code=400,
            detail="All arenas already created",
        )

    arena = Arena(
        id=str(ULID()),
        floor_id=floor_id,
        arena_number=arena_number,
        is_active=True,
    )
    db.add(arena)
    await db.flush()
    return _to_response(arena)


@router.get("/active", response_model=ArenaResponse | None)
async def get_active_arena(floor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Arena).where(
            Arena.floor_id == floor_id,
            Arena.is_active.is_(True),
        )
    )
    arena = result.scalar_one_or_none()
    if not arena:
        return None
    return _to_response(arena)


@router.get("/{arena_id}", response_model=ArenaResponse)
async def get_arena(
    floor_id: str,
    arena_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Arena).where(Arena.id == arena_id, Arena.floor_id == floor_id))
    arena = result.scalar_one_or_none()
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    return _to_response(arena)


@router.post("/{arena_id}/complete", response_model=ArenaCompleteResponse)
async def complete_arena(
    floor_id: str,
    arena_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Arena).where(Arena.id == arena_id, Arena.floor_id == floor_id))
    arena = result.scalar_one_or_none()
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    if arena.is_complete:
        raise HTTPException(status_code=400, detail="Arena already complete")

    arena.is_active = False
    arena.is_complete = True

    # Update floor
    floor = await db.get(Floor, floor_id)
    if floor:
        floor.arenas_completed += 1

    # Distribute XP and gold to all party characters
    gold_per_player = 0
    xp_award = 0
    leveled_characters: list[dict] = []

    if floor:
        run_result = await db.execute(select(Run).where(Run.id == floor.run_id))
        run = run_result.scalar_one_or_none()
        if run:
            campaign = await db.get(Campaign, run.campaign_id)
            settings = (
                CampaignSettings(**(campaign.settings or {})) if campaign else CampaignSettings()
            )

            char_result = await db.execute(
                select(Character).where(Character.campaign_id == run.campaign_id)
            )
            chars = char_result.scalars().all()
            party_size = len(chars)

            # Compute gold reward
            difficulty = arena.actual_difficulty or "moderate"
            gold_per_player = compute_arena_gold(
                arena.arena_number,
                run.starting_level,
                difficulty,
                gold_multiplier=settings.gold_multiplier,
            )
            arena.gold_earned_per_player = gold_per_player

            # Credit gold to campaign and run
            if campaign and party_size > 0:
                total_gold = gold_per_player * party_size
                campaign.gold_balance += total_gold
                run.total_gold_earned += total_gold

            # Distribute XP
            if chars:
                xp_award = compute_arena_xp_award(
                    arena.adjusted_xp or 0,
                    party_size,
                    leveling_speed=settings.leveling_speed,
                )
                for c in chars:
                    c.xp_total += xp_award
                    while check_level_up(c.level, c.xp_total) and c.level < 20:
                        c.level += 1
                        leveled_characters.append(
                            {
                                "character_id": c.id,
                                "name": c.name,
                                "new_level": c.level,
                            }
                        )

    await db.flush()
    return ArenaCompleteResponse(
        message=f"Arena {arena.arena_number} completed",
        gold_per_player=gold_per_player,
        xp_award=xp_award,
        leveled_characters=leveled_characters,
    )


@router.get(
    "/{arena_id}/creatures",
    response_model=list[ArenaCreatureStatusResponse],
)
async def list_arena_creatures(
    floor_id: str,
    arena_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ArenaCreatureStatus).where(ArenaCreatureStatus.arena_id == arena_id)
    )
    creatures = result.scalars().all()
    return [
        ArenaCreatureStatusResponse(
            id=c.id,
            arena_id=c.arena_id,
            monster_id=c.monster_id,
            instance_label=c.instance_label,
            status=c.status,
            is_reinforcement=c.is_reinforcement,
        )
        for c in creatures
    ]


@router.patch(
    "/{arena_id}/creatures/{creature_id}/status",
    response_model=ArenaCreatureStatusResponse,
)
async def update_creature_status(
    floor_id: str,
    arena_id: str,
    creature_id: str,
    body: CreatureStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a creature's status (alive/bloodied/defeated)."""
    result = await db.execute(
        select(ArenaCreatureStatus).where(
            ArenaCreatureStatus.id == creature_id,
            ArenaCreatureStatus.arena_id == arena_id,
        )
    )
    creature = result.scalar_one_or_none()
    if not creature:
        raise HTTPException(status_code=404, detail="Creature not found")

    creature.status = body.status
    await db.flush()

    return ArenaCreatureStatusResponse(
        id=creature.id,
        arena_id=creature.arena_id,
        monster_id=creature.monster_id,
        instance_label=creature.instance_label,
        status=creature.status,
        is_reinforcement=creature.is_reinforcement,
    )
