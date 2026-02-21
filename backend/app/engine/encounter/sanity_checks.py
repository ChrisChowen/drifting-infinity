"""Sanity checks per GDD 4.7 (Sly Flourish method + action economy caps)."""


def check_action_economy(
    creature_count: int,
    party_size: int,
) -> list[str]:
    """Check action economy balance."""
    warnings = []

    ratio = creature_count / max(party_size, 1)

    if ratio > 3.0:
        warnings.append(
            f"Extreme action economy imbalance: {creature_count} creatures vs {party_size} party members"
        )
    elif ratio > 2.5:
        warnings.append(
            f"High creature count ({creature_count}) may overwhelm party of {party_size}"
        )

    if creature_count == 1 and party_size >= 4:
        warnings.append(
            "Single creature vs large party: consider adding minions or lair actions"
        )

    return warnings


def check_sly_flourish_guidelines(
    highest_cr: float,
    party_level: int,
    party_size: int,
) -> list[str]:
    """Sly Flourish-style sanity checks."""
    warnings = []

    # Highest single CR vs party level
    if highest_cr > party_level + 3:
        warnings.append(
            f"Highest CR ({highest_cr}) is {highest_cr - party_level} above party level - may be too dangerous"
        )

    if highest_cr >= party_level * 2 and party_level >= 5:
        warnings.append(
            f"CR {highest_cr} creature is double+ party level - likely deadly"
        )

    return warnings


def run_sanity_checks(
    creature_count: int,
    highest_cr: float,
    party_level: int,
    party_size: int,
) -> list[str]:
    """Run all sanity checks."""
    warnings = []
    warnings.extend(check_action_economy(creature_count, party_size))
    warnings.extend(check_sly_flourish_guidelines(highest_cr, party_level, party_size))
    return warnings
