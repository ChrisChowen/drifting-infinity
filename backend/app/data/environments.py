"""Environment definitions for D&D encounter map/terrain generation.

Each environment provides terrain features for DM map setup,
suggested encounter templates that work well in the space,
and concrete map layout ideas.
"""

from dataclasses import dataclass, field


@dataclass
class EnvironmentDef:
    key: str
    name: str
    description: str
    terrain_features: list[str]  # 3-5 DM map-setup hints
    suggested_templates: list[str]  # encounter templates that work well
    map_suggestions: list[str]  # specific map layout ideas
    floor_weights: dict[int, float] = field(default_factory=dict)  # floor_num -> weight multiplier


ENVIRONMENTS: dict[str, EnvironmentDef] = {
    "forest": EnvironmentDef(
        key="forest",
        name="Dense Forest",
        description="Thick canopy blocks line of sight; narrow game trails wind between ancient trunks.",
        terrain_features=[
            "Dense tree cover providing three-quarters cover every 15 ft",
            "Narrow winding trails (5 ft wide) between trees",
            "Thick underbrush creating difficult terrain patches",
            "Fallen logs usable as half cover or elevated ground",
            "Canopy overhead blocks flying above 30 ft",
        ],
        suggested_templates=["ambush", "hold_and_flank"],
        map_suggestions=[
            "A forest clearing ringed by trees with two narrow trail entrances",
            "A dense thicket bisected by a shallow stream with a fallen tree bridge",
            "An old druid grove with standing stones among the roots",
        ],
        floor_weights={1: 1.5, 2: 1.0, 3: 0.5, 4: 0.3},
    ),
    "grassland": EnvironmentDef(
        key="grassland",
        name="Open Grassland",
        description="Wide open plains with scattered boulders and gentle rolling hills providing minimal cover.",
        terrain_features=[
            "Open sight lines out to 120 ft in most directions",
            "Scattered boulders providing half cover",
            "Gentle hills giving 10 ft elevation advantage",
            "Tall grass (waist height) granting light obscurement in patches",
        ],
        suggested_templates=["focus_fire", "attrition"],
        map_suggestions=[
            "A windswept hilltop with boulders arranged in a rough semicircle",
            "A flat plain with a lone ancient oak and a stone-lined well",
            "Rolling hills with a dirt road cutting through the center",
        ],
        floor_weights={1: 1.3, 2: 1.0, 3: 0.7, 4: 0.4},
    ),
    "urban": EnvironmentDef(
        key="urban",
        name="Urban Streets",
        description="Tight city streets, rooftops, and cluttered market stalls create a vertical battlefield.",
        terrain_features=[
            "Narrow alleyways (10 ft wide) with full cover at corners",
            "Rooftops accessible via ladders, 15-20 ft elevation",
            "Market stalls and carts providing half cover and difficult terrain",
            "Building interiors accessible through doors and windows",
            "Sewer grate entrances for underground flanking",
        ],
        suggested_templates=["ambush", "area_denial"],
        map_suggestions=[
            "A market square surrounded by two-story buildings with rooftop access",
            "A narrow alley intersection with a collapsed building creating rubble cover",
            "A tavern interior and the street outside, connected by doors and windows",
        ],
        floor_weights={1: 0.8, 2: 1.2, 3: 1.0, 4: 0.6},
    ),
    "underdark": EnvironmentDef(
        key="underdark",
        name="Underdark Caverns",
        description="Vast subterranean chambers with stalactites, chasms, and eerie bioluminescent fungi.",
        terrain_features=[
            "Stalactites and stalagmites providing three-quarters cover",
            "Deep chasms (40+ ft) splitting the battlefield",
            "Bioluminescent fungi casting dim light in 10 ft patches",
            "Narrow natural bridges over underground rivers",
            "Echo chambers that impose disadvantage on Perception checks",
        ],
        suggested_templates=["ambush", "area_denial"],
        map_suggestions=[
            "A large cavern with a 30 ft chasm crossed by two narrow stone bridges",
            "A fungi-lit grotto with pools of dark water and dripping stalactites",
            "A carved drow outpost built into the cavern walls with multiple levels",
        ],
        floor_weights={1: 0.3, 2: 0.8, 3: 1.5, 4: 1.8},
    ),
    "mountain": EnvironmentDef(
        key="mountain",
        name="Mountain Pass",
        description="Treacherous cliff edges, narrow switchback passes, and loose scree create perilous terrain.",
        terrain_features=[
            "Cliff edges with 60+ ft drops on one or both sides",
            "Narrow switchback paths (10 ft wide) limiting movement",
            "Loose rocks and scree creating difficult terrain",
            "Boulder fields providing full cover",
            "High elevation thin air (optional exhaustion at DM discretion)",
        ],
        suggested_templates=["hold_and_flank", "focus_fire"],
        map_suggestions=[
            "A narrow mountain pass with cliff walls on both sides and boulders for cover",
            "A wide ledge overlooking a valley, with cave entrances in the cliff face",
            "A crumbling stone bridge spanning a deep mountain gorge",
        ],
        floor_weights={1: 0.7, 2: 1.2, 3: 1.3, 4: 0.8},
    ),
    "swamp": EnvironmentDef(
        key="swamp",
        name="Murky Swamp",
        description="Fog-choked wetlands with waist-deep water, gnarled trees, and treacherous footing.",
        terrain_features=[
            "Waist-deep water creating difficult terrain across most of the map",
            "Patches of solid ground (islands) scattered throughout",
            "Thick fog imposing light obscurement beyond 30 ft",
            "Gnarled mangrove roots providing half cover",
            "Hidden sinkholes (DC 12 Perception or sink 5 ft)",
        ],
        suggested_templates=["attrition", "area_denial"],
        map_suggestions=[
            "A series of muddy islands connected by submerged log walkways",
            "A half-sunken ruin rising from the swamp with flooded lower levels",
            "A fog-blanketed clearing around a massive dead tree with exposed roots",
        ],
        floor_weights={1: 0.6, 2: 1.0, 3: 1.2, 4: 0.7},
    ),
    "coastal": EnvironmentDef(
        key="coastal",
        name="Rocky Coast",
        description="Sandy shores give way to tide pools and rocky outcrops battered by crashing waves.",
        terrain_features=[
            "Sandy beach (normal movement) transitioning to rocky terrain (difficult)",
            "Tide pools creating shallow difficult terrain pockets",
            "Rocky outcrops providing half to three-quarters cover",
            "Crashing waves (initiative count 20) that push creatures 10 ft shoreward",
        ],
        suggested_templates=["hold_and_flank", "attrition"],
        map_suggestions=[
            "A crescent-shaped beach with sea caves accessible at low tide",
            "A rocky headland with a shipwreck half-submerged offshore",
            "Tidal flats dotted with rock pillars and a stone jetty",
        ],
        floor_weights={1: 0.8, 2: 1.0, 3: 0.8, 4: 0.5},
    ),
    "desert": EnvironmentDef(
        key="desert",
        name="Scorching Desert",
        description="Shifting sand dunes, rocky mesas, and punishing heat sap strength from the unprepared.",
        terrain_features=[
            "Sand dunes creating difficult terrain and blocking line of sight",
            "Rocky mesa providing high ground (20 ft elevation)",
            "Extreme heat (DC 10 Constitution save each hour or gain exhaustion)",
            "Oasis with palm trees providing shade and half cover",
            "Sandstorm possibility (heavy obscurement, 2d4 slashing per round)",
        ],
        suggested_templates=["attrition", "focus_fire"],
        map_suggestions=[
            "A desert canyon with high mesa walls and a narrow floor",
            "An oasis surrounded by sand dunes with ancient ruins half-buried",
            "A flat salt pan with a lonely rock formation in the center",
        ],
        floor_weights={1: 0.5, 2: 1.0, 3: 1.2, 4: 0.8},
    ),
    "arctic": EnvironmentDef(
        key="arctic",
        name="Frozen Wastes",
        description="Blinding white ice sheets, howling blizzards, and frozen lakes hide deadly dangers.",
        terrain_features=[
            "Ice sheets creating slippery difficult terrain (DC 10 Dex or fall prone)",
            "Blizzard conditions imposing heavy obscurement beyond 20 ft",
            "Frozen lake surface (AC 10, 15 HP per 5-ft section before breaking)",
            "Snow banks providing half cover and concealment",
            "Crevasses hidden under snow (DC 14 Perception to spot)",
        ],
        suggested_templates=["attrition", "hold_and_flank"],
        map_suggestions=[
            "A frozen lake with an ice cave entrance on one shore",
            "A snow-covered mountain pass during a howling blizzard",
            "The ruins of a frost giant outpost half-buried in glacial ice",
        ],
        floor_weights={1: 0.4, 2: 0.8, 3: 1.3, 4: 1.0},
    ),
    "hill": EnvironmentDef(
        key="hill",
        name="Rolling Hills",
        description="Gentle hills dotted with sparse trees and hidden cave entrances reward tactical elevation play.",
        terrain_features=[
            "Rolling hills providing 10-15 ft elevation changes",
            "Sparse trees offering half cover at irregular intervals",
            "Cave entrances (10 ft wide) in hillsides for ambush points",
            "Rocky outcrops at hilltops providing three-quarters cover",
        ],
        suggested_templates=["hold_and_flank", "ambush"],
        map_suggestions=[
            "A trio of grassy hills with a cave entrance in the central hill",
            "A hillside dotted with boulders and a stream running through the valley",
            "An old watchtower ruin on the highest hill overlooking lower slopes",
        ],
        floor_weights={1: 1.2, 2: 1.0, 3: 0.8, 4: 0.5},
    ),
    "planar": EnvironmentDef(
        key="planar",
        name="Planar Rift",
        description="Reality fractures into floating platforms, shifting gravity, and elemental rifts that defy natural law.",
        terrain_features=[
            "Floating stone platforms (10-20 ft across) with 15 ft gaps between them",
            "Gravity shifts: DM can reverse gravity in a 20 ft zone once per round",
            "Elemental rifts that deal 2d6 fire/cold/lightning to creatures ending turn within 5 ft",
            "Shimmering portals that teleport creatures to another point on the map",
            "Reality tears that impose disadvantage on concentration saves within 10 ft",
        ],
        suggested_templates=["boss", "area_denial"],
        map_suggestions=[
            "A ring of floating platforms orbiting a central elemental rift",
            "A shattered plane with gravity pulling in different directions on each fragment",
            "A crystalline bridge spanning the void between two planar anchors",
        ],
        floor_weights={1: 0.1, 2: 0.3, 3: 0.8, 4: 2.5},
    ),
    "underwater": EnvironmentDef(
        key="underwater",
        name="Underwater Depths",
        description="Coral reefs, kelp forests, and underwater caves where combat follows three-dimensional rules.",
        terrain_features=[
            "Full three-dimensional movement (swimming speed or suffocation rules)",
            "Kelp forests creating underwater difficult terrain and light obscurement",
            "Coral formations providing half cover but dealing 1d4 piercing on contact",
            "Underwater caves with air pockets for breathing",
            "Strong currents pushing creatures 10 ft per round in one direction",
        ],
        suggested_templates=["area_denial", "hold_and_flank"],
        map_suggestions=[
            "A sunken temple courtyard surrounded by coral walls with kelp-choked entrances",
            "An underwater cave system with bioluminescent crystals and air pocket chambers",
            "A coral reef maze with a shipwreck at its center",
        ],
        floor_weights={1: 0.1, 2: 0.2, 3: 0.3, 4: 0.4},
    ),
    "volcanic_caldera": EnvironmentDef(
        key="volcanic_caldera",
        name="Volcanic Caldera",
        description="A smoldering caldera where rivers of molten rock carve through blackened stone and the air shimmers with heat.",
        terrain_features=[
            "Lava rivers (10 ft wide) dealing 6d10 fire damage to creatures entering or starting a turn in them",
            "Obsidian outcrops providing three-quarters cover but shattering on critical hits",
            "Sulfurous gas vents (DC 13 Constitution save or poisoned until end of next turn)",
            "Collapsing rock platforms (DM rolls d6 each round; on a 1 the platform crumbles)",
            "Intense ambient heat dealing 1d4 fire damage per round without fire resistance",
        ],
        suggested_templates=["attrition", "boss"],
        map_suggestions=[
            "A wide caldera floor split by two converging lava rivers with obsidian islands between them",
            "A volcanic vent chamber with a central magma pool and a ring of crumbling stone ledges",
            "A blackened ridge overlooking a lava lake, crossed by a narrow basalt bridge",
        ],
        floor_weights={1: 0.1, 2: 0.3, 3: 1.2, 4: 1.8},
    ),
    "haunted_ruins": EnvironmentDef(
        key="haunted_ruins",
        name="Haunted Ruins",
        description="Crumbling stonework and broken arches stand among spectral echoes; the dead do not rest quietly here.",
        terrain_features=[
            "Crumbling walls providing half cover that may collapse (DC 12 Dex save when struck)",
            "Cold spots (10 ft radius) that deal 1d6 cold damage to living creatures entering them",
            "Spectral apparitions that impose disadvantage on Wisdom saves within 15 ft",
            "Whispered warnings giving vague clues or false directions (DM discretion)",
            "Rubble piles creating difficult terrain throughout the ruins",
        ],
        suggested_templates=["ambush", "area_denial"],
        map_suggestions=[
            "A shattered great hall with collapsed pillars, a cracked mosaic floor, and a ghostly throne",
            "A ruined courtyard overgrown with dead vines, surrounded by broken tower stumps",
            "A partially collapsed crypt with open sarcophagi and flickering phantom lights",
        ],
        floor_weights={1: 0.4, 2: 1.2, 3: 1.3, 4: 0.7},
    ),
    "feywild_glade": EnvironmentDef(
        key="feywild_glade",
        name="Feywild Glade",
        description="Shimmering colours dance across impossible flora and the boundaries between illusion and reality blur dangerously.",
        terrain_features=[
            "Enchanted flora that shifts position between rounds (DM moves one terrain piece 10 ft)",
            "Illusion-blurred terrain requiring DC 13 Investigation to identify real paths",
            "Fey crossings (shimmering archways) that teleport creatures 30 ft in a random direction",
            "Bioluminescent flowers casting bright light in 10 ft, dim light for another 10 ft",
            "Charmed glades where creatures must succeed on DC 12 Wisdom save or waste movement dancing",
        ],
        suggested_templates=["area_denial", "focus_fire"],
        map_suggestions=[
            "A radiant clearing ringed by giant toadstools with a crystal-clear pool at the centre",
            "A twisting path through luminous trees where the trail loops back on itself",
            "A fey lord's garden with hedge-maze walls of living thornbushes and a gazebo at the heart",
        ],
        floor_weights={1: 0.2, 2: 1.0, 3: 1.3, 4: 0.8},
    ),
    "shadowfell_wastes": EnvironmentDef(
        key="shadowfell_wastes",
        name="Shadowfell Wastes",
        description="A bleak expanse drained of colour where life-sapping mists roll across grey desolation and despair is palpable.",
        terrain_features=[
            "Life-draining mist (DC 12 Constitution save or take 1d6 necrotic at start of turn)",
            "Despair aura imposing disadvantage on Charisma saves within 30 ft of shadow pools",
            "Shadow pools that spawn 1d4 shadows if a creature ends its turn within 5 ft",
            "Grey desolation — featureless terrain with no natural cover for 60 ft stretches",
            "Dim light everywhere; bright light sources have their radius halved",
        ],
        suggested_templates=["attrition", "ambush"],
        map_suggestions=[
            "A barren grey plain with scattered shadow pools and a ruined obelisk at the centre",
            "A crumbling shadow-road lined with dead trees leading to a dark fortress gate",
            "A hollow depression filled with rolling black mist and jagged tombstone-like rocks",
        ],
        floor_weights={1: 0.1, 2: 0.4, 3: 1.2, 4: 1.8},
    ),
    "temple_interior": EnvironmentDef(
        key="temple_interior",
        name="Temple Interior",
        description="Grand stone pillars support a vaulted ceiling; sacred wards still flicker along the altar dais.",
        terrain_features=[
            "Stone pillars (5 ft wide) providing three-quarters cover at regular intervals",
            "Raised altar platform (5 ft elevation) at one end of the chamber",
            "Sacred ward zones (10 ft radius) that deal 2d6 radiant damage to undead or fiends entering",
            "Narrow aisles (10 ft wide) between pew rows creating channelled movement",
            "Heavy wooden doors that can be barred (AC 15, 25 HP) at chamber entrances",
        ],
        suggested_templates=["hold_and_flank", "area_denial"],
        map_suggestions=[
            "A long nave flanked by stone pillars leading to a raised altar with side chapels",
            "A circular sanctum with a sunken ritual circle in the centre and balcony seating above",
            "A ruined temple where half the roof has collapsed, mixing interior and open-air terrain",
        ],
        floor_weights={1: 1.3, 2: 1.2, 3: 0.5, 4: 0.3},
    ),
    "ship_deck": EnvironmentDef(
        key="ship_deck",
        name="Ship Deck & Docks",
        description="Salt-crusted planks rock beneath your feet as rigging creaks overhead and waves crash against the hull.",
        terrain_features=[
            "Rocking deck requiring DC 10 Dexterity save when taking the Dash action or fall prone",
            "Rigging and masts climbable (Athletics DC 12) providing 20 ft elevation and half cover",
            "Narrow gangplanks (5 ft wide) connecting ship to dock or ship to ship",
            "Cargo crates and barrels providing half cover and throwable improvised weapons",
            "Open water surrounding the vessel (swimming or drowning rules apply)",
        ],
        suggested_templates=["hold_and_flank", "focus_fire"],
        map_suggestions=[
            "A three-masted galleon with fore and aft castles, mid-deck cargo, and boarding planks",
            "Two ships lashed together with gangplanks, each with different deck elevations",
            "A busy dock with a moored ship, warehouse entrance, and crane for vertical movement",
        ],
        floor_weights={1: 1.4, 2: 1.0, 3: 0.4, 4: 0.2},
    ),
    "crystal_caverns": EnvironmentDef(
        key="crystal_caverns",
        name="Crystal Caverns",
        description="Towering crystal formations refract light into prismatic beams and hum with latent arcane resonance.",
        terrain_features=[
            "Reflective crystal surfaces that redirect line-of-sight spells (DM adjudicates angles)",
            "Light refraction zones casting bright prismatic light and imposing disadvantage on Stealth",
            "Resonating crystals that amplify Thunder damage by 1d6 within 15 ft",
            "Narrow crystal tunnels (5 ft wide, 7 ft tall) limiting Large+ creatures",
            "Unstable crystal clusters (AC 12, 10 HP) that shatter into 2d4 piercing in 10 ft",
        ],
        suggested_templates=["focus_fire", "area_denial"],
        map_suggestions=[
            "A grand crystal chamber with towering formations, light-beam corridors, and a central geode",
            "A network of narrow crystal tunnels opening into a wide cavern with a reflecting pool",
            "A spiralling descent through crystal-studded rock with ledges and a glowing crystal heart below",
        ],
        floor_weights={1: 0.2, 2: 1.0, 3: 1.3, 4: 0.9},
    ),
    "fungal_forest": EnvironmentDef(
        key="fungal_forest",
        name="Fungal Forest",
        description="Giant mushrooms tower overhead, their caps forming a spongy canopy while luminous spores drift on still air.",
        terrain_features=[
            "Giant mushroom caps (15-20 ft tall) providing full cover beneath and platforms above",
            "Spore clouds (10 ft radius) requiring DC 12 Constitution save or blinded until end of turn",
            "Bioluminescent fungal paths casting dim light in 20 ft corridors",
            "Springy mycelium ground reducing fall damage by half but muffling footsteps (Stealth advantage)",
            "Acidic puddles near decomposing fungi dealing 1d6 acid to creatures stepping in them",
        ],
        suggested_templates=["ambush", "attrition"],
        map_suggestions=[
            "A towering mushroom grove with climbable stalks and cap-top platforms connected by tendrils",
            "A fungal-choked cavern with a narrow clear path winding between spore-belching growths",
            "A vast mycelium web spanning a chasm with bioluminescent nodes marking safe footholds",
        ],
        floor_weights={1: 0.3, 2: 1.0, 3: 1.2, 4: 0.8},
    ),
    "elemental_nexus": EnvironmentDef(
        key="elemental_nexus",
        name="Elemental Nexus",
        description="Four elemental forces collide in a maelstrom of fire, ice, lightning, and stone where reality buckles under the strain.",
        terrain_features=[
            "Colliding elemental zones (fire/cold/lightning/earth) each occupying a quadrant of the map",
            "Unstable rifts that randomly teleport creatures 20 ft when stepped on (DC 14 Dex to avoid)",
            "Energy surges dealing 3d6 damage of a random element at initiative count 10 in a 15 ft radius",
            "Floating debris platforms (10 ft across) that orbit the nexus centre",
            "A central convergence point that amplifies all elemental spell damage by 50% within 10 ft",
        ],
        suggested_templates=["boss", "area_denial"],
        map_suggestions=[
            "A four-quadrant arena — fire, ice, storm, earth — with a volatile nexus core at the centre",
            "A shattered planar crossroads with floating rock islands orbiting a swirling elemental vortex",
            "A ruined arcane laboratory where containment circles have failed and elements run wild",
        ],
        floor_weights={1: 0.0, 2: 0.1, 3: 0.4, 4: 2.5},
    ),
    "frozen_lake": EnvironmentDef(
        key="frozen_lake",
        name="Frozen Lake",
        description="A vast sheet of ice groans underfoot; snow-dusted banks and hidden ice caves offer scant refuge from the biting wind.",
        terrain_features=[
            "Ice surface requiring DC 10 Dexterity (Acrobatics) check when moving more than half speed or fall prone",
            "Cracks in the ice (DC 14 Perception to spot) — breaking through drops into frigid water (1d10 cold per round)",
            "Snow banks along the shore providing half cover and difficult terrain",
            "Ice caves at the lake edge offering full cover and choke points",
            "Howling wind imposing disadvantage on ranged attacks beyond 30 ft",
        ],
        suggested_templates=["attrition", "hold_and_flank"],
        map_suggestions=[
            "A broad frozen lake with a rocky island in the centre and ice caves along the north shore",
            "A frozen river bend with snow-covered banks, fallen trees, and thin ice near the centre",
            "A glacial shelf above a frozen lake with a winding ice-stair descent to the surface",
        ],
        floor_weights={1: 0.3, 2: 1.0, 3: 1.2, 4: 0.7},
    ),
    "lava_tubes": EnvironmentDef(
        key="lava_tubes",
        name="Lava Tubes",
        description="Narrow volcanic tunnels twist through the earth, their walls still glowing with residual heat and pools of magma.",
        terrain_features=[
            "Narrow tunnels (10 ft wide, 8 ft tall) restricting Large+ creature movement",
            "Magma pools along tunnel edges dealing 6d10 fire to creatures entering them",
            "Obsidian shard floors dealing 1d4 piercing to creatures moving without footwear",
            "Heat shimmer imposing disadvantage on ranged attacks beyond 30 ft",
            "Unstable ceiling sections (DM triggers collapse: 4d6 bludgeoning, DC 14 Dex half, in 10 ft area)",
        ],
        suggested_templates=["attrition", "boss"],
        map_suggestions=[
            "A long lava tube with side alcoves, a magma stream along one wall, and a widened boss chamber at the end",
            "A branching tunnel system with dead ends, magma pools, and a central junction room",
            "A vertical lava tube with spiral ledges descending around a central magma column",
        ],
        floor_weights={1: 0.1, 2: 0.3, 3: 1.3, 4: 1.6},
    ),
    "cloud_palace": EnvironmentDef(
        key="cloud_palace",
        name="Cloud Palace",
        description="Gleaming marble platforms float among the clouds, connected by arcing bridges over a dizzying open sky.",
        terrain_features=[
            "Floating marble platforms (15-25 ft across) with 10-20 ft gaps of open sky between them",
            "Cloud banks providing heavy obscurement in 20 ft zones that drift 10 ft per round",
            "Open sky drops — falling off a platform means plummeting unless flight or feather fall is available",
            "Wind gusts at initiative count 20 pushing creatures 10 ft toward the nearest edge (DC 12 Strength save)",
            "Ornate pillars and balustrades on platforms providing half cover",
        ],
        suggested_templates=["focus_fire", "boss"],
        map_suggestions=[
            "A grand cloud palace courtyard with four floating platforms and a central dais connected by marble bridges",
            "A sky-throne room with a massive central platform, smaller orbiting platforms, and cloud cover below",
            "A crumbling celestial bridge with missing sections, floating debris, and howling crosswinds",
        ],
        floor_weights={1: 0.0, 2: 0.1, 3: 0.5, 4: 2.5},
    ),
    "sewer_catacomb": EnvironmentDef(
        key="sewer_catacomb",
        name="Sewer & Catacomb",
        description="Dank tunnels reek of decay; waste channels flow between crumbling burial alcoves where vermin skitter in the dark.",
        terrain_features=[
            "Narrow tunnels (10 ft wide) with arched ceilings limiting vertical movement",
            "Waste channels (5 ft wide, 3 ft deep) creating difficult terrain and requiring DC 10 Con save vs. disease on submersion",
            "Rat swarms that emerge from grates (DM triggers 1d4 swarms as a lair action)",
            "Crumbling burial alcoves providing half cover and possible undead ambush points",
            "Locked iron grates (AC 17, 30 HP, DC 15 Thieves' Tools) controlling access between sections",
        ],
        suggested_templates=["ambush", "area_denial"],
        map_suggestions=[
            "A sewer junction where four tunnels meet at a central cistern with walkways along the edges",
            "A catacomb corridor lined with skeletal alcoves opening into a bone-littered ossuary chamber",
            "A flooded sewer section with raised stone walkways, grate-covered side passages, and a collapsed ceiling exit",
        ],
        floor_weights={1: 1.3, 2: 1.2, 3: 0.5, 4: 0.2},
    ),
}


