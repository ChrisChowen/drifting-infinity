"""Read-aloud text generation for encounters.

Composes scene-setting text the DM reads to players from environment,
creatures, objective, floor depth, and encounter theme. Each segment
draws from pools keyed by context, then assembled into a coherent
2-4 sentence passage.
"""

import random
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Arrival lines — keyed by environment key
# ---------------------------------------------------------------------------

ARRIVAL_LINES: dict[str, list[str]] = {
    "forest": [
        "The trees close in around you, ancient trunks"
        " blotting out the sky. Something moves in the"
        " shadows between the roots.",
        "Mist clings to the forest floor as you push through"
        " dense undergrowth. The canopy above swallows"
        " the light.",
        "A clearing opens ahead, ringed by gnarled oaks"
        " whose branches interlock like skeletal fingers.",
    ],
    "grassland": [
        "The wind sweeps across the open plain, carrying the"
        " scent of dry earth and something else — something"
        " predatory.",
        "Rolling hills stretch in every direction. There is"
        " nowhere to hide here, for you or for what"
        " watches you.",
        "The tall grass parts as you advance, golden stalks whispering against your armor.",
    ],
    "urban": [
        "The streets are too quiet. Shuttered windows stare"
        " down like hollow eyes, and the cobblestones are"
        " slick underfoot.",
        "You emerge into a cramped market square, abandoned"
        " stalls casting long shadows in the fading light.",
        "Alleyways branch in three directions, each darker"
        " than the last. Something clatters in the"
        " distance.",
    ],
    "underdark": [
        "The cavern opens before you, vast and dripping."
        " Bioluminescent fungi cast an eerie blue-green"
        " glow across the stone.",
        "Darkness swallows your torchlight within fifty"
        " paces. The sound of dripping water echoes from"
        " somewhere far below.",
        "Stalactites hang like teeth above a chamber carved"
        " by millennia of water. The air tastes of minerals"
        " and age.",
    ],
    "mountain": [
        "The path narrows to a ledge barely wide enough for"
        " two abreast. Wind howls through the pass,"
        " threatening to tear you from the rock.",
        "You crest a ridge and the mountain opens into a"
        " sheltered valley. Snow dusts the boulders, and"
        " the air is thin and cold.",
        "Scree shifts underfoot as you climb. Above, the"
        " peak vanishes into cloud. Below, something stirs.",
    ],
    "swamp": [
        "Fetid water rises to your ankles as the ground"
        " turns to muck. Dead trees lean at impossible"
        " angles, draped in moss.",
        "The swamp stretches endlessly, a maze of stagnant"
        " pools and half-submerged roots. Bubbles rise"
        " from the murk.",
        "Fog rolls across the bog, thick and sulfurous."
        " Every step squelches, and the ground sucks at"
        " your boots.",
    ],
    "desert": [
        "Heat shimmers rise from the sand, distorting the"
        " horizon into a wavering line. The sun is"
        " merciless.",
        "Dunes stretch in every direction, sculpted by a"
        " wind that never stops. Somewhere beneath the"
        " sand, something waits.",
        "A sandstone canyon opens before you, its walls"
        " carved smooth by ancient winds. The shade offers"
        " no comfort.",
    ],
    "coastal": [
        "Waves crash against the rocks below, sending salt"
        " spray high into the air. The tide pools gleam"
        " with strange light.",
        "The shoreline curves ahead, littered with driftwood"
        " and the bones of ships. Gulls circle overhead,"
        " screaming.",
        "Sea caves yawn open in the cliff face, their mouths"
        " dark and echoing with the surge of the tide.",
    ],
    "volcanic": [
        "The ground trembles beneath your feet. Cracks in"
        " the rock glow with molten light, and the air"
        " sears your lungs.",
        "Rivers of lava carve channels through obsidian"
        " fields. The heat is oppressive, distorting"
        " everything beyond thirty paces.",
        "Plumes of acrid smoke rise from vents in the stone. The rock itself is warm to the touch.",
    ],
    "temple": [
        "The temple's interior is vast and silent, dust"
        " motes drifting in shafts of light from cracks in"
        " the domed ceiling.",
        "Carved pillars line the central nave, their"
        " surfaces worn smooth by centuries of devotion"
        " now ended.",
        "An altar stands at the far end of the chamber, its"
        " sacred wards still faintly glowing. Someone — or"
        " something — has defiled this place.",
    ],
    "haunted_ruins": [
        "The ruins groan in the wind, stones shifting as though the building itself is breathing.",
        "A chill settles over you that has nothing to do"
        " with the temperature. The air here feels wrong"
        " — thin, like reality is fraying.",
        "Broken walls cast jagged shadows across the rubble."
        " A cold draft pushes through from somewhere below.",
    ],
    "crystal_caverns": [
        "Crystals jut from every surface, refracting your"
        " light into a thousand prismatic shards. The"
        " beauty is disorienting.",
        "The cave walls pulse with an inner light, deep"
        " violet and electric blue. The crystals hum at a"
        " frequency you feel in your teeth.",
        "A vast geode opens before you, its interior studded"
        " with formations taller than a man. The resonance"
        " is almost musical.",
    ],
    "sewer_catacomb": [
        "The stench hits you before the darkness does. Stone"
        " passages stretch ahead, slick with centuries of"
        " filth.",
        "Archways carved with forgotten names frame the"
        " entrance to the catacombs. Water trickles down"
        " the walls.",
        "Bones are stacked neatly in alcoves along the"
        " passage, skulls watching your approach with"
        " empty patience.",
    ],
    "planar": [
        "Reality buckles. The ground beneath you shifts"
        " between stone, glass, and something that isn't"
        " quite either.",
        "The sky — if it is a sky — churns with colors that"
        " don't exist in your world. Gravity feels like a"
        " suggestion.",
        "You step through the threshold and the rules"
        " change. Distance is unreliable. Sound arrives"
        " before its source.",
    ],
    "feywild": [
        "Colors are too vivid here, sounds too sweet. The"
        " flowers turn to watch you pass. Nothing in the"
        " Feywild is what it seems.",
        "A grove of silver-barked trees surrounds a clearing"
        " where fireflies drift in patterns too deliberate"
        " to be random.",
        "The air tastes of honey and ozone. Laughter echoes from somewhere you can't quite place.",
    ],
    "shadowfell_wastes": [
        "All color drains away as you cross the threshold."
        " The world is grey, the shadows too deep, the"
        " silence too complete.",
        "Ash falls like snow from a sky without sun. The"
        " landscape is familiar but hollowed out, a memory"
        " of a place that once had life.",
        "Your breath comes in clouds that hang too long in"
        " the still air. The darkness here has weight.",
    ],
    "elemental_nexus": [
        "The elements war around you — fire and ice, earth"
        " and air — crashing together in a kaleidoscope"
        " of raw power.",
        "Pillars of elemental energy surge from the ground,"
        " each one a different force of nature given form.",
        "The nexus thrums with barely contained energy. The"
        " air crackles, the ground shifts, and steam rises"
        " where fire meets ice.",
    ],
    "lava_tubes": [
        "The tunnel narrows, its walls smooth and glassy"
        " from ancient lava flows. A faint orange glow"
        " pulses from deeper within.",
        "You descend through tubes carved by molten rock"
        " millennia ago. The heat builds with every step.",
        "The lava tube opens into a chamber where the"
        " ceiling drips with obsidian stalactites. Pools"
        " of cooling magma line the floor.",
    ],
}

