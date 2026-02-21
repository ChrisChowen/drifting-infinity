"""Floor 20 final encounter — Aethon, The Architect.

The final arena of floor 20 is unique: a combined social/combat encounter
where the party confronts the entity behind the Armillary.
"""

from dataclasses import dataclass

from app.data.antagonist import (
    compute_aethon_stats_for_party,
    get_aethon_dialogue,
)


@dataclass
class AethonEncounter:
    """Configuration for the Floor 20 final encounter."""
    # Phase 1: Social
    greeting_text: str
    choice_text: str
    dm_social_instructions: str

    # Phase 2: Combat (if party fights)
    aethon_stats: dict
    combat_dm_instructions: str
    mirror_targets: list[str]       # Character classes to mirror

    # Phase 3: Resolution
    victory_text: str
    defeat_text: str

    # Metadata
    is_final_encounter: bool = True
    xp_value: int = 0


def generate_aethon_encounter(
    party_level: int,
    party_size: int,
    party_classes: list[str],
    run_number: int = 1,
) -> AethonEncounter:
    """Generate the Aethon final encounter for Floor 20.

    Args:
        party_level: Current party level (expected: 20).
        party_size: Number of living party members.
        party_classes: List of character classes in the party.
        run_number: Which campaign run this is (for dialogue variation).

    Returns:
        AethonEncounter with all three phases configured.
    """
    stats = compute_aethon_stats_for_party(party_level, party_size)

    greeting = get_aethon_dialogue("floor_20_greeting", run_number)
    choice = get_aethon_dialogue("floor_20_choice", run_number)
    fight_start = get_aethon_dialogue("floor_20_fight_start", run_number)
    victory = get_aethon_dialogue("floor_20_victory_party", run_number)
    defeat = get_aethon_dialogue("floor_20_defeat_party", run_number)

    # Mirror Protocol targets: prioritize full casters, then half casters, then martials
    caster_priority = ["wizard", "sorcerer", "warlock", "cleric", "druid", "bard"]
    half_caster = ["paladin", "ranger", "artificer"]
    martial = ["fighter", "barbarian", "rogue", "monk"]

    mirror_order: list[str] = []
    for cls in caster_priority + half_caster + martial:
        if cls in [c.lower() for c in party_classes]:
            mirror_order.append(cls)
    if not mirror_order:
        mirror_order = list(party_classes)

    # XP value: equivalent to a CR 22 creature (41,000 XP)
    xp_value = 41_000

    social_instructions = (
        "Aethon materializes in the center of the arena. Read the greeting, then present "
        "the choice. Give the party time to discuss and ask questions. Aethon will answer "
        "honestly — they have nothing to hide at this point. If the party chooses to join, "
        "describe the transformation: their consciousness merges with the Armillary. They "
        "become part of the machine, like Korvath. The run ends in 'transcendence.' "
        "If they choose to fight, proceed to Phase 2."
    )

    combat_instructions = (
        f"Aethon fights using Mirror Protocol — each round, they copy one party member's "
        f"class abilities. Priority order: {', '.join(mirror_order)}. Aethon is not trying "
        f"to kill the party — they're trying to test them. If the party is clearly outmatched, "
        f"Aethon scales back slightly (reduce damage by 25%). The goal is a dramatic, close "
        f"fight, not a TPK. {fight_start}"
    )

    return AethonEncounter(
        greeting_text=greeting,
        choice_text=choice,
        dm_social_instructions=social_instructions,
        aethon_stats=stats,
        combat_dm_instructions=combat_instructions,
        mirror_targets=mirror_order,
        victory_text=victory,
        defeat_text=defeat,
        xp_value=xp_value,
    )