# ── Biome Groups ─────────────────────────────────────────────────────
# Each floor picks one biome; arenas within that floor draw environments
# from the biome's variant list (no repeats until all variants exhausted).

BIOME_GROUPS: dict[str, list[str]] = {
    "arctic": ["arctic", "frozen_lake"],
    "forest": ["forest", "fungal_forest", "feywild_glade"],
    "underground": ["underdark", "crystal_caverns", "lava_tubes", "sewer_catacomb"],
    "water": ["coastal", "underwater", "swamp"],
    "mountain": ["mountain", "volcanic_caldera"],
    "urban": ["urban", "haunted_ruins", "temple_interior", "ship_deck"],
    "desert": ["desert"],
    "plains": ["grassland", "hill"],
    "planar": ["planar", "elemental_nexus", "shadowfell_wastes", "cloud_palace"],
}


def get_biome_for_environment(env_key: str) -> str | None:
    """Return which biome an environment belongs to, or None."""
    for biome, envs in BIOME_GROUPS.items():
        if env_key in envs:
            return biome
    return None


def get_environments_in_biome(biome: str) -> list[str]:
    """Return all environment keys in a biome."""
    return BIOME_GROUPS.get(biome, [])


def get_environment(key: str) -> EnvironmentDef | None:
    """Get an environment definition by key."""
    return ENVIRONMENTS.get(key)


def get_all_environments() -> list[EnvironmentDef]:
    """Get all environment definitions."""
    return list(ENVIRONMENTS.values())