# Default for environments not in the map
DEFAULT_ARRIVALS: list[str] = [
    "The arena shifts around you. The Armillary has chosen this ground.",
    "The air changes as the Armillary configures the next arena. You are not alone.",
    "Stone and shadow rearrange themselves. The arena takes shape, and with it, the threat.",
]

# ---------------------------------------------------------------------------
# Creature reveal lines — keyed by creature count category
# ---------------------------------------------------------------------------

CREATURE_REVEALS: dict[str, list[str]] = {
    "solo": [
        "A single figure stands between you and the way forward. It does not flinch.",
        "One creature waits here — but the Armillary would not choose it without reason.",
        "It stands alone, which means it doesn't need help.",
    ],
    "pair": [
        "Two shapes emerge from the gloom, moving in concert.",
        "A pair of enemies bar your path, watching with predatory patience.",
        "Two threats materialize — one to hold your attention, one to exploit the opening.",
    ],
    "group": [
        "Several figures move into position around you. They've been expecting you.",
        "A group of enemies emerges from cover, coordinated and ready.",
        "The arena fills with hostile shapes. This was planned.",
    ],
    "horde": [
        "They come in numbers. Too many to count in the"
        " first heartbeat, too many to ignore in the"
        " second.",
        "A tide of enemies surges forward. The Armillary has"
        " chosen quantity over quality — or perhaps both.",
        "The ground trembles with approaching footsteps. Dozens of eyes gleam in the half-light.",
    ],
}

