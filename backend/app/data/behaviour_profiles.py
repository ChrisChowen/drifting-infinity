"""Default behaviour profile templates per tactical role. Per GDD 4.5."""


# Default profiles per role
DEFAULT_PROFILES: dict[str, dict] = {
    "brute": {
        "positioning": "frontline",
        "target_priority": "nearest",
        "retreat_threshold": 0.25,
        "ability_priority": ["multiattack", "melee_attack"],
        "group_tactics": None,
    },
    "soldier": {
        "positioning": "frontline",
        "target_priority": "highest_threat",
        "retreat_threshold": 0.3,
        "ability_priority": ["defensive", "melee_attack", "leadership"],
        "group_tactics": "shield_wall",
    },
    "artillery": {
        "positioning": "backline",
        "target_priority": "caster",
        "retreat_threshold": 0.5,
        "ability_priority": ["ranged_attack", "spell"],
        "group_tactics": "focus_fire",
    },
    "controller": {
        "positioning": "backline",
        "target_priority": "highest_threat",
        "retreat_threshold": 0.4,
        "ability_priority": ["area_denial", "debuff", "ranged_attack"],
        "group_tactics": None,
    },
    "skirmisher": {
        "positioning": "mobile",
        "target_priority": "lowest_hp",
        "retreat_threshold": 0.5,
        "ability_priority": ["hit_and_run", "melee_attack", "disengage"],
        "group_tactics": "harass",
    },
    "lurker": {
        "positioning": "hidden",
        "target_priority": "highest_value",
        "retreat_threshold": 0.3,
        "ability_priority": ["ambush", "stealth", "melee_attack"],
        "group_tactics": "pincer",
    },
}

# Intelligence tier modifiers
INTELLIGENCE_MODIFIERS: dict[str, dict] = {
    "mindless": {
        "target_priority": "nearest",
        "retreat_threshold": 0.0,
        "group_tactics": None,
    },
    "instinctual": {
        "target_priority_options": ["nearest", "lowest_hp"],
        "group_tactics": None,
    },
    "cunning": {},  # Full profile, no modifications
    "mastermind": {
        "target_priority": "adaptive",
        "group_tactics_override": "tactical_withdrawal",
    },
}


def build_behaviour_profile(role: str, statblock: dict, intelligence_tier: str) -> dict:
    """Build a behaviour profile for a creature based on role and intelligence."""
    base = dict(DEFAULT_PROFILES.get(role, DEFAULT_PROFILES["brute"]))
    base["role"] = role

    # Apply intelligence modifications
    intel_mod = INTELLIGENCE_MODIFIERS.get(intelligence_tier, {})

    if "target_priority" in intel_mod:
        base["target_priority"] = intel_mod["target_priority"]

    if "retreat_threshold" in intel_mod:
        base["retreat_threshold"] = intel_mod["retreat_threshold"]

    if "group_tactics" in intel_mod:
        base["group_tactics"] = intel_mod["group_tactics"]
    elif "group_tactics_override" in intel_mod:
        base["group_tactics"] = intel_mod["group_tactics_override"]

    return base
