"""Setting descriptions for the Armillary campaign setting.

Provides floor cluster descriptions, biome atmosphere text, and
Armillary-as-a-place descriptions that make the dungeon feel like
a living, coherent world rather than a random encounter generator.
"""

import random
from dataclasses import dataclass


@dataclass
class FloorCluster:
    """A thematic grouping of floors with shared atmosphere."""

    name: str
    floors: tuple[int, int]  # (start, end) inclusive
    description: str
    atmosphere: str
    dm_notes: str
    transition_text: str  # Read when entering this cluster


# ---------------------------------------------------------------------------
# Floor clusters — the Armillary's regions
# ---------------------------------------------------------------------------

FLOOR_CLUSTERS: list[FloorCluster] = [
    FloorCluster(
        name="The Clockwork Halls",
        floors=(1, 5),
        description=(
            "The upper levels of the Armillary are mechanical and ordered. Brass gears "
            "turn in the walls, crystal conduits pulse with measured energy, and the "
            "architecture follows a cold, geometric logic. This is the machine's public "
            "face — functional, impersonal, and designed to be survived."
        ),
        atmosphere=(
            "The air tastes of ozone and old metal. Every surface hums faintly with "
            "arcane power. The arenas here are relatively straightforward — the Armillary "
            "is calibrating, learning what the party can do."
        ),
        dm_notes=(
            "These floors introduce the Armillary's tone. Keep encounters fair and "
            "the environment mechanical. The party should feel tested but not overwhelmed. "
            "Aethon is watching but hasn't revealed themselves yet."
        ),
        transition_text=(
            "The expedition begins. The Armillary's brass doors grind open, revealing "
            "corridors of interlocking gears and softly glowing conduits. The machine "
            "stirs to life around you."
        ),
    ),
    FloorCluster(
        name="The Living Depths",
        floors=(6, 10),
        description=(
            "Below the Clockwork Halls, the Armillary becomes organic. The brass gives "
            "way to stone threaded with bioluminescent veins. The arenas feel less "
            "constructed and more grown — as if the machine is alive at this depth. "
            "The creatures are nastier, the environments stranger."
        ),
        atmosphere=(
            "The humming of gears is replaced by a deeper, rhythmic pulse — like a "
            "heartbeat. The walls breathe. Fungi and crystal formations emerge from "
            "the stonework. Down here, the Armillary stops pretending to be a machine."
        ),
        dm_notes=(
            "The Armillary becomes personal here. Encounters target party weaknesses. "
            "Aethon begins to communicate. The shift from mechanical to organic should "
            "feel gradual but unmistakable."
        ),
        transition_text=(
            "The corridors change. Brass and crystal give way to stone veined with "
            "pulsing light. The air is warmer, thicker. The Armillary's heartbeat "
            "echoes through the floor beneath your feet."
        ),
    ),
    FloorCluster(
        name="The Shattered Planes",
        floors=(11, 15),
        description=(
            "Reality fractures in the middle depths. The arenas draw from other planes "
            "of existence — fragments of the Feywild, echoes of the Shadowfell, pockets "
            "of elemental chaos. The Armillary's reach extends beyond the Material Plane, "
            "and it pulls these fragments in as testing grounds."
        ),
        atmosphere=(
            "Each arena feels like stepping into a different world. The transitions are "
            "jarring — one moment you're in a crystal cavern, the next you're standing "
            "in a Shadowfell wasteland. The Armillary is showing off."
        ),
        dm_notes=(
            "Lean into the planar variety. Each arena should feel distinct and alien. "
            "Aethon is openly communicating now and reveals their nature and purpose. "
            "The philosophical heart of the narrative lives here."
        ),
        transition_text=(
            "The walls crack. Through the fissures: other worlds. Fragments of reality "
            "tumble past like debris in a slow river. The Armillary's power extends "
            "beyond this plane, and it's pulling everything it can reach into the testing grounds."
        ),
    ),
    FloorCluster(
        name="The Heart of the Machine",
        floors=(16, 20),
        description=(
            "The deepest levels are the Armillary itself — not arenas within a machine, "
            "but the machine's organs exposed. Gears the size of buildings, rivers of "
            "liquid arcane energy, crystalline structures that sing with power. This is "
            "where the Armillary's purpose is laid bare."
        ),
        atmosphere=(
            "Power radiates from every surface. The air crackles. Gravity is a suggestion. "
            "The arenas here don't just host encounters — they participate in them. "
            "The boundary between arena and Armillary has dissolved."
        ),
        dm_notes=(
            "Maximum intensity. Encounters are the hardest of the run. Aethon is no "
            "longer an observer but a participant. The final floors should feel "
            "transcendent — cosmic in scale, personal in stakes."
        ),
        transition_text=(
            "You descend into the heart. The arena walls dissolve into the machine's "
            "core — an orrery of impossible scale, gears turning within gears, light "
            "and shadow dancing in patterns that hurt to comprehend. "
            "You are inside the Armillary now."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Cluster index
# ---------------------------------------------------------------------------


def get_cluster_for_floor(floor_number: int) -> FloorCluster | None:
    """Return the floor cluster for a given floor number."""
    for cluster in FLOOR_CLUSTERS:
        if cluster.floors[0] <= floor_number <= cluster.floors[1]:
            return cluster
    return None


# ---------------------------------------------------------------------------
# Biome atmosphere text — layered on top of environment descriptions
# ---------------------------------------------------------------------------

BIOME_ATMOSPHERE: dict[str, list[str]] = {
    "arctic": [
        "The cold is absolute. It seeps through armor, numbs fingers, and "
        "turns breath to frost. The Armillary has recreated winter at its "
        "most hostile.",
        "Ice and silence. The only sounds are the creak of frozen stone "
        "and the distant howl of wind that shouldn't exist underground.",
        "Frost crystallizes on every surface within seconds. The "
        "Armillary's recreation of arctic conditions is merciless in "
        "its fidelity.",
    ],
    "forest": [
        "The trees are too old. Their roots dig into the Armillary's "
        "structure as if they've been growing here for centuries — "
        "which, perhaps, they have.",
        "A false sky stretches overhead, complete with drifting clouds. "
        "The illusion is perfect until you notice the gears turning "
        "behind the canopy.",
        "The forest floor is carpeted in real leaves. Insects buzz "
        "through real air. Only the faint hum of the Armillary reminds "
        "you this is constructed.",
    ],
    "underground": [
        "The darkness below is real darkness — not the absence of "
        "light, but a presence. Something that presses against your "
        "torchlight and pushes back.",
        "Stone and shadow form the Armillary's bones. Down here, you "
        "can feel the machine's age — millennia of purpose, still "
        "grinding forward.",
        "The weight of the earth above is palpable. The Armillary "
        "recreates not just caves, but the crushing sense of depth "
        "that comes with them.",
    ],
    "water": [
        "Water fills the lower chambers, salt-tinged and cold. The "
        "Armillary has somehow recreated tidal forces — the water "
        "level shifts between arenas.",
        "The sound of water is constant — dripping, flowing, crashing. "
        "It masks other sounds. The creatures know this.",
        "The Armillary's aquatic chambers smell of brine and ancient "
        "stone. Currents push through passages that shouldn't have "
        "tides.",
    ],
    "mountain": [
        "The Armillary has compressed a mountain range into a vertical "
        "labyrinth. The air thins as you climb, and the views between "
        "platforms are dizzying.",
        "Stone and wind. The Armillary's recreation of alpine conditions "
        "is unsettlingly accurate, down to the thin air and sudden "
        "weather shifts.",
        "The peaks here reach into a void that is not sky. The "
        "Armillary's mountains end where the machine's ceiling begins "
        "— if it has one.",
    ],
    "urban": [
        "A ghost city within the machine. The buildings are hollow "
        "approximations — facades with nothing behind them. But the "
        "alleys are real, and so are the shadows within them.",
        "The Armillary has studied cities. These streets follow no "
        "real city's plan, but they feel right — the cramped angles, "
        "the echo of footsteps, the sense of being watched from "
        "windows.",
        "Lanterns flicker in windows with no rooms behind them. The "
        "urban arenas are stage sets built by something that "
        "understands cities but has never lived in one.",
    ],
    "desert": [
        "Heat radiates from the stone floor — the Armillary has "
        "recreated a sun without a sky. Sand drifts through mechanisms "
        "that were never designed to hold it.",
        "The desert within the machine is somehow more hostile than a "
        "natural one. The sand is finer, the heat more focused, the "
        "desolation more absolute.",
        "The Armillary generates heat without flame. The sand underfoot "
        "was stone before the machine ground it down — patience "
        "measured in geological time.",
    ],
    "plains": [
        "An impossible grassland stretches beneath an artificial sky. "
        "Wind ripples through the grass in patterns that feel almost "
        "intentional.",
        "Open ground is rare in the Armillary. When it appears, it "
        "means the machine wants you exposed. There's nowhere to hide "
        "here by design.",
        "The grassland hums with insect life — a detail so precise it "
        "betrays the Armillary's obsession with authenticity. Even the "
        "smell of cut grass is real.",
    ],
    "planar": [
        "Reality comes apart at the seams. The Armillary's power "
        "reaches between planes here, pulling fragments of other worlds "
        "into the arena. Nothing can be trusted — not distance, not "
        "direction, not gravity.",
        "The planar energy is intoxicating and terrifying in equal "
        "measure. Colors are wrong. Sounds arrive before their sources. "
        "Time stutters.",
        "The boundaries between worlds are tissue-thin here. Step "
        "through the wrong shadow and you might end up somewhere the "
        "Armillary can't reach.",
    ],
}


def get_biome_atmosphere(biome: str) -> str:
    """Get atmospheric text for a biome."""
    pool = BIOME_ATMOSPHERE.get(biome, [])
    if pool:
        return random.choice(pool)
    return "The Armillary configures the arena. The air shifts. Something is different."


# ---------------------------------------------------------------------------
# Floor transition text
# ---------------------------------------------------------------------------

FLOOR_TRANSITION_LINES: list[str] = [
    "The arena collapses behind you. Ahead: a passage downward. The Armillary reconfigures.",
    "The mechanisms shift. Walls fold into floors, floors"
    " become ceilings. A new level takes shape.",
    "A moment of stillness between floors. The Armillary is thinking.",
    "The descent continues. Each floor is deeper into the machine's purpose.",
    "Stone grinds against stone as the passage to the next floor opens. The air changes.",
    "The floor beneath you rotates — slowly at first, then "
    "faster — and when it stops, the world around you is new.",
    "Gears engage with a sound like distant thunder. The "
    "Armillary is reconfiguring the path ahead.",
    "The corridor spirals downward. With each revolution, the "
    "architecture subtly shifts — older, stranger, deeper.",
    "A bridge of light spans a void between floors. You cross it, and it dissolves behind you.",
    "The transition is gentler this time — a slow fade from one "
    "reality to the next, as if the Armillary is being careful "
    "with you.",
]


def get_floor_transition_text(floor_number: int) -> str:
    """Get transition text between floors.

    Uses cluster transition text when entering a new cluster,
    otherwise uses generic transition lines.
    """
    cluster = get_cluster_for_floor(floor_number)
    if cluster and floor_number == cluster.floors[0]:
        return cluster.transition_text
    return random.choice(FLOOR_TRANSITION_LINES)