# ---------------------------------------------------------------------------
# Objective flavor lines — keyed by objective category
# ---------------------------------------------------------------------------

OBJECTIVE_HOOKS: dict[str, list[str]] = {
    "combat": [
        "Nothing survives. That is the condition.",
        "The arena demands blood. Give it what it wants.",
    ],
    "tactical": [
        "Killing alone won't be enough. The arena has set conditions.",
        "Brute force has its place, but the Armillary rewards those who think.",
    ],
    "exploration": [
        "There is something here beyond the enemies. Find it before they find you.",
        "Not every victory is won with a blade.",
    ],
}

# ---------------------------------------------------------------------------
# Armillary scene-setters — keyed by floor depth band
# ---------------------------------------------------------------------------

ARMILLARY_FLAVOR: dict[str, list[str]] = {
    "early": [
        "The Armillary's mechanisms grind overhead, gears turning with mechanical indifference.",
        "A faint hum fills the arena — the Armillary, watching, calculating.",
    ],
    "mid": [
        "The Armillary's presence is heavier here. The air itself seems to press down on you.",
        "Arcs of energy dance between the arena's pillars. The Armillary is paying attention.",
    ],
    "deep": [
        "The Armillary is no longer subtle. Reality warps at"
        " the edges of the arena, and the machine's purpose"
        " is written in every surface.",
        "Power radiates from the walls. This deep, the Armillary doesn't watch — it participates.",
    ],
    "heart": [
        "You have reached the heart of the machine. The"
        " Armillary is everywhere here — above, below,"
        " within.",
        "The boundary between the arena and the Armillary"
        " itself has dissolved. You fight inside a living"
        " engine.",
    ],
}


# ---------------------------------------------------------------------------
# Theme-keyed arrival lines — used when a floor theme is active
# ---------------------------------------------------------------------------

