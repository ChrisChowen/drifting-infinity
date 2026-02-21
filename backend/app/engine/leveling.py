"""Character leveling engine for roguelike pace.

XP thresholds are tuned so that a party doing ~5 arenas per floor
reaches level 20 by approximately floor 18-20. The power_xp_bonus
system rewards parties that acquire gacha items and buffs with
faster leveling, reflecting their increased combat effectiveness.
"""

# XP thresholds tuned for roguelike pace (level 20 by floor 18-20).
# Target: complete 20 floors, reach level 20.
# DMG encounter XP scales exponentially by tier, so thresholds must track
# the actual per-floor XP yields at each level. Each threshold ≈ 1.1× the
# expected XP from a single floor at that party level, so that base pace
# is ~1 level per floor. The power_xp_bonus (up to 1.5×) speeds this up
# for parties with gacha items and floor completion bonuses.
XP_TO_LEVEL: dict[int, int] = {
    1: 75,       # 1 -> 2   (tier 1: ~1 floor per level, hook players fast)
    2: 175,      # 2 -> 3
    3: 350,      # 3 -> 4
    4: 550,      # 4 -> 5
    5: 1800,     # 5 -> 6   (tier 2: encounter XP jumps with DMG thresholds)
    6: 2250,     # 6 -> 7
    7: 3200,     # 7 -> 8
    8: 4000,     # 8 -> 9
    9: 4500,     # 9 -> 10
    10: 5500,    # 10 -> 11
    11: 8000,    # 11 -> 12  (tier 3: bigger encounters)
    12: 10000,   # 12 -> 13
    13: 12000,   # 13 -> 14
    14: 14000,   # 14 -> 15
    15: 16500,   # 15 -> 16
    16: 20000,   # 16 -> 17
    17: 25000,   # 17 -> 18  (tier 4: final push)
    18: 32000,   # 18 -> 19
    19: 40000,   # 19 -> 20
    20: 0,       # Max level
}


def xp_to_next_level(level: int) -> int:
    """Return XP needed to reach the next level from current level."""
    return XP_TO_LEVEL.get(level, 0)


def compute_arena_xp_award(arena_raw_xp: int, party_size: int, leveling_speed: float = 1.0) -> int:
    """Compute per-character XP award from an arena.

    Uses raw XP (not encounter-multiplier-adjusted XP) per 2024 DMG:
    the encounter multiplier affects budget calculation only, not awards.
    """
    if party_size <= 0:
        return 0
    base = arena_raw_xp // party_size
    return max(1, int(base * leveling_speed))


def compute_power_xp_bonus(
    gacha_items_owned: int = 0,
    floors_completed: int = 0,
) -> float:
    """Compute leveling speed multiplier from accumulated party power.

    Parties that gain more items and clear more floors level faster,
    reflecting their increased combat effectiveness drawing tougher
    encounters that yield more XP.

    Returns a leveling_speed multiplier (1.0 = base, capped at 1.5).
    """
    bonus = 1.0
    bonus += gacha_items_owned * 0.05
    bonus += floors_completed * 0.02
    return min(1.5, bonus)


def check_level_up(level: int, xp_total: int) -> bool:
    """Check if character has enough XP to level up."""
    if level >= 20:
        return False
    required = xp_to_next_level(level)
    return required > 0 and xp_total >= required


def compute_xp_progress(level: int, xp_total: int) -> dict:
    """Return XP progress info for display."""
    required = xp_to_next_level(level)
    if required == 0:
        return {"current": xp_total, "required": 0, "percentage": 100.0, "can_level_up": False}
    pct = min(100.0, (xp_total / required) * 100)
    return {
        "current": xp_total,
        "required": required,
        "percentage": round(pct, 1),
        "can_level_up": xp_total >= required,
    }
