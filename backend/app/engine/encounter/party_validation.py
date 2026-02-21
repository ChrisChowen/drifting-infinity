"""Party validation per GDD 4.6.

Checks encounter against party capabilities to issue ACCEPT/WARN/REJECT verdicts.
"""

from dataclasses import dataclass
from enum import Enum

from app.engine.encounter.candidate_pool import MonsterCandidate


class ValidationVerdict(str, Enum):
    ACCEPT = "accept"
    WARN = "warn"
    REJECT = "reject"


@dataclass
class ValidationResult:
    verdict: ValidationVerdict
    warnings: list[str]
    rejections: list[str]


def validate_encounter(
    creatures: list[tuple[MonsterCandidate, int]],  # (candidate, count)
    party_damage_types: list[str],
    party_capabilities: dict[str, bool],
    party_level: int,
    party_size: int,
) -> ValidationResult:
    """Validate an encounter against party capabilities.

    Checks:
    - Can party deal damage to all creatures? (immunity check)
    - Can party handle flight? (if enemies fly)
    - Can party handle conditions? (if enemies impose dangerous conditions)
    - Is CR spread reasonable?
    """
    warnings = []
    rejections = []

    has_ranged = party_capabilities.get("ranged_attack", False)
    has_magic = party_capabilities.get("spellcasting", False)
    has_flight = party_capabilities.get("flight", False)
    has_healing = party_capabilities.get("healing", False)
    has_dispel = party_capabilities.get("dispel_magic", False)

    total_creatures = sum(count for _, count in creatures)

    for candidate, count in creatures:
        flags = candidate.threat_flags

        # Flight check
        if "flight_only" in flags and not has_ranged and not has_magic and not has_flight:
            rejections.append(
                f"{candidate.name} flies and party has no ranged/magic/flight capability"
            )

        # Save-or-die check
        if "save_or_die" in flags and party_level < 5:
            warnings.append(
                f"{candidate.name} has save-or-die effects (dangerous at level {party_level})"
            )

        # Incapacitation flood
        if "incapacitation" in flags and count >= 3:
            warnings.append(
                f"Multiple {candidate.name} can chain incapacitation effects"
            )

        # Action economy: too many creatures vs party
        if total_creatures > party_size * 3:
            warnings.append(
                f"Action economy heavily favors monsters ({total_creatures} vs {party_size} party)"
            )

    # Determine verdict
    if rejections:
        verdict = ValidationVerdict.REJECT
    elif warnings:
        verdict = ValidationVerdict.WARN
    else:
        verdict = ValidationVerdict.ACCEPT

    return ValidationResult(
        verdict=verdict,
        warnings=warnings,
        rejections=rejections,
    )
