"""Select an appropriate environment for an encounter based on available monsters and floor depth.

Supports floor-level biome constraints: each floor picks a primary biome,
then arenas within that floor draw from the biome's environment variants
without repeating until all variants are exhausted.
"""

import random

from app.data.environments import (
    BIOME_GROUPS,
    ENVIRONMENTS,
    EnvironmentDef,
    get_environment,
    get_environments_in_biome,
)


def select_floor_biome(
    floor_number: int,
    party_level: int,
    monster_dicts: list[dict],
) -> str:
    """Select a biome for a floor based on monster availability and floor depth.

    For each biome group, computes an average floor weight across its member
    environments and weights by monster availability. Returns a biome key.
    """
    # Count monster availability per environment
    env_monster_counts = _count_monster_environments(monster_dicts)

    biome_weights: list[tuple[str, float]] = []
    for biome, env_keys in BIOME_GROUPS.items():
        # Average floor weight across biome's environments
        total_weight = 0.0
        total_monsters = 0
        valid_envs = 0
        for ek in env_keys:
            env_def = ENVIRONMENTS.get(ek)
            if not env_def:
                continue
            fw = env_def.floor_weights.get(floor_number, 1.0)
            mc = env_monster_counts.get(ek, 0)
            total_weight += fw
            total_monsters += mc
            valid_envs += 1

        if valid_envs == 0 or total_monsters < 3:
            continue

        avg_weight = total_weight / valid_envs
        availability = min(total_monsters / (valid_envs * 20.0), 1.0)
        biome_weights.append((biome, avg_weight * (0.5 + availability)))

    if not biome_weights:
        return "forest"

    keys, weights = zip(*biome_weights)
    return random.choices(keys, weights=weights, k=1)[0]


def select_environment(
    monster_dicts: list[dict],
    floor_number: int = 1,
    templates_used: list[str] | None = None,
    preference: str | None = None,
    biome_constraint: str | None = None,
    used_environments: list[str] | None = None,
) -> EnvironmentDef:
    """Select an environment based on available monsters and floor depth.

    Args:
        monster_dicts: List of monster dicts (must have 'environments' field).
        floor_number: Current floor number (affects weight of certain envs).
        templates_used: Templates already used this floor (for template affinity).
        preference: If set, force this environment (if it exists).
        biome_constraint: If set, restrict candidates to this biome's envs.
        used_environments: Environments already used this floor (avoid repeats).

    Returns:
        The selected EnvironmentDef.
    """
    # If preference specified, use it
    if preference:
        env = get_environment(preference)
        if env:
            return env

    # Determine eligible environment keys
    if biome_constraint:
        eligible_keys = set(get_environments_in_biome(biome_constraint))
        # Exclude already-used environments (fall back to repeats if exhausted)
        if used_environments:
            remaining = eligible_keys - set(used_environments)
            if remaining:
                eligible_keys = remaining
        # Ensure all eligible keys exist in ENVIRONMENTS
        eligible_keys = {k for k in eligible_keys if k in ENVIRONMENTS}
    else:
        eligible_keys = set(ENVIRONMENTS.keys())
        if used_environments:
            remaining = eligible_keys - set(used_environments)
            if remaining:
                eligible_keys = remaining

    # Count monster availability per environment
    env_monster_counts = _count_monster_environments(monster_dicts)

    # Build weighted candidate list
    candidates: list[tuple[str, float]] = []
    for key in eligible_keys:
        env_def = ENVIRONMENTS.get(key)
        if not env_def:
            continue
        monster_count = env_monster_counts.get(key, 0)
        if monster_count < 3:
            continue

        floor_weight = env_def.floor_weights.get(floor_number, 1.0)
        availability_bonus = min(monster_count / 20.0, 1.0)

        template_bonus = 0.0
        if templates_used and env_def.suggested_templates:
            unused_suggested = [
                t for t in env_def.suggested_templates if t not in templates_used
            ]
            if unused_suggested:
                template_bonus = 0.3 * len(unused_suggested)

        weight = floor_weight * (0.5 + availability_bonus) + template_bonus
        candidates.append((key, weight))

    if not candidates:
        return ENVIRONMENTS.get("forest", list(ENVIRONMENTS.values())[0])

    keys, weights = zip(*candidates)
    chosen_key = random.choices(keys, weights=weights, k=1)[0]
    return ENVIRONMENTS[chosen_key]


def _count_monster_environments(monster_dicts: list[dict]) -> dict[str, int]:
    """Count how many monsters are available in each environment."""
    env_monster_counts: dict[str, int] = {}
    for monster in monster_dicts:
        envs = monster.get("environments", [])
        if not envs:
            for key in ENVIRONMENTS:
                env_monster_counts[key] = env_monster_counts.get(key, 0) + 1
        else:
            for env_name in envs:
                env_key = env_name.lower().strip()
                if env_key in ENVIRONMENTS:
                    env_monster_counts[env_key] = (
                        env_monster_counts.get(env_key, 0) + 1
                    )
    return env_monster_counts
