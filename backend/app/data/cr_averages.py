"""Average HP, AC, and DPR by CR for role classification baseline comparisons."""

# Based on DMG Monster Statistics by CR table
# {cr: {"hp": avg_hp, "ac": avg_ac, "dpr": avg_damage_per_round, "attack_bonus": avg, "save_dc": avg}}
CR_AVERAGES: dict[float, dict[str, float]] = {
    0:     {"hp": 3,   "ac": 12, "dpr": 1,   "attack_bonus": 2, "save_dc": 10},
    0.125: {"hp": 7,   "ac": 13, "dpr": 3,   "attack_bonus": 3, "save_dc": 10},
    0.25:  {"hp": 14,  "ac": 13, "dpr": 5,   "attack_bonus": 3, "save_dc": 10},
    0.5:   {"hp": 21,  "ac": 13, "dpr": 8,   "attack_bonus": 3, "save_dc": 11},
    1:     {"hp": 33,  "ac": 13, "dpr": 12,  "attack_bonus": 3, "save_dc": 11},
    2:     {"hp": 51,  "ac": 13, "dpr": 17,  "attack_bonus": 3, "save_dc": 12},
    3:     {"hp": 66,  "ac": 13, "dpr": 23,  "attack_bonus": 4, "save_dc": 12},
    4:     {"hp": 80,  "ac": 14, "dpr": 29,  "attack_bonus": 5, "save_dc": 13},
    5:     {"hp": 95,  "ac": 15, "dpr": 35,  "attack_bonus": 6, "save_dc": 13},
    6:     {"hp": 110, "ac": 15, "dpr": 41,  "attack_bonus": 6, "save_dc": 14},
    7:     {"hp": 125, "ac": 15, "dpr": 47,  "attack_bonus": 6, "save_dc": 14},
    8:     {"hp": 140, "ac": 16, "dpr": 53,  "attack_bonus": 7, "save_dc": 15},
    9:     {"hp": 155, "ac": 16, "dpr": 59,  "attack_bonus": 7, "save_dc": 15},
    10:    {"hp": 170, "ac": 17, "dpr": 65,  "attack_bonus": 7, "save_dc": 16},
    11:    {"hp": 185, "ac": 17, "dpr": 71,  "attack_bonus": 8, "save_dc": 16},
    12:    {"hp": 200, "ac": 17, "dpr": 77,  "attack_bonus": 8, "save_dc": 17},
    13:    {"hp": 215, "ac": 18, "dpr": 83,  "attack_bonus": 8, "save_dc": 17},
    14:    {"hp": 230, "ac": 18, "dpr": 89,  "attack_bonus": 8, "save_dc": 18},
    15:    {"hp": 245, "ac": 18, "dpr": 95,  "attack_bonus": 8, "save_dc": 18},
    16:    {"hp": 260, "ac": 18, "dpr": 101, "attack_bonus": 9, "save_dc": 18},
    17:    {"hp": 275, "ac": 19, "dpr": 107, "attack_bonus": 10, "save_dc": 19},
    18:    {"hp": 290, "ac": 19, "dpr": 113, "attack_bonus": 10, "save_dc": 19},
    19:    {"hp": 305, "ac": 19, "dpr": 119, "attack_bonus": 10, "save_dc": 19},
    20:    {"hp": 320, "ac": 19, "dpr": 125, "attack_bonus": 10, "save_dc": 19},
    21:    {"hp": 370, "ac": 19, "dpr": 131, "attack_bonus": 11, "save_dc": 20},
    22:    {"hp": 400, "ac": 19, "dpr": 137, "attack_bonus": 11, "save_dc": 20},
    23:    {"hp": 430, "ac": 19, "dpr": 143, "attack_bonus": 11, "save_dc": 20},
    24:    {"hp": 460, "ac": 19, "dpr": 149, "attack_bonus": 12, "save_dc": 21},
    25:    {"hp": 490, "ac": 19, "dpr": 155, "attack_bonus": 12, "save_dc": 21},
    26:    {"hp": 520, "ac": 19, "dpr": 161, "attack_bonus": 12, "save_dc": 21},
    27:    {"hp": 550, "ac": 19, "dpr": 167, "attack_bonus": 13, "save_dc": 22},
    28:    {"hp": 580, "ac": 19, "dpr": 173, "attack_bonus": 13, "save_dc": 22},
    29:    {"hp": 610, "ac": 19, "dpr": 179, "attack_bonus": 13, "save_dc": 22},
    30:    {"hp": 640, "ac": 19, "dpr": 185, "attack_bonus": 14, "save_dc": 23},
}


def get_cr_average_hp(cr: float) -> float:
    """Get average HP for a given CR."""
    nearest = min(CR_AVERAGES.keys(), key=lambda k: abs(k - cr))
    return CR_AVERAGES[nearest]["hp"]


def get_cr_average_ac(cr: float) -> float:
    """Get average AC for a given CR."""
    nearest = min(CR_AVERAGES.keys(), key=lambda k: abs(k - cr))
    return CR_AVERAGES[nearest]["ac"]


def get_cr_average_dpr(cr: float) -> float:
    """Get average DPR for a given CR."""
    nearest = min(CR_AVERAGES.keys(), key=lambda k: abs(k - cr))
    return CR_AVERAGES[nearest]["dpr"]
