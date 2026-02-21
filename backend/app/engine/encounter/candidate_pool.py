"""Filter and score monster candidates for encounter building."""

from dataclasses import dataclass


@dataclass
class MonsterCandidate:
    """A monster that could be included in an encounter."""
    id: str
    slug: str
    name: str
    cr: float
    xp: int
    hp: int
    ac: int
    tactical_role: str
    secondary_role: str | None
    vulnerabilities: list[str]
    weak_saves: list[str]
    environments: list[str]
    creature_type: str
    size: str
    mechanical_signature: dict
    threat_flags: list[str]


def build_candidate_pool(
    monsters: list[dict],
    cr_min: float,
    cr_max: float,
    environment: str | None = None,
    exclude_ids: set[str] | None = None,
) -> list[MonsterCandidate]:
    """Filter monsters into valid candidates for the encounter.

    Args:
        monsters: List of monster dicts from the database
        cr_min: Minimum CR to include
        cr_max: Maximum CR to include
        environment: Optional environment filter (e.g., "underdark", "forest")
        exclude_ids: Monster IDs to exclude (recently used)
    """
    exclude_ids = exclude_ids or set()
    candidates = []

    for m in monsters:
        # Skip excluded
        if m["id"] in exclude_ids:
            continue

        cr = m.get("cr", 0)

        # CR filter
        if cr < cr_min or cr > cr_max:
            continue

        # Environment filter (if specified, monster must match or have no environments)
        if environment:
            envs = m.get("environments", []) or []
            if envs and environment.lower() not in [e.lower() for e in envs]:
                continue

        sig = m.get("mechanical_signature", {}) or {}

        candidates.append(MonsterCandidate(
            id=m["id"],
            slug=m.get("slug", ""),
            name=m.get("name", ""),
            cr=cr,
            xp=m.get("xp", 0),
            hp=m.get("hp", 0),
            ac=m.get("ac", 0),
            tactical_role=m.get("tactical_role", "brute"),
            secondary_role=m.get("secondary_role"),
            vulnerabilities=m.get("vulnerabilities", []) or [],
            weak_saves=m.get("weak_saves", []) or [],
            environments=m.get("environments", []) or [],
            creature_type=m.get("creature_type", ""),
            size=m.get("size", "Medium"),
            mechanical_signature=sig,
            threat_flags=sig.get("threat_flags", []) if sig else [],
        ))

    return candidates


def score_candidate(
    candidate: MonsterCandidate,
    template_role_weights: dict[str, float],
    party_damage_types: list[str] | None = None,
    theme_creature_types: list[str] | None = None,
    theme_creature_names: list[str] | None = None,
    environment: str | None = None,
) -> float:
    """Score a candidate for a given template. Higher = better fit.

    Args:
        candidate: The monster candidate to score
        template_role_weights: Role weights from the encounter template
        party_damage_types: Damage types the party can deal (for exploitability)
        theme_creature_types: Creature types from the active encounter theme
        theme_creature_names: Specific creature names from the active encounter theme
        environment: Active environment for thematic matching
    """
    score = 0.0

    # Role match score (primary role)
    role_weight = template_role_weights.get(candidate.tactical_role, 0.5)
    score += role_weight * 10.0

    # Secondary role bonus
    if candidate.secondary_role:
        secondary_weight = template_role_weights.get(candidate.secondary_role, 0.0)
        score += secondary_weight * 3.0

    # Exploitability bonus: if party can exploit vulnerabilities
    if party_damage_types and candidate.vulnerabilities:
        for vuln in candidate.vulnerabilities:
            if vuln.lower() in [dt.lower() for dt in party_damage_types]:
                score += 5.0
                break

    # Weak saves bonus (more fun encounters have exploitable saves)
    if candidate.weak_saves:
        score += len(candidate.weak_saves) * 1.0

    # Environment scoring: strongly prefer thematically-appropriate creatures
    if environment and candidate.environments:
        env_lower = [e.lower() for e in candidate.environments]
        if environment.lower() in env_lower:
            score += 8.0   # Matching environment tag
        else:
            score -= 5.0   # Has environment tags but none match
    # Creatures with no environment tags: neutral (score += 0)

    # Theme scoring: creatures matching the active theme get a significant bonus
    if theme_creature_names:
        if candidate.name in theme_creature_names:
            score += 20.0  # Strong preference for exact name match
        elif theme_creature_types and candidate.creature_type.lower() in [
            t.lower() for t in theme_creature_types
        ]:
            score += 10.0  # Moderate preference for type match

    return score
