"""Affix XP Cost Offset (Phase 11D).

Floor affixes buff creatures after selection, making encounters harder
than the XP budget intended. This module estimates the additional
difficulty each affix adds and returns a negative offset to reduce
the XP budget proportionally.

For example, if active affixes add +16% effective difficulty, the
budget is reduced by 16% so the final encounter is at the intended level.
"""

# Affix ID → estimated difficulty increase percentage (positive = harder)
AFFIX_XP_COST: dict[str, float] = {
    # Creature buffs
    "fortified": 0.08,       # +10% HP
    "armored": 0.08,         # +1 AC
    "emboldened": 0.06,      # +1 attack
    "empowered": 0.04,       # +1 damage
    "regenerating": 0.05,    # 2 HP regen/turn
    "quickened": 0.02,       # +10 speed
    "resolute": 0.03,        # Save advantage vs condition
    "relentless": 0.06,      # Fight at 0 HP for 1 round
    "spellguard": 0.05,      # Advantage on spell saves
    "pack_tactics": 0.07,    # Advantage on attacks near allies

    # Environment (affect both sides but creatures are designed for them)
    "dim_light": 0.03,
    "difficult_terrain": 0.02,
    "hazard_zones": 0.04,
    "antimagic_pockets": 0.05,
    "wind_tunnels": 0.03,
    "shifting_walls": 0.03,
    "magical_darkness": 0.05,
    "gravity_wells": 0.03,
    "temporal_flux": 0.02,
    "ley_line_surges": 0.02,

    # Armillary (may help or hurt; net effect is slightly harder)
    "volatile_favour": 0.04,
    "hyperactive": 0.03,
    "favour_drain": 0.02,
    "empowered_effects": 0.04,
    "cascading_effects": 0.03,
    "armillary_wrath": 0.06,
    "armillary_mercy": -0.03,  # Beneficial — slightly easier

    # Economy (no combat impact)
    "golden_floor": 0.0,
    "shard_resonance": 0.0,
    "merchant_favour": 0.0,
    "merchant_markup": 0.0,
    "bounty_hunter": 0.0,
    "treasure_trove": 0.0,
    "xp_bounty": 0.0,
}


def compute_affix_difficulty_offset(active_affix_ids: list[str]) -> float:
    """Compute the XP budget offset from active floor affixes.

    Returns a negative float (e.g., -0.16) indicating the budget should
    be reduced by that percentage. Capped at -0.30 to prevent encounters
    from becoming trivially easy.
    """
    total = 0.0
    for affix_id in active_affix_ids:
        total += AFFIX_XP_COST.get(affix_id, 0.0)

    # Negate: affixes add difficulty, so we REDUCE the budget
    offset = -total

    # Clamp: don't reduce more than 30%
    return max(-0.30, offset)
