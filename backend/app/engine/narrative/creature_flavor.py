"""Creature flavor text generation.

Gives each creature in an encounter a personality, behavioral description,
and reason for being in this arena. Draws from tactical role, intelligence
tier, encounter theme, and environment to produce DM-readable text.
"""

import random
from dataclasses import dataclass


@dataclass
class CreatureFlavorResult:
    """Flavor text for a single creature type in an encounter."""

    monster_id: str
    name: str
    personality: str
    behavior: str
    arena_reason: str


# ---------------------------------------------------------------------------
# Personality fragments by tactical role
# ---------------------------------------------------------------------------

ROLE_PERSONALITY: dict[str, list[str]] = {
    "brute": [
        "Rage-driven and fearless, it charges without hesitation.",
        "A wall of muscle and fury, it knows nothing but forward.",
        "Brutal and direct — it will hit the nearest thing until it stops moving.",
        "It bellows a challenge the moment it sees the party. Subtlety is not in its nature.",
    ],
    "soldier": [
        "Disciplined and watchful, it holds its ground with professional calm.",
        "It moves with military precision, eyes constantly scanning for the greatest threat.",
        "Loyal to the group, it positions itself to protect weaker allies.",
        "Trained and methodical — it waits for the right moment before committing.",
    ],
    "artillery": [
        "It keeps its distance, preferring to strike from safety.",
        "Calculating and patient, it picks targets with cold precision.",
        "It positions itself where it can see everything and be reached by nothing.",
        "Cowardly by nature, but devastating when given space to work.",
    ],
    "controller": [
        "It doesn't fight — it reshapes the battlefield to suit its purposes.",
        "Cunning and manipulative, it targets the party's coordination, not their hit points.",
        "It cares nothing for direct combat. The arena itself is its weapon.",
        "Methodical and patient, it layers effects to create zones of misery.",
    ],
    "skirmisher": [
        "Quick and opportunistic, it strikes and vanishes before retaliation comes.",
        "It darts from shadow to shadow, looking for the wounded and the isolated.",
        "Restless and aggressive, but never foolish enough to stand and trade blows.",
        "It tests the party's formation, probing for gaps to exploit.",
    ],
    "lurker": [
        "Patient beyond measure, it waits for the perfect moment to strike.",
        "It has been here longer than you realize. It was watching before you entered.",
        "Silent and lethal — it exists in the spaces between your attention.",
        "It will not announce itself. The first sign will be the blade at your back.",
    ],
}

# ---------------------------------------------------------------------------
# Behavior descriptions by tactical role
# ---------------------------------------------------------------------------

ROLE_BEHAVIOR: dict[str, list[str]] = {
    "brute": [
        "Charges the nearest enemy and uses multiattack relentlessly. Ignores pain until death.",
        "Targets whoever hit it last. Retreats only when grievously"
        " wounded — and even then, reluctantly.",
        "Opens with its most powerful attack, then pounds away with melee strikes.",
    ],
    "soldier": [
        "Holds a defensive position, using terrain to its advantage."
        " Protects allies and punishes overextension.",
        "Forms a shield wall with other soldiers. Targets the party's most dangerous attacker.",
        "Stays between the party and the backline creatures."
        " Uses leadership abilities to coordinate.",
    ],
    "artillery": [
        "Maintains maximum range at all times. Focuses fire on the party's spellcasters.",
        "Uses AoE abilities to catch clustered enemies, then"
        " switches to single-target against isolated threats.",
        "Repositions constantly to maintain line of sight. Flees if engaged in melee.",
    ],
    "controller": [
        "Opens with area denial abilities to split the party."
        " Then uses debuffs on the highest-threat target.",
        "Creates zones of difficult terrain or damaging effects. Herds enemies toward its allies.",
        "Targets concentration casters first. Uses conditions"
        " to remove key party members from the fight.",
    ],
    "skirmisher": [
        "Hit-and-run tactics. Attacks, disengages, repositions."
        " Targets the wounded and the isolated.",
        "Looks for flanking opportunities. Coordinates with other"
        " skirmishers to keep pressure on multiple targets.",
        "Kites at the edge of melee range. Dashes through the"
        " party's formation to reach backline targets.",
    ],
    "lurker": [
        "Begins hidden. Ambushes the highest-value target with"
        " maximum damage. Retreats to stealth if possible.",
        "Strikes from concealment, then repositions while the"
        " party is distracted by other threats.",
        "Waits until a party member is isolated or distracted,"
        " then delivers a devastating surprise attack.",
    ],
}

# ---------------------------------------------------------------------------
# Arena reason by creature type
# ---------------------------------------------------------------------------