THEME_ARRIVALS: dict[str, list[str]] = {
    "undead_horde": [
        "The stench of decay precedes them. Shambling forms emerge from the shadows,"
        " dead eyes fixed on the living.",
        "A cold wind carries the rattle of bones and the low moan of things that"
        " should be dead. The ground here is restless.",
    ],
    "goblinoid_warband": [
        "The clash of crude weapons and harsh goblin voices echoes ahead. They know"
        " you're coming — and they don't care.",
        "Crude barricades and hastily-set traps mark goblinoid territory. Beyond"
        " them, yellow eyes gleam with malice.",
    ],
    "dragons_lair": [
        "The air shimmers with heat. Claw marks score the walls, and the faint"
        " scent of sulfur hangs in every breath.",
        "Gold glints in the half-light — scattered coins and melted treasures."
        " A dragon has claimed this place.",
    ],
    "demonic_incursion": [
        "Reality tears at the seams. The air is thick with the stench of brimstone"
        " and the whisper of infernal tongues.",
        "The ground cracks and bleeds light. Something is pushing through from the"
        " other side, and it is hungry.",
    ],
    "fey_court": [
        "The light changes — softer, warmer, wrong. Flowers bloom in impossible"
        " colors and the air tastes of honey and lies.",
        "Laughter echoes from nowhere and everywhere. The fey do not fight fairly,"
        " and they do not fight clean.",
    ],
    "elemental_chaos": [
        "The elements war around you. Fire meets ice, stone crashes against wind —"
        " raw power unchained and furious.",
        "The air crackles with competing forces. Elemental energy surges through"
        " every surface, eager to be unleashed.",
    ],
    "aberrant_horror": [
        "Your mind recoils before your eyes can process what waits ahead. Geometry"
        " bends. Angles are wrong. Something thinks at you.",
        "The walls pulse with a rhythm that isn't a heartbeat. Things that"
        " shouldn't exist press against the membrane of reality.",
    ],
    "lycanthrope_pack": [
        "A howl splits the air — primal, hungry, close. The pack has found your"
        " scent, and they hunt as one.",
        "Claw marks score the ground in parallel tracks. The beasts that made them"
        " are near, and they are not alone.",
    ],
    "construct_workshop": [
        "Gears grind and pistons hiss. The workshop's guardians stand motionless"
        " until you cross the threshold — then every eye of glass and steel locks"
        " onto you.",
        "Arcane formulae glow on the walls. The constructs here were built for one"
        " purpose: to stop intruders.",
    ],
    "giant_kin": [
        "The ground shakes with footsteps that belong to something far larger than"
        " you. The ceiling groans under immense weight.",
        "Boulders the size of carriages litter the path — not obstacles, but"
        " ammunition. Giants make war on a different scale.",
    ],
    "serpent_cult": [
        "Serpentine carvings adorn every surface, scales and fangs wrought in"
        " stone. The air is warm, humid, and smells of venom.",
        "Torches flicker in ritual patterns. The cultists knew you would come —"
        " their serpent gods whispered your arrival.",
    ],
    "ooze_infestation": [
        "The walls glisten with moisture that moves against gravity. Something"
        " wet and formless slides through the cracks ahead.",
        "Acid has eaten through the floor in patches. The stone dissolves where"
        " the oozes have passed, leaving trails of corroded ruin.",
    ],
    "spiders_web": [
        "Webs stretch between every surface, thick as rope and sticky as tar."
        " Things wrapped in silk hang from the ceiling, some still twitching.",
        "Chitinous legs tap against stone in the darkness above. The webs vibrate"
        " with each step you take — announcing your presence.",
    ],
    "bandit_raiders": [
        "An ambush site. Overturned carts block the path, and the shadows behind"
        " them are too still, too deliberate.",
        "Steel glints from hidden positions. These aren't monsters — they're"
        " professionals, and they've done this before.",
    ],
    "celestial_test": [
        "Light fills the chamber — warm, golden, and judgmental. Divine guardians"
        " assess your worth with eyes that see through pretense.",
        "The air hums with sacred power. This is not a fight — it is a trial."
        " Prove yourselves, or be found wanting.",
    ],
    "infernal_pact": [
        "Chains rattle in the darkness. The smell of brimstone mingles with the"
        " metallic tang of blood. A contract has been broken — or enforced.",
        "Infernal sigils blaze to life on the floor, each one a binding clause"
        " in a contract older than mortal memory.",
    ],
    "natures_wrath": [
        "The vegetation moves with purpose. Roots coil, thorns extend, and the"
        " green world turns hostile with primal fury.",
        "The forest is alive in ways it shouldn't be. Trees groan, vines lash,"
        " and the very ground tries to swallow your feet.",
    ],
    "shadow_court": [
        "Darkness pools like liquid, deep and hungry. Shapes move within it —"
        " not shadows cast by light, but shadows that exist independently.",
        "The temperature plummets. Your breath comes in ragged clouds as the"
        " darkness presses in, feeding on warmth and hope.",
    ],
    "aquatic_terror": [
        "Water surges across the arena floor. Things break the surface — scaled,"
        " finned, and staring with dead black eyes.",
        "The crash of waves fills the chamber. Salt spray stings your eyes as"
        " creatures of the deep surge onto contested ground.",
    ],
    "clockwork_army": [
        "The click of gears echoes in perfect synchronization. Rank upon rank of"
        " metal soldiers stand at attention, awaiting the signal.",
        "Brass and iron forms march in lockstep, their movements mathematically"
        " precise. There is no fear to exploit, no morale to break.",
    ],
}

