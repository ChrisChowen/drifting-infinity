"""Build MechanicalSignature from statblock JSON. Per GDD 4.3-4.4."""

import re


def build_mechanical_signature(statblock: dict, cr: float) -> dict:
    """Construct a MechanicalSignature dict from a parsed statblock."""
    actions = statblock.get("actions", [])
    special = statblock.get("special_abilities", [])
    abilities = statblock.get("abilities", {})
    saves = statblock.get("saves", {})

    all_text = _get_all_text(statblock)

    # Damage profile
    damage_output = _compute_damage_output(actions, all_text)

    # Effective HP
    effective_hp = _compute_effective_hp(statblock, cr)

    # Save difficulty
    save_difficulty = _compute_save_difficulty(saves, statblock)

    # Threat flags
    threat_flags = _detect_threat_flags(all_text, statblock)

    # Danger by tier
    danger_by_tier = _assess_danger_by_tier(cr, threat_flags)

    # Party warnings
    party_warnings = _compute_party_warnings(threat_flags, statblock)

    # Exploit profile
    exploit_profile = _compute_exploit_profile(statblock, saves)

    return {
        "damage_output": damage_output,
        "effective_hp": effective_hp,
        "save_difficulty": save_difficulty,
        "threat_flags": threat_flags,
        "danger_by_tier": danger_by_tier,
        "party_warnings": party_warnings,
        "exploit_profile": exploit_profile,
    }


def _get_all_text(statblock: dict) -> str:
    """Concatenate all text from actions, abilities, etc."""
    parts = []
    for key in ["actions", "special_abilities", "legendary_actions", "reactions"]:
        for item in statblock.get(key, []):
            parts.append(item.get("desc", ""))
            parts.append(item.get("name", ""))
    return " ".join(parts).lower()


def _compute_damage_output(actions: list[dict], all_text: str) -> dict:
    """Estimate DPR from action descriptions."""
    damage_rolls = []
    damage_types = set()
    requires_recharge = False

    for action in actions:
        desc = action.get("desc", "")

        # Find damage dice patterns like "11 (2d8 + 2) slashing damage"
        hits = re.findall(r"(\d+)\s*\((\d+d\d+(?:\s*[+-]\s*\d+)?)\)\s+(\w+)\s+damage", desc)
        for avg_str, dice, dmg_type in hits:
            damage_rolls.append({"average": int(avg_str), "dice": dice, "type": dmg_type})
            damage_types.add(dmg_type)

        if "recharge" in desc.lower():
            requires_recharge = True

    # Compute DPR: if multiattack exists, use sum of attack damages
    multiattack_count = 1
    for action in actions:
        if action.get("name", "").lower() == "multiattack":
            # Try to find "makes X attacks" pattern
            desc = action.get("desc", "")
            match = re.search(r"makes (\w+)", desc.lower())
            if match:
                word = match.group(1)
                word_to_num = {"two": 2, "three": 3, "four": 4, "five": 5, "2": 2, "3": 3, "4": 4}
                multiattack_count = word_to_num.get(word, 2)
            break

    per_round_avg = 0
    per_round_max = 0
    spike = 0

    if damage_rolls:
        # Use the highest damage action for multiattack estimation
        best_avg = max(d["average"] for d in damage_rolls)
        per_round_avg = int(best_avg * multiattack_count * 0.65)  # 65% hit rate
        per_round_max = int(best_avg * multiattack_count)
        spike = max(d["average"] for d in damage_rolls) * 2  # Crit approximation

    return {
        "per_round_average": per_round_avg,
        "per_round_max": per_round_max,
        "spike_potential": spike,
        "damage_types": list(damage_types),
        "requires_recharge": requires_recharge,
    }


def _compute_effective_hp(statblock: dict, cr: float) -> float:
    """Compute effective HP adjusted for resistances and regeneration."""
    # Base HP isn't in statblock directly (it's on the Monster model),
    # so we estimate from hit dice if available, or use CR average
    from app.data.cr_averages import get_cr_average_hp
    base_hp = get_cr_average_hp(cr)

    all_text = _get_all_text(statblock)
    resistances = statblock.get("damage_resistances", "")
    immunities = statblock.get("damage_immunities", "")

    multiplier = 1.0
    if resistances:
        # Common resistances at Tier 1 multiply by 1.5, Tier 2+ by 1.25
        multiplier += 0.25 if cr >= 5 else 0.5
    if immunities:
        multiplier += 0.25

    # Regeneration
    if "regenerat" in all_text:
        regen_match = re.search(r"regains (\d+) hit points", all_text)
        if regen_match:
            regen = int(regen_match.group(1))
            base_hp += regen * 4  # Amortize over 4 rounds

    return base_hp * multiplier


