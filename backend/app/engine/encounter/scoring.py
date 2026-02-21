"""Advanced candidate scoring per GDD 4.3.

Weights candidates by exploit compatibility, diversity, novelty, and threat profile.
"""

from app.engine.encounter.candidate_pool import MonsterCandidate


def score_candidate_advanced(
    candidate: MonsterCandidate,
    template_role_weights: dict[str, float],
    party_damage_types: list[str] | None = None,
    party_saves: dict[str, int] | None = None,
    recently_used_monster_ids: set[str] | None = None,
    current_roles: list[str] | None = None,
) -> float:
    """Advanced candidate scoring with multiple factors.

    Factors:
    1. Role fit (template matching)
    2. Exploit compatibility (can party exploit vulnerabilities?)
    3. Diversity bonus (prefer variety of roles)
    4. Novelty bonus (prefer monsters not recently used)
    5. Threat profile (interesting threat flags)
    """
    score = 0.0

    # 1. Role fit (0-30 points)
    role_weight = template_role_weights.get(candidate.tactical_role, 0.5)
    score += role_weight * 10.0

    if candidate.secondary_role:
        score += template_role_weights.get(candidate.secondary_role, 0.0) * 3.0

    # 2. Exploit compatibility (0-15 points)
    if party_damage_types and candidate.vulnerabilities:
        matches = sum(
            1 for v in candidate.vulnerabilities
            if v.lower() in [dt.lower() for dt in party_damage_types]
        )
        score += min(15.0, matches * 7.5)

    # Weak save compatibility
    if party_saves and candidate.weak_saves:
        for save in candidate.weak_saves:
            if save in party_saves and party_saves[save] >= 5:
                score += 3.0

    # 3. Diversity bonus (0-10 points)
    if current_roles is not None:
        if candidate.tactical_role not in current_roles:
            score += 8.0
        elif current_roles.count(candidate.tactical_role) == 1:
            score += 3.0

    # 4. Novelty bonus (0-5 points)
    if recently_used_monster_ids:
        if candidate.id not in recently_used_monster_ids:
            score += 5.0
    else:
        score += 5.0

    # 5. Threat profile (0-5 points)
    interesting_flags = {"pack_tactics", "multiattack", "spellcasting", "aoe_attack", "flight_only"}
    matching = set(candidate.threat_flags) & interesting_flags
    score += len(matching) * 1.5

    return score
