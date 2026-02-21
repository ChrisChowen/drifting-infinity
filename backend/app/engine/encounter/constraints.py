"""Hard constraint enforcement per GDD 4.4.

Prevents encounters that would be unfun or unfair.
"""

from app.engine.encounter.candidate_pool import MonsterCandidate

# Maximum counts of certain threat types per encounter
THREAT_CAPS: dict[str, int] = {
    "save_or_die": 1,
    "permanent_drain": 0,  # Never allowed
    "incapacitation": 2,
    "domination": 1,
    "swallow": 1,
    "petrification": 1,
}


def check_hard_constraints(
    candidate: MonsterCandidate,
    current_threat_counts: dict[str, int],
    party_level: int,
) -> tuple[bool, str]:
    """Check if adding this candidate would violate hard constraints.

    Returns:
        (allowed, reason) - False + reason if rejected
    """
    flags = candidate.threat_flags

    for flag in flags:
        cap = THREAT_CAPS.get(flag)
        if cap is not None:
            current = current_threat_counts.get(flag, 0)
            if current >= cap:
                return False, f"Would exceed cap for {flag} ({cap} max)"

    # CR sanity: no single creature should be more than party_level + 5
    if candidate.cr > party_level + 5:
        return False, f"CR {candidate.cr} exceeds maximum for level {party_level}"

    # Permanent drain is always rejected
    if "permanent_drain" in flags:
        return False, "Permanent drain effects are not allowed"

    return True, ""


def update_threat_counts(
    counts: dict[str, int],
    candidate: MonsterCandidate,
    quantity: int = 1,
) -> dict[str, int]:
    """Update threat counts after adding a candidate."""
    updated = dict(counts)
    for flag in candidate.threat_flags:
        updated[flag] = updated.get(flag, 0) + quantity
    return updated
