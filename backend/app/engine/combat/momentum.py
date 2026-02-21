"""Momentum recovery system per GDD 2.5.

Between arenas, the DM can grant limited recovery to the party.
Base: 2 recovery options per arena cleared (standard party).
Momentum Bonus: If the arena was cleared efficiently (DM discretion),
the party gets extra recovery options.
"""

from dataclasses import dataclass


@dataclass
class RecoveryOption:
    """A single recovery option the DM can grant."""
    key: str
    name: str
    description: str
    category: str  # "hp", "resource", "condition"


RECOVERY_OPTIONS: list[RecoveryOption] = [
    RecoveryOption(
        key="short_rest_hp",
        name="Short Rest HP",
        description="One character can spend one Hit Die to recover HP.",
        category="hp",
    ),
    RecoveryOption(
        key="partial_heal",
        name="Partial Heal",
        description="One character regains HP equal to their level + CON modifier.",
        category="hp",
    ),
    RecoveryOption(
        key="remove_condition",
        name="Remove Condition",
        description="One condition is removed from a character.",
        category="condition",
    ),
    RecoveryOption(
        key="restore_spell_slot",
        name="Restore Spell Slot",
        description="One character regains a spent spell slot (level 3 or lower).",
        category="resource",
    ),
    RecoveryOption(
        key="restore_ability",
        name="Restore Ability",
        description="One character regains a spent class ability (short rest type).",
        category="resource",
    ),
    RecoveryOption(
        key="inspiration",
        name="Inspiration",
        description="One character gains Inspiration.",
        category="resource",
    ),
]


def get_recovery_count(
    base_count: int = 1,
    momentum_bonus: bool = False,
    bonus_count: int = 2,
) -> int:
    """Get how many recovery options the party gets.

    Args:
        base_count: Base recovery options per scaling params
        momentum_bonus: Whether the Momentum Bonus was earned
        bonus_count: Extra options from Momentum Bonus per scaling params
    """
    total = base_count
    if momentum_bonus:
        total = bonus_count
    return total


def get_available_recoveries() -> list[RecoveryOption]:
    """Get all available recovery options."""
    return list(RECOVERY_OPTIONS)
