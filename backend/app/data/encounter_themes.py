"""Themed encounter packs for thematic creature groupings.

Each theme defines creature types/tags that work together thematically.
The pipeline can prefer creatures matching the active theme for coherent encounters.
"""

from dataclasses import dataclass, field


@dataclass
class EncounterThemeDef:
    """A themed encounter pack definition."""

    id: str
    name: str
    description: str
    creature_types: list[str]  # SRD creature types (e.g. "undead", "fiend")
    creature_names: list[str]  # Specific creature names to strongly prefer
    min_floor: int = 1
    suggested_environments: list[str] = field(default_factory=list)
    suggested_templates: list[str] = field(default_factory=list)
    floor_weights: dict[int, float] = field(default_factory=dict)


ENCOUNTER_THEMES: dict[str, EncounterThemeDef] = {
    "undead_horde": EncounterThemeDef(
        id="undead_horde",
        name="Undead Horde",
        description="Shambling corpses and restless spirits rise to overwhelm the living.",
        creature_types=["undead"],
        creature_names=[
            "Zombie",
            "Skeleton",
            "Wight",
            "Ghoul",
            "Ghast",
            "Wraith",
            "Specter",
            "Shadow",
            "Mummy",
        ],
        min_floor=1,
        suggested_environments=["haunted_ruins", "sewer_catacomb", "shadowfell_wastes"],
        suggested_templates=["swarm_rush", "attrition", "ambush"],
        floor_weights={1: 1.5, 2: 1.2, 3: 1.0, 4: 0.8},
    ),
    "goblinoid_warband": EncounterThemeDef(
        id="goblinoid_warband",
        name="Goblinoid Warband",
        description="A ragtag warband of goblinoids strikes with cunning and numbers.",
        creature_types=["humanoid"],
        creature_names=["Goblin", "Hobgoblin", "Bugbear", "Goblin Boss", "Hobgoblin Captain"],
        min_floor=1,
        suggested_environments=["forest", "hill", "urban", "sewer_catacomb"],
        suggested_templates=["ambush", "pincer_strike", "swarm_rush"],
        floor_weights={1: 1.5, 2: 1.0, 3: 0.5, 4: 0.3},
    ),
    "dragons_lair": EncounterThemeDef(
        id="dragons_lair",
        name="Dragon's Lair",
        description="A dragon and its servants guard a hoard of treasure.",
        creature_types=["dragon"],
        creature_names=[
            "Kobold",
            "Kobold Inventor",
            "Young Red Dragon",
            "Young Blue Dragon",
            "Young Green Dragon",
            "Young White Dragon",
            "Young Black Dragon",
            "Adult Red Dragon",
            "Adult Blue Dragon",
            "Red Dragon Wyrmling",
            "Blue Dragon Wyrmling",
            "Green Dragon Wyrmling",
            "White Dragon Wyrmling",
            "Black Dragon Wyrmling",
            "Guard Drake",
        ],
        min_floor=2,
        suggested_environments=["volcanic_caldera", "mountain", "crystal_caverns", "lava_tubes"],
        suggested_templates=["dragons_court", "boss", "elite_duel"],
        floor_weights={1: 0.0, 2: 0.8, 3: 1.5, 4: 2.0},
    ),
    "demonic_incursion": EncounterThemeDef(
        id="demonic_incursion",
        name="Demonic Incursion",
        description="Fiends pour through a rift torn in the fabric of reality.",
        creature_types=["fiend"],
        creature_names=[
            "Dretch",
            "Manes",
            "Quasit",
            "Shadow Demon",
            "Barlgura",
            "Vrock",
            "Hezrou",
            "Glabrezu",
            "Nalfeshnee",
            "Marilith",
            "Balor",
        ],
        min_floor=3,
        suggested_environments=[
            "planar",
            "shadowfell_wastes",
            "volcanic_caldera",
            "elemental_nexus",
        ],
        suggested_templates=["swarm_rush", "boss", "attrition"],
        floor_weights={1: 0.0, 2: 0.0, 3: 1.5, 4: 2.0},
    ),
    "fey_court": EncounterThemeDef(
        id="fey_court",
        name="Fey Court",
        description="Mischievous fey creatures weave illusions and enchantments.",
        creature_types=["fey"],
        creature_names=[
            "Pixie",
            "Sprite",
            "Dryad",
            "Satyr",
            "Green Hag",
            "Sea Hag",
            "Night Hag",
            "Blink Dog",
            "Displacer Beast",
        ],
        min_floor=2,
        suggested_environments=["feywild_glade", "forest", "fungal_forest"],
        suggested_templates=["area_denial", "ambush", "guerrilla"],
        floor_weights={1: 0.0, 2: 1.3, 3: 1.5, 4: 1.0},
    ),
    "elemental_chaos": EncounterThemeDef(
        id="elemental_chaos",
        name="Elemental Chaos",
        description="Raw elemental forces rage unchecked through the arena.",
        creature_types=["elemental"],
        creature_names=[
            "Fire Elemental",
            "Water Elemental",
            "Air Elemental",
            "Earth Elemental",
            "Magma Mephit",
            "Ice Mephit",
            "Mud Mephit",
            "Steam Mephit",
            "Dust Mephit",
            "Smoke Mephit",
            "Galeb Duhr",
            "Gargoyle",
            "Salamander",
            "Azer",
            "Xorn",
        ],
        min_floor=2,
        suggested_environments=["planar", "volcanic_caldera", "elemental_nexus", "frozen_lake"],
        suggested_templates=["attrition", "area_denial", "siege"],
        floor_weights={1: 0.0, 2: 1.0, 3: 1.5, 4: 2.0},
    ),
    "aberrant_horror": EncounterThemeDef(
        id="aberrant_horror",
        name="Aberrant Horror",
        description="Things that should not exist slither from the Far Realm.",
        creature_types=["aberration"],
        creature_names=[
            "Mind Flayer",
            "Intellect Devourer",
            "Gibbering Mouther",
            "Nothic",
            "Otyugh",
            "Chuul",
            "Aboleth",
            "Beholder",
            "Spectator",
            "Cloaker",
        ],
        min_floor=3,
        suggested_environments=["underdark", "crystal_caverns", "planar"],
        suggested_templates=["elite_duel", "ambush", "area_denial"],
        floor_weights={1: 0.0, 2: 0.0, 3: 1.3, 4: 2.0},
    ),
    "lycanthrope_pack": EncounterThemeDef(
        id="lycanthrope_pack",
        name="Lycanthrope Pack",
        description="Shapeshifters hunt under the moon, blending among humanoids.",
        creature_types=["humanoid", "monstrosity"],
        creature_names=[
            "Werewolf",
            "Wererat",
            "Wereboar",
            "Weretiger",
            "Werebear",
            "Wolf",
            "Dire Wolf",
            "Winter Wolf",
        ],
        min_floor=2,
        suggested_environments=["forest", "hill", "urban", "arctic"],
        suggested_templates=["pincer_strike", "ambush", "focus_fire"],
        floor_weights={1: 0.0, 2: 1.5, 3: 1.0, 4: 0.5},
    ),
    "construct_workshop": EncounterThemeDef(
        id="construct_workshop",
        name="Construct Workshop",
        description="Magical automatons defend their creator's sanctum.",
        creature_types=["construct"],
        creature_names=[
            "Animated Armor",
            "Flying Sword",
            "Rug of Smothering",
            "Shield Guardian",
            "Clay Golem",
            "Stone Golem",
            "Iron Golem",
            "Flesh Golem",
            "Helmed Horror",
        ],
        min_floor=2,
        suggested_environments=["temple_interior", "urban", "haunted_ruins"],
        suggested_templates=["hold_and_flank", "elite_duel", "siege"],
        floor_weights={1: 0.0, 2: 1.2, 3: 1.5, 4: 1.0},
    ),
    "giant_kin": EncounterThemeDef(
        id="giant_kin",
        name="Giant Kin",
        description="Towering brutes shatter the ground with every step.",
        creature_types=["giant"],
        creature_names=[
            "Ogre",
            "Troll",
            "Hill Giant",
            "Stone Giant",
            "Frost Giant",
            "Fire Giant",
            "Cloud Giant",
            "Storm Giant",
            "Ettin",
            "Half-Ogre",
            "Cyclops",
        ],
        min_floor=2,
        suggested_environments=["mountain", "arctic", "hill", "cloud_palace"],
        suggested_templates=["elite_duel", "boss", "hold_and_flank"],
        floor_weights={1: 0.0, 2: 1.0, 3: 1.5, 4: 1.2},
    ),
    "serpent_cult": EncounterThemeDef(
        id="serpent_cult",
        name="Serpent Cult",
        description="Yuan-ti schemers and their scaled servants lie in ambush.",
        creature_types=["monstrosity", "humanoid"],
        creature_names=[
            "Yuan-Ti Pureblood",
            "Yuan-Ti Malison",
            "Yuan-Ti Abomination",
            "Giant Constrictor Snake",
            "Giant Poisonous Snake",
            "Medusa",
            "Basilisk",
            "Cockatrice",
        ],
        min_floor=2,
        suggested_environments=["swamp", "temple_interior", "desert"],
        suggested_templates=["ambush", "area_denial", "guerrilla"],
        floor_weights={1: 0.0, 2: 1.3, 3: 1.2, 4: 0.8},
    ),
    "ooze_infestation": EncounterThemeDef(
        id="ooze_infestation",
        name="Ooze Infestation",
        description="Corrosive slimes ooze through every crack and crevice.",
        creature_types=["ooze"],
        creature_names=[
            "Gelatinous Cube",
            "Black Pudding",
            "Ochre Jelly",
            "Gray Ooze",
            "Green Slime",
        ],
        min_floor=1,
        suggested_environments=["sewer_catacomb", "underdark", "fungal_forest"],
        suggested_templates=["attrition", "area_denial", "ambush"],
        floor_weights={1: 1.0, 2: 1.3, 3: 1.0, 4: 0.5},
    ),
    "spiders_web": EncounterThemeDef(
        id="spiders_web",
        name="Spider's Web",
        description="Chitinous horrors lurk in webs of sticky silk.",
        creature_types=["beast", "monstrosity"],
        creature_names=[
            "Giant Spider",
            "Phase Spider",
            "Drider",
            "Ettercap",
            "Giant Wolf Spider",
            "Swarm of Insects",
        ],
        min_floor=1,
        suggested_environments=["forest", "underdark", "fungal_forest", "sewer_catacomb"],
        suggested_templates=["ambush", "guerrilla", "area_denial"],
        floor_weights={1: 1.3, 2: 1.2, 3: 0.8, 4: 0.5},
    ),
    "bandit_raiders": EncounterThemeDef(
        id="bandit_raiders",
        name="Bandit Raiders",
        description="Cutthroats and brigands attack from the shadows.",
        creature_types=["humanoid"],
        creature_names=[
            "Bandit",
            "Bandit Captain",
            "Thug",
            "Assassin",
            "Spy",
            "Scout",
            "Veteran",
            "Knight",
            "Berserker",
            "Gladiator",
        ],
        min_floor=1,
        suggested_environments=["urban", "hill", "forest", "ship_deck", "coastal"],
        suggested_templates=["ambush", "pincer_strike", "swarm_rush"],
        floor_weights={1: 1.5, 2: 1.0, 3: 0.5, 4: 0.3},
    ),
    "celestial_test": EncounterThemeDef(
        id="celestial_test",
        name="Celestial Test",
        description="Divine guardians test the party's worthiness.",
        creature_types=["celestial"],
        creature_names=[
            "Deva",
            "Couatl",
            "Unicorn",
            "Pegasus",
            "Planetar",
            "Solar",
        ],
        min_floor=3,
        suggested_environments=["feywild_glade", "cloud_palace", "temple_interior"],
        suggested_templates=["elite_duel", "boss", "focus_fire"],
        floor_weights={1: 0.0, 2: 0.0, 3: 1.0, 4: 1.5},
    ),
    "infernal_pact": EncounterThemeDef(
        id="infernal_pact",
        name="Infernal Pact",
        description="Devils enforce contracts with fire and chain.",
        creature_types=["fiend"],
        creature_names=[
            "Imp",
            "Bearded Devil",
            "Barbed Devil",
            "Chain Devil",
            "Bone Devil",
            "Horned Devil",
            "Erinyes",
            "Ice Devil",
            "Pit Fiend",
            "Hell Hound",
            "Nightmare",
        ],
        min_floor=3,
        suggested_environments=["planar", "volcanic_caldera", "lava_tubes"],
        suggested_templates=["hold_and_flank", "boss", "elite_duel"],
        floor_weights={1: 0.0, 2: 0.0, 3: 1.3, 4: 2.0},
    ),
    "natures_wrath": EncounterThemeDef(
        id="natures_wrath",
        name="Nature's Wrath",
        description="The wild itself turns hostile, animated by primal fury.",
        creature_types=["plant"],
        creature_names=[
            "Treant",
            "Shambling Mound",
            "Vine Blight",
            "Twig Blight",
            "Needle Blight",
            "Awakened Tree",
            "Awakened Shrub",
        ],
        min_floor=1,
        suggested_environments=["forest", "swamp", "fungal_forest", "feywild_glade"],
        suggested_templates=["attrition", "area_denial", "swarm_rush"],
        floor_weights={1: 1.2, 2: 1.3, 3: 1.0, 4: 0.5},
    ),
    "shadow_court": EncounterThemeDef(
        id="shadow_court",
        name="Shadow Court",
        description="Creatures of darkness feed on fear and despair.",
        creature_types=["undead", "fiend"],
        creature_names=[
            "Shadow",
            "Wraith",
            "Shadow Demon",
            "Specter",
            "Banshee",
            "Nightwalker",
            "Bodak",
            "Allip",
        ],
        min_floor=3,
        suggested_environments=["shadowfell_wastes", "underdark", "haunted_ruins"],
        suggested_templates=["ambush", "guerrilla", "attrition"],
        floor_weights={1: 0.0, 2: 0.0, 3: 1.5, 4: 2.0},
    ),
    "aquatic_terror": EncounterThemeDef(
        id="aquatic_terror",
        name="Aquatic Terror",
        description="Creatures of the deep surge onto land and shore.",
        creature_types=["monstrosity", "humanoid"],
        creature_names=[
            "Sahuagin",
            "Sahuagin Priestess",
            "Sahuagin Baron",
            "Merrow",
            "Sea Hag",
            "Water Elemental",
            "Hunter Shark",
            "Giant Octopus",
            "Aboleth",
            "Kraken",
        ],
        min_floor=2,
        suggested_environments=["coastal", "underwater", "ship_deck", "swamp"],
        suggested_templates=["swarm_rush", "siege", "boss"],
        floor_weights={1: 0.0, 2: 1.3, 3: 1.2, 4: 1.0},
    ),
    "clockwork_army": EncounterThemeDef(
        id="clockwork_army",
        name="Clockwork Army",
        description="Precisely ordered constructs march in formation.",
        creature_types=["construct"],
        creature_names=[
            "Modron",
            "Monodrone",
            "Duodrone",
            "Tridrone",
            "Quadrone",
            "Pentadrone",
            "Shield Guardian",
            "Helmed Horror",
            "Iron Golem",
        ],
        min_floor=3,
        suggested_environments=["planar", "temple_interior", "cloud_palace"],
        suggested_templates=["hold_and_flank", "siege", "swarm_rush"],
        floor_weights={1: 0.0, 2: 0.0, 3: 1.2, 4: 1.5},
    ),
}


