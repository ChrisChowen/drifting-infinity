"""Greedy budget-filling encounter selection."""

import random
from dataclasses import dataclass, field

from app.data.encounter_multipliers import get_encounter_multiplier
from app.data.xp_thresholds import cr_to_xp
from app.engine.encounter.candidate_pool import MonsterCandidate


@dataclass
class SelectedCreature:
    """A creature selected for the encounter with count."""

    monster_id: str
    name: str
    cr: float
    xp: int
    hp: int
    ac: int
    tactical_role: str
    count: int
    is_empowered_boss: bool = False
    creature_type: str = ""
    vulnerabilities: list[str] = field(default_factory=list)
    weak_saves: list[str] = field(default_factory=list)


@dataclass
class EncounterSelection:
    """Result of the selection process."""

    creatures: list[SelectedCreature] = field(default_factory=list)
    total_raw_xp: int = 0
    adjusted_xp: int = 0
    creature_count: int = 0
    encounter_multiplier: float = 1.0


def select_creatures(
    candidates: list[MonsterCandidate],
    xp_budget: int,
    template_name: str,
    min_creatures: int,
    max_creatures: int,
    preferred_spread: str,
    party_size_category: str = "standard",
    scored_candidates: list[tuple[MonsterCandidate, float]] | None = None,
) -> EncounterSelection:
    """Greedy selection: pick creatures that fit the XP budget.

    Uses scored_candidates if provided (sorted best-first), otherwise uses candidates directly.
    """
    if not candidates:
        return EncounterSelection()

    # Sort by score (best first) if scored
    if scored_candidates:
        sorted_candidates = [c for c, _ in sorted(scored_candidates, key=lambda x: -x[1])]
    else:
        sorted_candidates = list(candidates)
        random.shuffle(sorted_candidates)

    selection: dict[str, tuple[MonsterCandidate, int]] = {}  # monster_id -> (candidate, count)
    empowered_boss_id: str | None = None
    total_raw_xp = 0

    if preferred_spread == "boss_plus_minions":
        # For boss encounters: pick the highest CR creature as boss, fill rest with low CR
        boss_candidates = sorted(sorted_candidates, key=lambda c: -c.cr)
        boss_selected = False
        if boss_candidates:
            # Try highest CR first; fall back to highest that fits the budget
            boss = None
            for candidate in boss_candidates:
                candidate_xp = candidate.xp or cr_to_xp(candidate.cr)
                if candidate_xp <= xp_budget:
                    boss = candidate
                    break

            if boss is not None:
                boss_xp = boss.xp or cr_to_xp(boss.cr)
                # Flag as empowered if this isn't the highest-CR candidate (had to fall back)
                if boss is not boss_candidates[0]:
                    empowered_boss_id = boss.id
                selection[boss.id] = (boss, 1)
                total_raw_xp = boss_xp
                boss_selected = True

                # Fill remaining budget with minions
                # Allow minions up to half boss CR, but always allow CR 1 or lower
                remaining = xp_budget - _compute_adjusted(total_raw_xp, 1, party_size_category)
                minion_cr_cap = max(boss.cr / 2, 1.0)
                minion_candidates = [
                    c for c in sorted_candidates if c.cr <= minion_cr_cap and c.id != boss.id
                ]
                _fill_budget(
                    minion_candidates, remaining, selection, max_creatures - 1, party_size_category
                )

        # Fallback: if boss_plus_minions produced nothing, use standard greedy fill
        if not boss_selected or not selection:
            selection.clear()
            _fill_budget(
                sorted_candidates, xp_budget, selection, max_creatures, party_size_category
            )
    else:
        # Standard greedy fill
        _fill_budget(sorted_candidates, xp_budget, selection, max_creatures, party_size_category)

    # Build result
    creatures = []
    total_raw_xp = 0
    total_count = 0

    for monster_id, (candidate, count) in selection.items():
        xp_each = candidate.xp or cr_to_xp(candidate.cr)
        creatures.append(
            SelectedCreature(
                monster_id=candidate.id,
                name=candidate.name,
                cr=candidate.cr,
                xp=xp_each,
                hp=candidate.hp,
                ac=candidate.ac,
                tactical_role=candidate.tactical_role,
                count=count,
                is_empowered_boss=monster_id == empowered_boss_id,
                creature_type=candidate.creature_type,
                vulnerabilities=candidate.vulnerabilities,
                weak_saves=candidate.weak_saves,
            )
        )
        total_raw_xp += xp_each * count
        total_count += count

    multiplier = get_encounter_multiplier(total_count, party_size_category)
    adjusted_xp = int(total_raw_xp * multiplier)

    return EncounterSelection(
        creatures=creatures,
        total_raw_xp=total_raw_xp,
        adjusted_xp=adjusted_xp,
        creature_count=total_count,
        encounter_multiplier=multiplier,
    )


def _fill_budget(
    candidates: list[MonsterCandidate],
    budget: int,
    selection: dict[str, tuple[MonsterCandidate, int]],
    max_creatures: int,
    party_size_category: str,
) -> None:
    """Greedy fill: add creatures until budget is met or exceeded."""
    current_count = sum(count for _, count in selection.values())
    current_raw_xp = sum((c.xp or cr_to_xp(c.cr)) * count for c, count in selection.values())

    for candidate in candidates:
        if current_count >= max_creatures:
            break

        xp_each = candidate.xp or cr_to_xp(candidate.cr)
        if xp_each <= 0:
            continue

        # How many can we add?
        while current_count < max_creatures:
            test_raw = current_raw_xp + xp_each
            test_count = current_count + 1
            test_adjusted = _compute_adjusted(test_raw, test_count, party_size_category)

            if test_adjusted > budget * 1.15:  # Allow 15% overshoot
                break

            # Add one more
            if candidate.id in selection:
                old_candidate, old_count = selection[candidate.id]
                selection[candidate.id] = (old_candidate, old_count + 1)
            else:
                selection[candidate.id] = (candidate, 1)

            current_raw_xp = test_raw
            current_count = test_count

            # Don't stack too many of the same creature (max 4 of one type)
            if selection[candidate.id][1] >= 4:
                break


def _compute_adjusted(raw_xp: int, count: int, party_size_category: str) -> int:
    """Compute adjusted XP from raw XP and creature count."""
    multiplier = get_encounter_multiplier(count, party_size_category)
    return int(raw_xp * multiplier)
