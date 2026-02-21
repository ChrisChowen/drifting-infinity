"""Combo interaction multipliers per GDD 4.5.

Certain creature combinations are synergistic and have their adjusted XP modified.
"""

from dataclasses import dataclass


@dataclass
class ComboResult:
    combo_name: str
    description: str
    xp_multiplier: float
    triggering_roles: list[str]


COMBO_DEFINITIONS: list[ComboResult] = [
    ComboResult(
        combo_name="Shield Wall",
        description="Multiple soldiers form an impenetrable front line.",
        xp_multiplier=1.15,
        triggering_roles=["soldier", "soldier"],
    ),
    ComboResult(
        combo_name="Hammer and Anvil",
        description="Brutes smash while soldiers hold the line.",
        xp_multiplier=1.1,
        triggering_roles=["brute", "soldier"],
    ),
    ComboResult(
        combo_name="Artillery Battery",
        description="Multiple ranged attackers focus fire from distance.",
        xp_multiplier=1.2,
        triggering_roles=["artillery", "artillery"],
    ),
    ComboResult(
        combo_name="Lockdown",
        description="Controllers restrict movement while others deal damage.",
        xp_multiplier=1.15,
        triggering_roles=["controller", "brute"],
    ),
    ComboResult(
        combo_name="Ambush Pincer",
        description="Lurkers and skirmishers attack from multiple angles.",
        xp_multiplier=1.15,
        triggering_roles=["lurker", "skirmisher"],
    ),
    ComboResult(
        combo_name="Suppression Fire",
        description="Artillery pins down while controllers zone.",
        xp_multiplier=1.15,
        triggering_roles=["artillery", "controller"],
    ),
    ComboResult(
        combo_name="Pack Hunters",
        description="Skirmishers surround and overwhelm isolated targets.",
        xp_multiplier=1.1,
        triggering_roles=["skirmisher", "skirmisher"],
    ),
    ComboResult(
        combo_name="Shadow Strike",
        description="Lurkers strike from stealth while controller disables.",
        xp_multiplier=1.2,
        triggering_roles=["lurker", "controller"],
    ),
    ComboResult(
        combo_name="Brute Force",
        description="Multiple brutes overwhelm through sheer damage.",
        xp_multiplier=1.1,
        triggering_roles=["brute", "brute"],
    ),
]


def detect_combos(encounter_roles: list[str]) -> list[ComboResult]:
    """Detect which combos are present in an encounter."""
    active_combos = []
    role_counts = {}
    for r in encounter_roles:
        role_counts[r] = role_counts.get(r, 0) + 1

    for combo in COMBO_DEFINITIONS:
        # Check if the combo's triggering roles are present
        needed = {}
        for role in combo.triggering_roles:
            needed[role] = needed.get(role, 0) + 1

        all_met = True
        for role, count in needed.items():
            if role_counts.get(role, 0) < count:
                all_met = False
                break

        if all_met:
            active_combos.append(combo)

    return active_combos


def compute_combo_multiplier(combos: list[ComboResult]) -> float:
    """Compute the combined XP multiplier from active combos.

    Combos stack multiplicatively but are capped.
    """
    if not combos:
        return 1.0

    combined = 1.0
    for combo in combos:
        combined *= combo.xp_multiplier

    # Cap at 1.5x
    return min(1.5, combined)
