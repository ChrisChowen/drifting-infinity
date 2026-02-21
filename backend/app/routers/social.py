"""Social encounter API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.social_encounters import compute_social_dc, get_social_encounter
from app.database import get_db
from app.engine.encounter.social import (
    generate_social_encounter_for_arena,
    resolve_social_encounter,
)
from app.models.arena import Arena
from app.models.character import Character
from app.models.floor import Floor
from app.models.run import Run

router = APIRouter(prefix="/arenas/{arena_id}/social", tags=["social"])


class SkillCheckSetup(BaseModel):
    skill: str
    dc: int
    success_text: str
    failure_text: str


class SocialEncounterSetupResponse(BaseModel):
    encounter_id: str
    name: str
    description: str
    dm_prompt: str
    skill_checks: list[SkillCheckSetup]
    lore_fragment_id: str | None = None


class CheckResultInput(BaseModel):
    skill: str
    roll: int
    modifier: int


class SkillCheckOutcome(BaseModel):
    skill: str
    dc: int
    roll: int
    modifier: int
    total: int
    success: bool
    result_text: str


class SocialEncounterResolveRequest(BaseModel):
    check_results: list[CheckResultInput]


class SocialEncounterResolveResponse(BaseModel):
    encounter_id: str
    encounter_name: str
    checks: list[SkillCheckOutcome]
    successes: int
    total_checks: int
    overall_success: bool
    rewards: dict
    consequences: dict
    lore_fragment_id: str | None = None


@router.post("/generate", response_model=SocialEncounterSetupResponse | None)
async def generate_social(
    arena_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Check if this arena should be social and return setup data."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")

    floor = await db.get(Floor, arena.floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    run = await db.get(Run, floor.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Check if social already assigned
    if arena.is_social and arena.social_encounter_id:
        enc = get_social_encounter(arena.social_encounter_id)
        if enc:
            party_level = run.starting_level
            chars_result = await db.execute(
                select(Character).where(Character.campaign_id == run.campaign_id)
            )
            chars = chars_result.scalars().all()
            if chars:
                party_level = max(c.level for c in chars)

            return SocialEncounterSetupResponse(
                encounter_id=enc.id,
                name=enc.name,
                description=enc.description,
                dm_prompt=enc.dm_prompt,
                skill_checks=[
                    SkillCheckSetup(
                        skill=sc.skill,
                        dc=compute_social_dc(sc.dc_base, party_level, floor.floor_number),
                        success_text=sc.success_text,
                        failure_text=sc.failure_text,
                    )
                    for sc in enc.skill_checks
                ],
                lore_fragment_id=enc.lore_fragment_id,
            )

    # Check if any socials already placed this floor
    existing_arenas = await db.execute(
        select(Arena).where(Arena.floor_id == floor.id)
    )
    social_placed = any(a.is_social for a in existing_arenas.scalars().all())

    # Determine used social encounters this run
    all_floors = await db.execute(
        select(Floor).where(Floor.run_id == run.id)
    )
    used_social: list[str] = []
    for f in all_floors.scalars().all():
        floor_arenas = await db.execute(
            select(Arena).where(Arena.floor_id == f.id, Arena.is_social.is_(True))
        )
        for a in floor_arenas.scalars().all():
            if a.social_encounter_id:
                used_social.append(a.social_encounter_id)

    is_boss_floor = floor.floor_number in (5, 10, 15, 20)

    # Get party level
    chars_result = await db.execute(
        select(Character).where(Character.campaign_id == run.campaign_id)
    )
    chars = chars_result.scalars().all()
    party_level = max((c.level for c in chars), default=run.starting_level)

    encounter_def = generate_social_encounter_for_arena(
        floor_number=floor.floor_number,
        arena_number=arena.arena_number,
        total_arenas=floor.arena_count,
        party_level=party_level,
        used_social_encounters=used_social,
        is_boss_floor=is_boss_floor,
        social_placed_this_floor=social_placed,
    )

    if not encounter_def:
        return None

    # Mark arena as social
    arena.is_social = True
    arena.social_encounter_id = encounter_def.id
    await db.flush()

    return SocialEncounterSetupResponse(
        encounter_id=encounter_def.id,
        name=encounter_def.name,
        description=encounter_def.description,
        dm_prompt=encounter_def.dm_prompt,
        skill_checks=[
            SkillCheckSetup(
                skill=sc.skill,
                dc=compute_social_dc(sc.dc_base, party_level, floor.floor_number),
                success_text=sc.success_text,
                failure_text=sc.failure_text,
            )
            for sc in encounter_def.skill_checks
        ],
        lore_fragment_id=encounter_def.lore_fragment_id,
    )


@router.post("/resolve", response_model=SocialEncounterResolveResponse)
async def resolve_social(
    arena_id: str,
    body: SocialEncounterResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resolve skill checks and compute outcome."""
    arena = await db.get(Arena, arena_id)
    if not arena:
        raise HTTPException(status_code=404, detail="Arena not found")
    if not arena.is_social or not arena.social_encounter_id:
        raise HTTPException(status_code=400, detail="Not a social encounter")

    encounter_def = get_social_encounter(arena.social_encounter_id)
    if not encounter_def:
        raise HTTPException(status_code=404, detail="Social encounter definition not found")

    floor = await db.get(Floor, arena.floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    run = await db.get(Run, floor.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    chars_result = await db.execute(
        select(Character).where(Character.campaign_id == run.campaign_id)
    )
    chars = chars_result.scalars().all()
    party_level = max((c.level for c in chars), default=run.starting_level)

    check_dicts = [
        {"skill": cr.skill, "roll": cr.roll, "modifier": cr.modifier}
        for cr in body.check_results
    ]

    result = resolve_social_encounter(
        encounter=encounter_def,
        party_level=party_level,
        floor_number=floor.floor_number,
        check_results=check_dicts,
    )

    # Save result on arena
    arena.social_encounter_result = {
        "overall_success": result.overall_success,
        "successes": result.successes,
        "total_checks": result.total_checks,
        "rewards": result.rewards,
        "consequences": result.consequences,
        "lore_fragment_id": result.lore_fragment_id,
    }
    await db.flush()

    return SocialEncounterResolveResponse(
        encounter_id=result.encounter_id,
        encounter_name=result.encounter_name,
        checks=[
            SkillCheckOutcome(
                skill=c.skill,
                dc=c.dc,
                roll=c.roll,
                modifier=c.modifier,
                total=c.roll + c.modifier,
                success=c.success,
                result_text=c.result_text,
            )
            for c in result.checks
        ],
        successes=result.successes,
        total_checks=result.total_checks,
        overall_success=result.overall_success,
        rewards=result.rewards,
        consequences=result.consequences,
        lore_fragment_id=result.lore_fragment_id,
    )
