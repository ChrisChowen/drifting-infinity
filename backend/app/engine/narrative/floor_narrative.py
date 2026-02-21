"""Floor narrative orchestrator.

Assembles the full narrative output for an encounter from all narrative
engine modules. This is the primary entry point for generating DM-facing
narrative content for an encounter proposal.
"""

from dataclasses import dataclass

from app.engine.narrative.creature_flavor import (
    CreatureFlavorResult,
    generate_creature_flavor,
)
from app.engine.narrative.dm_guidance import (
    GuidanceBox,
    generate_dm_guidance,
)
from app.engine.narrative.encounter_hooks import generate_encounter_hook
from app.engine.narrative.read_aloud import (
    ReadAloudResult,
    generate_read_aloud,
)
from app.engine.narrative.weakness_guidance import (
    WeaknessTip,
    build_roguelike_reference,
    generate_weakness_tips,
)


@dataclass
class EncounterNarrative:
    """Complete narrative output for a single encounter."""

    read_aloud: ReadAloudResult
    encounter_hook: str
    creature_flavor: list[CreatureFlavorResult]
    dm_guidance_boxes: list[GuidanceBox]
    weakness_tips: list[WeaknessTip]
    roguelike_reference: dict[str, str]


def generate_encounter_narrative(
    template_name: str,
    danger_rating: str,
    environment_key: str,
    floor_number: int,
    arena_number: int,
    total_arenas: int,
    creatures: list[dict],
    objective_category: str = "combat",
    theme_name: str = "",
    theme_id: str = "",
    arc_position: str = "middle",
) -> EncounterNarrative:
    """Generate complete narrative content for an encounter.

    This is the primary orchestration function. It calls each narrative
    module and assembles the results.

    Args:
        template_name: Encounter template (e.g. "hold_and_flank")
        danger_rating: Danger rating (Challenging/Dangerous/Brutal/Lethal)
        environment_key: Environment key (e.g. "forest")
        floor_number: Current floor number
        arena_number: Current arena number on this floor
        total_arenas: Total arenas on this floor
        creatures: List of creature dicts with keys:
            monster_id, name, tactical_role, creature_type, count,
            vulnerabilities, weak_saves
        objective_category: Objective category (combat/tactical/exploration)
        theme_name: Encounter theme name (optional)
        theme_id: Encounter theme ID for keyed lookups (optional)
        arc_position: Arena position within floor ("opener"/"middle"/"climax")
    """
    # Total creature count for read-aloud
    creature_count = sum(c.get("count", 1) for c in creatures)

    # Read-aloud text
    read_aloud = generate_read_aloud(
        environment_key=environment_key,
        creature_count=creature_count,
        objective_category=objective_category,
        floor_number=floor_number,
        theme_name=theme_name,
        theme_id=theme_id,
        arc_position=arc_position,
    )

    # Encounter hook
    encounter_hook = generate_encounter_hook(
        template_name=template_name,
        danger_rating=danger_rating,
        floor_number=floor_number,
        arena_number=arena_number,
        total_arenas=total_arenas,
        theme_name=theme_name,
        theme_id=theme_id,
    )

    # Creature flavor
    creature_flavor = [
        generate_creature_flavor(
            monster_id=c.get("monster_id", ""),
            name=c.get("name", "Unknown"),
            tactical_role=c.get("tactical_role", "brute"),
            creature_type=c.get("creature_type", ""),
            count=c.get("count", 1),
        )
        for c in creatures
    ]

    # DM guidance boxes
    dm_guidance_boxes = generate_dm_guidance(
        template_name=template_name,
        danger_rating=danger_rating,
        environment_key=environment_key,
        creatures=creatures,
    )

    # Weakness tips
    weakness_tips = generate_weakness_tips(creatures)

    # Roguelike rules reference
    roguelike_reference = build_roguelike_reference()

    return EncounterNarrative(
        read_aloud=read_aloud,
        encounter_hook=encounter_hook,
        creature_flavor=creature_flavor,
        dm_guidance_boxes=dm_guidance_boxes,
        weakness_tips=weakness_tips,
        roguelike_reference=roguelike_reference,
    )
