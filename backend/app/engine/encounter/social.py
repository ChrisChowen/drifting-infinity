"""Social encounter engine — scheduling and resolution.

Social encounters replace one combat arena per floor.  They use skill
checks instead of initiative and reward creative play beyond fighting.
"""

from dataclasses import dataclass, field

from app.data.social_encounters import (
    SocialEncounterDef,
    compute_social_dc,
    select_social_encounter,
    should_place_social_encounter,
)


@dataclass
class SocialCheckResult:
    skill: str
    dc: int
    roll: int
    modifier: int
    success: bool
    result_text: str


@dataclass
class SocialEncounterResult:
    encounter_id: str
    encounter_name: str
    checks: list[SocialCheckResult]
    successes: int
    total_checks: int
    overall_success: bool          # Majority of checks passed
    rewards: dict = field(default_factory=dict)
    consequences: dict = field(default_factory=dict)
    lore_fragment_id: str | None = None
    dm_prompt: str = ""


def resolve_social_encounter(
    encounter: SocialEncounterDef,
    party_level: int,
    floor_number: int,
    check_results: list[dict] | None = None,
) -> SocialEncounterResult:
    """Resolve a social encounter given check results.

    If check_results is None, this returns the encounter setup (DM prompt,
    DCs) for the frontend to present.  If check_results is provided, it
    processes them and returns rewards/consequences.

    Args:
        encounter: The social encounter definition.
        party_level: Current party level for DC scaling.
        floor_number: Current floor for DC scaling.
        check_results: List of {"skill": str, "roll": int, "modifier": int}
            dicts from the frontend, or None for setup mode.

    Returns:
        SocialEncounterResult with all check outcomes and rewards.
    """
    checks: list[SocialCheckResult] = []
    successes = 0

    for i, skill_check in enumerate(encounter.skill_checks):
        dc = compute_social_dc(skill_check.dc_base, party_level, floor_number)

        if check_results and i < len(check_results):
            cr = check_results[i]
            roll = cr.get("roll", 10)
            modifier = cr.get("modifier", 0)
            total = roll + modifier
            success = total >= dc
            result_text = skill_check.success_text if success else skill_check.failure_text
        else:
            # Setup mode — no results yet
            roll = 0
            modifier = 0
            success = False
            result_text = ""

        if success:
            successes += 1

        checks.append(SocialCheckResult(
            skill=skill_check.skill,
            dc=dc,
            roll=roll,
            modifier=modifier,
            success=success,
            result_text=result_text,
        ))

    total_checks = len(encounter.skill_checks)
    overall_success = successes >= (total_checks + 1) // 2  # Majority

    rewards = dict(encounter.success_rewards) if overall_success else {}
    consequences = dict(encounter.failure_consequences) if not overall_success else {}

    return SocialEncounterResult(
        encounter_id=encounter.id,
        encounter_name=encounter.name,
        checks=checks,
        successes=successes,
        total_checks=total_checks,
        overall_success=overall_success,
        rewards=rewards,
        consequences=consequences,
        lore_fragment_id=encounter.lore_fragment_id if overall_success else None,
        dm_prompt=encounter.dm_prompt,
    )


def generate_social_encounter_for_arena(
    floor_number: int,
    arena_number: int,
    total_arenas: int,
    party_level: int,
    used_social_encounters: list[str] | None = None,
    is_boss_floor: bool = False,
    social_placed_this_floor: bool = False,
) -> SocialEncounterDef | None:
    """Determine if this arena should be social, and if so, which encounter.

    Returns None if this arena should be combat, or a SocialEncounterDef
    if it should be a social encounter.
    """
    if not should_place_social_encounter(
        floor_number=floor_number,
        arena_number=arena_number,
        total_arenas=total_arenas,
        is_boss_floor=is_boss_floor,
        social_placed_this_floor=social_placed_this_floor,
    ):
        return None

    return select_social_encounter(
        floor_number=floor_number,
        used_encounters=used_social_encounters,
    )