# ---------------------------------------------------------------------------
# Arc position flavor — keyed by arena position within the floor
# ---------------------------------------------------------------------------

ARC_POSITION_FLAVOR: dict[str, list[str]] = {
    "opener": [
        "The first signs of trouble appear.",
        "You enter cautiously. The floor reveals its nature.",
    ],
    "middle": [
        "Deeper now. The resistance grows fiercer.",
        "They know you're here. The element of surprise is long gone.",
    ],
    "climax": [
        "This is the heart of the threat. Everything has led to this.",
        "The final stand awaits. Whatever rules this floor waits ahead.",
    ],
}


def _floor_depth_band(floor_number: int) -> str:
    if floor_number <= 5:
        return "early"
    elif floor_number <= 10:
        return "mid"
    elif floor_number <= 16:
        return "deep"
    return "heart"


def _creature_count_category(count: int) -> str:
    if count <= 1:
        return "solo"
    elif count <= 2:
        return "pair"
    elif count <= 6:
        return "group"
    return "horde"


@dataclass
class ReadAloudResult:
    """Generated read-aloud text with its components."""

    full_text: str
    arrival: str
    creature_reveal: str
    objective_hook: str
    armillary_flavor: str


def generate_read_aloud(
    environment_key: str,
    creature_count: int,
    objective_category: str,
    floor_number: int,
    theme_name: str = "",
    theme_id: str = "",
    arc_position: str = "middle",
) -> ReadAloudResult:
    """Generate read-aloud text for an encounter.

    Composes from four pools: arrival, creature reveal, objective hook,
    and armillary flavor. When a theme is active, uses theme-specific
    arrival text 70% of the time.
    """
    # Arrival — prefer theme arrival when a theme is active
    if theme_id and theme_id in THEME_ARRIVALS and random.random() < 0.7:
        arrival = random.choice(THEME_ARRIVALS[theme_id])
    else:
        pool = ARRIVAL_LINES.get(environment_key, DEFAULT_ARRIVALS)
        arrival = random.choice(pool)

    # Arc position flavor
    arc_flavor = random.choice(ARC_POSITION_FLAVOR.get(arc_position, [""]))

    # Creature reveal
    category = _creature_count_category(creature_count)
    creature_reveal = random.choice(CREATURE_REVEALS[category])

    # Objective hook
    obj_pool = OBJECTIVE_HOOKS.get(objective_category, OBJECTIVE_HOOKS["combat"])
    objective_hook = random.choice(obj_pool)

    # Armillary flavor
    depth = _floor_depth_band(floor_number)
    armillary_flavor = random.choice(ARMILLARY_FLAVOR[depth])

    # Compose full text
    parts = [arrival]
    if arc_flavor:
        parts.append(arc_flavor)
    parts.append(creature_reveal)
    parts.append(armillary_flavor)
    full_text = "\n\n".join(parts)

    return ReadAloudResult(
        full_text=full_text,
        arrival=arrival,
        creature_reveal=creature_reveal,
        objective_hook=objective_hook,
        armillary_flavor=armillary_flavor,
    )
