"""Tactical role assignment from statblock analysis. Per GDD 4.2."""

import re

from app.data.cr_averages import get_cr_average_ac, get_cr_average_hp

ROLES = ["brute", "soldier", "artillery", "controller", "skirmisher", "lurker"]


def classify_tactical_role(statblock: dict, cr: float) -> tuple[str, str | None]:
    """Assign primary and optional secondary tactical role from statblock data."""
    scores: dict[str, float] = {role: 0.0 for role in ROLES}
    abilities = statblock.get("abilities", {})
    actions = statblock.get("actions", [])
    special = statblock.get("special_abilities", [])
    speed_data = statblock.get("speed", {})

    hp = sum(1 for _ in [])  # placeholder - we get HP from model
    # Estimate HP from hit dice if available in actions context
    avg_hp = get_cr_average_hp(cr)
    avg_ac = get_cr_average_ac(cr)

    # Actual HP/AC from the statblock's parent model isn't available here directly,
    # so we work with abilities and action analysis

    # Strength-based: likely brute
    str_score = abilities.get("str", 10)
    if str_score >= 16:
        scores["brute"] += 2
    if str_score >= 20:
        scores["brute"] += 2

    # High CON: brute or soldier
    con_score = abilities.get("con", 10)
    if con_score >= 16:
        scores["brute"] += 1
        scores["soldier"] += 1

    # High DEX: skirmisher or lurker
    dex_score = abilities.get("dex", 10)
    if dex_score >= 16:
        scores["skirmisher"] += 2
        scores["lurker"] += 1

    # High INT/WIS/CHA: controller or artillery
    int_score = abilities.get("int", 10)
    wis_score = abilities.get("wis", 10)
    cha_score = abilities.get("cha", 10)
    if max(int_score, wis_score, cha_score) >= 16:
        scores["controller"] += 1
        scores["artillery"] += 1

    # Speed analysis
    walk_speed = 30
    if isinstance(speed_data, dict):
        walk_str = speed_data.get("walk", "30")
        try:
            walk_speed = int(str(walk_str).replace(" ft.", "").replace("ft", "").strip() or "30")
        except ValueError:
            walk_speed = 30

        if speed_data.get("fly"):
            scores["artillery"] += 1
            scores["skirmisher"] += 1

    if walk_speed >= 40:
        scores["skirmisher"] += 2

    # Analyze actions for ranged vs melee, AoE, conditions
    has_ranged_primary = False
    has_aoe = False
    has_conditions = False
    has_multiattack = False
    has_stealth = False
    has_leadership = False

    action_text = " ".join(a.get("desc", "") for a in actions).lower()
    special_text = " ".join(a.get("desc", "") for a in special).lower()
    all_text = action_text + " " + special_text

    # Check for ranged attacks
    if re.search(r"ranged (?:weapon |spell )?attack.*\+\d+.*reach", all_text) or \
       re.search(r"range \d+/\d+ ft", action_text) or \
       re.search(r"range \d+ ft", action_text):
        has_ranged_primary = True
        scores["artillery"] += 3

    # Check for AoE
    if re.search(r"each creature (?:in|within)", all_text):
        has_aoe = True
        scores["controller"] += 2
        scores["artillery"] += 1

    # Check for condition imposition
    condition_keywords = ["frightened", "paralyzed", "stunned", "restrained",
                         "charmed", "incapacitated", "blinded", "prone"]
    for cond in condition_keywords:
        if cond in all_text:
            has_conditions = True
            scores["controller"] += 1
            break

    # Check for multiattack
    if "multiattack" in action_text:
        has_multiattack = True
        scores["brute"] += 1
        scores["soldier"] += 1

    # Check for stealth
    skills = statblock.get("skills", {})
    stealth_bonus = 0
    if isinstance(skills, dict):
        stealth_bonus = skills.get("stealth", 0)
    if stealth_bonus >= 6 or "invisible" in all_text or "invisibility" in all_text:
        has_stealth = True
        scores["lurker"] += 3

    # Check for leadership/buff abilities
    if re.search(r"leadership|command|rally|inspire", all_text):
        has_leadership = True
        scores["soldier"] += 2

    # Check for defensive features
    if "shield" in all_text or "parry" in all_text:
        scores["soldier"] += 2

    # Check for cunning action, disengage, dash bonus
    if re.search(r"cunning action|disengage|nimble escape", all_text):
        scores["skirmisher"] += 3

    # Check for ambush/surprise
    if re.search(r"ambush|surprise|sneak", all_text):
        scores["lurker"] += 2

    # Check for terrain manipulation
    if re.search(r"difficult terrain|wall of|web|entangle", all_text):
        scores["controller"] += 2

    # Determine primary role
    sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_roles[0][0]

    # Secondary role if score is close (within 2 points)
    secondary = None
    if len(sorted_roles) > 1 and sorted_roles[1][1] >= sorted_roles[0][1] - 2 and sorted_roles[1][1] > 0:
        secondary = sorted_roles[1][0]

    return primary, secondary