ARENA_REASONS: dict[str, list[str]] = {
    "undead": [
        "The Armillary has drawn it from the space between life and death.",
        "It was dead. The arena does not care about such trivialities.",
        "Bound by the Armillary's will, it fights because it"
        " has no choice — and no desire for one.",
    ],
    "fiend": [
        "Summoned from the lower planes, it relishes the opportunity for violence.",
        "The Armillary's rift pierced the Abyss. This creature clawed its way through.",
        "It serves no master here. It fights because that is what fiends do.",
    ],
    "beast": [
        "Territorial and aggressive, driven to fury by the arena's unnatural energies.",
        "The Armillary plucked it from the wild. Confused and"
        " angry, it lashes out at anything that moves.",
        "Its instincts have been sharpened by the arena. It hunts with unnatural focus.",
    ],
    "humanoid": [
        "Conscripted by the Armillary — whether they know it or not.",
        "They fight with purpose, though whether that purpose is their own remains unclear.",
        "Professional warriors, drawn to the arena by the promise of gold or glory.",
    ],
    "dragon": [
        "Even dragons are not beyond the Armillary's reach. It is furious at being summoned.",
        "It commands this space with the arrogance of its kind. The arena is now its lair.",
        "The Armillary respects power. A dragon earns its own arena.",
    ],
    "aberration": [
        "It doesn't belong in this reality. The Armillary found it in the spaces between worlds.",
        "Its mind operates on principles alien to mortal"
        " understanding. Do not try to reason with it.",
        "The arena warps subtly in its presence, as though reality itself recoils.",
    ],
    "construct": [
        "Built for this purpose. It is a weapon of the Armillary, and it feels nothing.",
        "Gears whir and pistons fire. The construct activates the moment the party enters.",
        "A remnant of whatever civilization built this place, still executing its final orders.",
    ],
    "monstrosity": [
        "The Armillary breeds these things in its depths. Each one is a unique horror.",
        "It is a predator, pure and simple. The arena is its hunting ground.",
        "Nature twisted by magical forces beyond comprehension. It is hungry.",
    ],
    "elemental": [
        "Raw elemental force given hostile intent by the Armillary's mechanisms.",
        "It erupts from the arena floor, a living manifestation of the environment's fury.",
        "The elemental plane bleeds through here. This creature is the wound made manifest.",
    ],
    "fey": [
        "It dances at the edge of perception, beautiful and lethal in equal measure.",
        "Drawn from the Feywild by the Armillary's resonance with the plane of dreams.",
        "It finds this all terribly amusing. Your suffering is entertainment.",
    ],
    "giant": [
        "The ground shakes with each step. It towers over the arena, barely contained.",
        "The Armillary chose something large. The arena is barely big enough.",
        "Ancient and powerful, it regards the party with contempt.",
    ],
    "celestial": [
        "Even the divine serves the Armillary here. Its light is cold and purposeful.",
        "Fallen or commanded, it fights with the terrible"
        " efficiency of something that was once good.",
        "Its presence is a paradox — radiant and merciless.",
    ],
    "ooze": [
        "It has no mind, no will, no mercy. It simply dissolves whatever it touches.",
        "A shapeless hunger, drawn to warmth and movement. It oozes toward the party.",
        "The Armillary unleashes the simplest of horrors: something that cannot be reasoned with.",
    ],
    "plant": [
        "Roots erupt from the floor. The arena itself has come alive.",
        "It looks like vegetation until it moves. Then it looks like a nightmare.",
        "The Armillary's influence has accelerated its growth."
        " It is hungry for more than sunlight.",
    ],
    "swarm": [
        "They pour from every crack and crevice, a living carpet of hunger.",
        "Individually nothing. Together, a nightmare. They move as one.",
        "The buzzing fills the arena. There are too many to count, too many to fight individually.",
    ],
}

DEFAULT_ARENA_REASONS: list[str] = [
    "The Armillary has placed it here. Its reasons are its own.",
    "It fights because the arena demands it. Perhaps it had a life before this.",
    "A creature of the Armillary's choosing, shaped for this exact moment.",
]


def generate_creature_flavor(
    monster_id: str,
    name: str,
    tactical_role: str,
    creature_type: str,
    count: int = 1,
) -> CreatureFlavorResult:
    """Generate flavor text for a creature type in an encounter."""
    role = tactical_role.lower() if tactical_role else "brute"

    personality = random.choice(ROLE_PERSONALITY.get(role, ROLE_PERSONALITY["brute"]))
    behavior = random.choice(ROLE_BEHAVIOR.get(role, ROLE_BEHAVIOR["brute"]))

    ctype = creature_type.lower() if creature_type else ""
    reason_pool = ARENA_REASONS.get(ctype, DEFAULT_ARENA_REASONS)
    arena_reason = random.choice(reason_pool)

    # Pluralize personality for groups
    if count > 2:
        personality = personality.replace("It ", "They ").replace("it ", "they ")
        personality = personality.replace("Its ", "Their ").replace("its ", "their ")

    return CreatureFlavorResult(
        monster_id=monster_id,
        name=name,
        personality=personality,
        behavior=behavior,
        arena_reason=arena_reason,
    )