def _compute_save_difficulty(saves: dict[str, int], statblock: dict) -> dict:
    """Categorize saves into strong/weak."""
    strong = [k for k, v in saves.items() if v >= 3]
    weak = [k for k, v in saves.items() if v < 0]

    condition_immunities = statblock.get("condition_immunities", "")
    ci_list = [c.strip() for c in condition_immunities.split(",")] if condition_immunities else []

    all_text = _get_all_text(statblock)
    magic_resistance = "magic resistance" in all_text or "advantage on saving throws against spells" in all_text

    return {
        "strong_saves": strong,
        "weak_saves": weak,
        "condition_immunities": ci_list,
        "magic_resistance": magic_resistance,
    }


def _detect_threat_flags(all_text: str, statblock: dict) -> dict:
    """Detect threat flags from statblock text. Per GDD 4.4."""
    flags = {
        "save_or_die": False,
        "save_or_incapacitate": False,
        "permanent_drain": False,
        "action_denial": False,
        "healing_prevention": False,
        "forced_movement": False,
        "summon_or_split": False,
        "aoe_damage": False,
        "aoe_control": False,
        "stealth_ambush": False,
        "flight_only": False,
        "counterspell_or_dispel": False,
        "charm_or_dominate": False,
        "swarm_scaling": False,
        "equipment_destruction": False,
        "pack_tactics": False,
        "grapple_capable": False,
        "creates_darkness": False,
        "has_blindsight_or_devilsight": False,
        "high_single_hit_damage": False,
        "imposes_restrained": False,
        "imposes_frightened": False,
    }

    # Save or die
    if re.search(r"(drops to 0 hit points|the target dies|reduced to 0 hit points).*saving throw", all_text) or \
       re.search(r"saving throw.*(?:drops to 0|the target dies|reduced to 0)", all_text):
        flags["save_or_die"] = True

    # Save or incapacitate
    if re.search(r"saving throw.*(paralyzed|stunned|petrified|unconscious)", all_text) or \
       re.search(r"(paralyzed|stunned|petrified|unconscious).*saving throw", all_text):
        flags["save_or_incapacitate"] = True

    # Permanent drain
    if re.search(r"reduces?.*(maximum hit points|strength score|hit point maximum)", all_text):
        flags["permanent_drain"] = True

    # Action denial
    if any(word in all_text for word in ["stunned", "paralyzed", "incapacitated", "petrified"]):
        flags["action_denial"] = True

    # Healing prevention
    if re.search(r"can'?t regain hit points|prevents?.* healing", all_text):
        flags["healing_prevention"] = True

    # Forced movement
    if re.search(r"push(?:ed)?.* (?:\d+ feet|away)|pull(?:ed)?.* (?:\d+ feet|toward)|knocked (?:prone|back)", all_text):
        flags["forced_movement"] = True

    # Summon or split
    if re.search(r"summon|conjure|splits? into|divides? into", all_text):
        flags["summon_or_split"] = True

    # AoE damage
    if re.search(r"each creature (?:in|within)", all_text):
        flags["aoe_damage"] = True

    # AoE control
    if re.search(r"difficult terrain|(?:each creature|all creatures).*(restrained|frightened|prone)", all_text):
        flags["aoe_control"] = True

    # Stealth ambush
    skills = statblock.get("skills", {})
    stealth_val = skills.get("stealth", 0) if isinstance(skills, dict) else 0
    if stealth_val >= 6 or "invisible" in all_text or "invisibility" in all_text:
        flags["stealth_ambush"] = True

    # Flight only
    speed = statblock.get("speed", {})
    if isinstance(speed, dict):
        has_fly = bool(speed.get("fly"))
        walk_str = str(speed.get("walk", "30"))
        walk_speed = 0
        try:
            walk_speed = int(walk_str.replace(" ft.", "").replace("ft", "").strip() or "0")
        except ValueError:
            pass
        if has_fly and walk_speed == 0:
            flags["flight_only"] = True

    # Counterspell or dispel
    if "counterspell" in all_text or "dispel magic" in all_text:
        flags["counterspell_or_dispel"] = True

    # Charm or dominate
    if re.search(r"charm(?:ed)?|dominate", all_text):
        flags["charm_or_dominate"] = True

    # Swarm
    if "swarm" in all_text:
        flags["swarm_scaling"] = True

    # Equipment destruction
    if re.search(r"corrodes|dissolves|destroys.*nonmagical", all_text):
        flags["equipment_destruction"] = True

    # Pack tactics
    if "pack tactics" in all_text:
        flags["pack_tactics"] = True

    # Grapple capable
    if "grappled" in all_text or "grapple" in all_text:
        flags["grapple_capable"] = True

    # Creates darkness
    if "darkness" in all_text and ("cast" in all_text or "magical darkness" in all_text):
        flags["creates_darkness"] = True

    # Blindsight or Devil's Sight
    senses = statblock.get("senses", "")
    if "blindsight" in senses.lower() or "devil" in all_text:
        flags["has_blindsight_or_devilsight"] = True

    # Restrained
    if "restrained" in all_text:
        flags["imposes_restrained"] = True

    # Frightened
    if "frightened" in all_text:
        flags["imposes_frightened"] = True

    return flags