def get_theme(theme_id: str) -> EncounterThemeDef | None:
    """Look up a theme by ID."""
    return ENCOUNTER_THEMES.get(theme_id)


def get_all_themes() -> list[EncounterThemeDef]:
    """Return all theme definitions."""
    return list(ENCOUNTER_THEMES.values())


def get_themes_for_floor(floor_number: int) -> list[EncounterThemeDef]:
    """Return themes available at the given floor number."""
    return [t for t in ENCOUNTER_THEMES.values() if t.min_floor <= floor_number]


def select_theme_for_floor(
    biome: str | None,
    floor_number: int,
    used_themes: list[str] | None = None,
) -> EncounterThemeDef | None:
    """Select a single theme for an entire floor based on biome and depth.

    Prefers themes whose suggested_environments overlap with the biome's
    environment list, avoids recently used themes, and weights by tier.
    Returns None only if no theme matches at all.
    """
    import random

    from app.data.environments import get_environments_in_biome

    available = get_themes_for_floor(floor_number)
    if not available:
        return None

    # Get environments in this biome for overlap scoring
    biome_envs = set(get_environments_in_biome(biome)) if biome else set()

    # Map floor_number to tier for floor_weights lookup
    if floor_number <= 4:
        tier = 1
    elif floor_number <= 10:
        tier = 2
    elif floor_number <= 16:
        tier = 3
    else:
        tier = 4

    # Exclude recently used themes (last 3 floors) unless all are exhausted
    used = set(used_themes or [])
    candidates = [t for t in available if t.id not in used]
    if not candidates:
        candidates = available

    # Score each theme
    weighted: list[tuple[EncounterThemeDef, float]] = []
    for theme in candidates:
        # Base weight from tier
        base = theme.floor_weights.get(tier, 1.0)
        if base <= 0:
            continue

        # Biome overlap bonus: how many of the theme's suggested_environments
        # overlap with this biome's environment list
        if biome_envs and theme.suggested_environments:
            overlap = len(biome_envs & set(theme.suggested_environments))
            biome_bonus = 1.0 + overlap * 0.5
        else:
            biome_bonus = 1.0

        weighted.append((theme, base * biome_bonus))

    if not weighted:
        return None

    themes, weights = zip(*weighted)
    return random.choices(list(themes), weights=list(weights), k=1)[0]


def select_theme_for_environment(
    environment: str,
    floor_number: int,
) -> EncounterThemeDef | None:
    """Select a theme that fits the given environment and floor.

    Returns None if no theme is a strong fit (encounter will be unthemed).
    """
    import random

    available = get_themes_for_floor(floor_number)
    matching = [t for t in available if environment in t.suggested_environments]

    if not matching:
        return None

    # Weight by floor_weights if available
    weighted: list[tuple[EncounterThemeDef, float]] = []
    for theme in matching:
        weight = theme.floor_weights.get(floor_number, 1.0)
        if weight > 0:
            weighted.append((theme, weight))

    if not weighted:
        return None

    themes, weights = zip(*weighted)
    return random.choices(list(themes), weights=list(weights), k=1)[0]