def _assess_danger_by_tier(cr: float, threat_flags: dict) -> dict:
    """Assess danger level per tier of play."""
    threat_count = sum(1 for v in threat_flags.values() if v)

    def assess(tier_min_cr: float, tier_max_cr: float) -> str:
        if cr < tier_min_cr * 0.25:
            return "trivial"
        if threat_flags.get("save_or_die"):
            if cr <= tier_min_cr:
                return "banned" if tier_min_cr <= 4 else "lethal"
            return "lethal"
        if threat_count >= 3 and cr >= tier_max_cr * 0.5:
            return "dangerous"
        if cr > tier_max_cr:
            return "lethal"
        return "standard"

    return {
        "tier1": assess(1, 4),
        "tier2": assess(5, 10),
        "tier3": assess(11, 16),
        "tier4": assess(17, 20),
    }


def _compute_party_warnings(threat_flags: dict, statblock: dict) -> dict:
    """Compute party composition warnings."""
    dangerous_if_no: list[str] = []
    trivialised_by: list[str] = []
    hard_counters: list[str] = []

    if threat_flags.get("flight_only"):
        dangerous_if_no.append("ranged_damage")

    if threat_flags.get("permanent_drain"):
        dangerous_if_no.append("condition_removal")

    if threat_flags.get("charm_or_dominate"):
        dangerous_if_no.append("high_wis_saves")

    resistances = statblock.get("damage_resistances", "").lower()
    immunities = statblock.get("damage_immunities", "").lower()

    if "fire" in immunities:
        trivialised_by.append("non_fire_damage")

    if threat_flags.get("save_or_die"):
        hard_counters.append("low_con_saves")

    if threat_flags.get("save_or_incapacitate"):
        hard_counters.append("low_wis_saves")

    return {
        "dangerous_if_no": dangerous_if_no,
        "trivialised_by": trivialised_by,
        "hard_counters": hard_counters,
    }


def _compute_exploit_profile(statblock: dict, saves: dict[str, int]) -> dict:
    """Compute Weakness Exploit data."""
    vulnerabilities = []
    vuln_str = statblock.get("damage_vulnerabilities", "")
    if vuln_str:
        vulnerabilities = [v.strip().lower() for v in vuln_str.split(",") if v.strip()]

    weak_saves = [
        {"ability": k, "modifier": v}
        for k, v in saves.items()
        if v < 0
    ]

    # Resistance gaps: common damage types NOT resisted or immune
    resistances = statblock.get("damage_resistances", "").lower()
    immunities = statblock.get("damage_immunities", "").lower()
    all_covered = resistances + " " + immunities
    common_types = ["fire", "cold", "lightning", "thunder", "acid", "poison",
                    "radiant", "necrotic", "force", "psychic"]
    gaps = [t for t in common_types if t not in all_covered]

    return {
        "vulnerabilities": vulnerabilities,
        "weak_saves": weak_saves,
        "resistance_gaps": gaps,
    }
