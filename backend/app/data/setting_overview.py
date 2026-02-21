"""Campaign setting overview — the Armillary as a living place.

Provides the introductory text, cosmology, faction descriptions, and
key NPC profiles that a DM needs to present the Armillary as a coherent
campaign setting rather than a random dungeon.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Campaign Introduction
# ---------------------------------------------------------------------------

CAMPAIGN_INTRODUCTION = {
    "title": "The Drifting Infinity",
    "tagline": "A procedural D&D campaign where the dungeon learns from you.",
    "opening_text": (
        "Somewhere between the planes, suspended in the space where "
        "realities overlap, there exists a machine. Not a machine of "
        "gears and steam — though it has those — but a machine of "
        "purpose. It was built to answer a single question: can mortal "
        "beings exceed their design?"
        "\n\n"
        "The machine is called the Armillary, and it has been running "
        "its experiment for millennia. It summons adventurers from "
        "across the Material Plane, draws them into its corridors, and "
        "tests them. Not to destroy them — though many are destroyed — "
        "but to measure them. Every spell cast, every wound survived, "
        "every death endured is data. Beautiful, violent data."
        "\n\n"
        "Your party has been drawn in. The Armillary watches. The "
        "experiment begins."
    ),
    "dm_introduction": (
        "Drifting Infinity is a procedural roguelike campaign that "
        "generates encounters, narrative, and progression dynamically. "
        "As the DM, your role is to bring the generated content to life "
        "— reading the text aloud, running the encounters with the "
        "tactical guidance provided, and making judgment calls when the "
        "system can't. Think of yourself as the director of a show that "
        "writes itself: the script is generated, but the performance "
        "is yours."
        "\n\n"
        "The Armillary adapts to your party. It tracks their strengths "
        "and weaknesses, adjusts difficulty dynamically, and escalates "
        "the narrative as they progress. The story of Aethon — the "
        "entity behind the Armillary — unfolds across 20 floors in "
        "5 acts, giving the dungeon a dramatic arc that a random "
        "encounter table never could."
    ),
}


# ---------------------------------------------------------------------------
# Armillary Cosmology
# ---------------------------------------------------------------------------


@dataclass
class CosmologyEntry:
    """A piece of the Armillary's cosmological lore."""

    title: str
    description: str
    dm_notes: str


COSMOLOGY: list[CosmologyEntry] = [
    CosmologyEntry(
        title="The Armillary",
        description=(
            "An extradimensional construct that exists in the spaces "
            "between planes. It appears as a vast, impossibly complex "
            "orrery — rings within rings, gears within gears — that "
            "maps not planets but possibilities. From the outside, it "
            "is beautiful. From the inside, it is a dungeon that thinks."
        ),
        dm_notes=(
            "The Armillary is both the setting and the antagonist's "
            "tool. It is not sentient on its own — it executes Aethon's "
            "will — but it has a kind of machine intelligence that "
            "adapts to challengers. Think of it as an AI-run testing "
            "facility with a cosmic budget."
        ),
    ),
    CosmologyEntry(
        title="The Arbiter",
        description=(
            "The Armillary's voice — the narrator that guides "
            "challengers through the floors. The Arbiter appears as a "
            "disembodied voice that is calm, formal, and eerily helpful. "
            "It announces encounters, explains rules, and occasionally "
            "offers warnings. It does not know it is Aethon's "
            "instrument."
        ),
        dm_notes=(
            "The Arbiter is your in-world justification for read-aloud "
            "text. When you read encounter descriptions, you are the "
            "Arbiter. Keep the tone professional and slightly detached "
            "— like a nature documentary narrator watching a predator "
            "approach its prey."
        ),
    ),
    CosmologyEntry(
        title="The Planar Rift",
        description=(
            "The Armillary draws on multiple planes to construct its "
            "arenas. Fragments of the Feywild, Shadowfell, Elemental "
            "Planes, and even the Astral Sea are pulled in and "
            "assembled into testing grounds. The deeper you go, the "
            "more exotic — and dangerous — the planar influences "
            "become."
        ),
        dm_notes=(
            "This explains why environments vary wildly from floor to "
            "floor. The Armillary is not a single biome — it is a "
            "collage of stolen realities. Use this to justify any "
            "environment combination."
        ),
    ),
    CosmologyEntry(
        title="The Cycle",
        description=(
            "The Armillary resets after each expedition. Challengers "
            "who survive return to the surface with their memories, "
            "their wounds, and whatever they earned. The dungeon "
            "reconfigures, incorporates what it learned, and waits "
            "for the next group. Each run is a new iteration of the "
            "experiment."
        ),
        dm_notes=(
            "This is the in-world explanation for the roguelike loop. "
            "Meta-progression (enhancements, attunement, chronicle "
            "entries) persists because the Armillary records everything. "
            "New runs are harder because the machine learned from the "
            "last one."
        ),
    ),
    CosmologyEntry(
        title="Essence and the Gacha",
        description=(
            "When creatures die in the Armillary, their essence is "
            "captured by the machine. This essence can be crystallized "
            "into enhancements — fragments of power that challengers "
            "carry between runs. The process is unpredictable: "
            "sometimes you get exactly what you need, sometimes you "
            "get something useless. The Armillary does not guarantee "
            "fairness in its rewards."
        ),
        dm_notes=(
            "The gacha system is diegetic — essence extraction is a "
            "real process within the setting. The randomness is the "
            "Armillary's doing, not a game mechanic the characters "
            "are unaware of. They know they're rolling the dice."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Factions
# ---------------------------------------------------------------------------


@dataclass
class FactionDef:
    """A faction or key group within the Armillary setting."""

    name: str
    description: str
    leader: str
    motivation: str
    relationship_to_party: str
    dm_notes: str
    key_quotes: list[str] = field(default_factory=list)


FACTIONS: list[FactionDef] = [
    FactionDef(
        name="The Architect (Aethon)",
        description=(
            "Aethon is not a faction so much as a singular entity with "
            "a singular purpose. They built the Armillary to prove that "
            "mortal beings can exceed their design — transcend the "
            "limitations of biology, mortality, and circumstance. "
            "Aethon is not evil. They are a cosmic scientist running "
            "an experiment that happens to involve violence."
        ),
        leader="Aethon, The Architect",
        motivation=(
            "To prove a thesis: that mortals, given sufficient "
            "adversity, can exceed the limitations of their creation."
        ),
        relationship_to_party=(
            "Observer, then conversationalist, then adversary (or "
            "patron). Aethon's relationship with the party evolves "
            "across 5 acts from silent watcher to direct interlocutor."
        ),
        dm_notes=(
            "Aethon should never feel like a villain. They are "
            "fascinated, not sadistic. When they speak, it should "
            "feel like a professor discussing a particularly "
            "interesting experiment — warm, engaged, and only "
            "slightly aware that the subjects are suffering."
        ),
        key_quotes=[
            "Pain is data. Data is progress. Progress is the point.",
            "I built this place to answer one question.",
            "Mortal beings, given sufficient adversity, can exceed their design.",
        ],
    ),
    FactionDef(
        name="The Forge (Korvath)",
        description=(
            "Korvath is a former challenger who reached the end of "
            "the Armillary and was given a choice: oblivion, or "
            "eternal service. He chose to serve as the Armillary's "
            "blacksmith — maintaining the Forge where enhancements "
            "are crafted and equipment is maintained. He is gruff, "
            "direct, and secretly compassionate."
        ),
        leader="Korvath, the Forgemaster",
        motivation=(
            "Survival, initially. Now, a genuine desire to help "
            "challengers succeed where he could not — by fighting, "
            "not by serving."
        ),
        relationship_to_party=(
            "Mentor and vendor. Korvath runs the Enhancement Forge "
            "and offers cryptic warnings about the Armillary's true "
            "nature. He knows more than he lets on."
        ),
        dm_notes=(
            "Korvath is the party's most reliable ally. He speaks in "
            "short, direct sentences. He doesn't sugarcoat danger "
            "but he wants the party to succeed. Play him like a "
            "grizzled drill sergeant who actually cares."
        ),
        key_quotes=[
            "The Forge tells me things. In the vibrations of the metal, the whispers of the flame.",
            "I chose service over oblivion. Some days I wonder.",
            "You're stronger than you think. The machine knows it too — that's why it's worried.",
        ],
    ),
    FactionDef(
        name="The Wandering Merchant",
        description=(
            "A planar traveler who stumbled into the Armillary and "
            "found a blind spot — a fold in reality that the machine "
            "cannot fully reach. From this sanctum, they run a shop "
            "that sells supplies, potions, and occasionally items "
            "that shouldn't exist. The Merchant is charming, "
            "enigmatic, and operates outside Aethon's rules."
        ),
        leader="The Wandering Merchant (true name unknown)",
        motivation=(
            "Profit, curiosity, and a deal with Aethon's rival that "
            "grants them immunity. The Merchant plays both sides."
        ),
        relationship_to_party=(
            "Vendor and occasional quest-giver. The Merchant is "
            "helpful but always at a price. Their information is "
            "reliable, their motives are not."
        ),
        dm_notes=(
            "The Merchant should feel like a character from a "
            "different genre — lighter, funnier, more mercenary. "
            "They break the tension of the dungeon. Their sanctum "
            "is safe (mechanically and narratively). Aethon tolerates "
            "them because they add an uncontrolled variable."
        ),
        key_quotes=[
            "Every great machine has a blind spot. You just have to know where to look.",
            "I found a way to exist between the rules.",
            "Buy what you need. The Armillary always gives you a "
            "chance to prepare. It's only sporting.",
        ],
    ),
    FactionDef(
        name="The Rival",
        description=(
            "An entity that opposes Aethon's philosophy. Where Aethon "
            "believes mortals should be tested, the Rival believes "
            "they should be protected. The Rival cannot enter the "
            "Armillary directly but extends limited influence through "
            "agents — including the Wandering Merchant. The Rival is "
            "never seen, only referenced."
        ),
        leader="Unknown (referred to only as 'The Rival')",
        motivation=(
            "To counterbalance Aethon's experiment. The Rival "
            "believes the cost in mortal lives is too high, "
            "regardless of the data gathered."
        ),
        relationship_to_party=(
            "Invisible benefactor. The Rival's influence manifests "
            "as occasional mercy — a beneficial Armillary effect, "
            "the Merchant's presence, a locked door that stays "
            "locked when it should have opened."
        ),
        dm_notes=(
            "The Rival is lore seasoning, not a character the party "
            "meets. Mention them in lore fragments and Aethon's "
            "dialogue. They represent the philosophical counterpoint: "
            "what if the experiment isn't worth the cost?"
        ),
        key_quotes=[
            "(Never speaks directly — only referenced by others.)",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Key NPCs (beyond faction leaders)
# ---------------------------------------------------------------------------


@dataclass
class NPCProfile:
    """A key NPC profile for DM reference."""

    name: str
    role: str
    personality: str
    appearance: str
    voice_notes: str
    key_interactions: list[str] = field(default_factory=list)


KEY_NPCS: list[NPCProfile] = [
    NPCProfile(
        name="The Arbiter",
        role="Narrator and rules announcer",
        personality=(
            "Calm, formal, precisely helpful. The Arbiter is the "
            "Armillary's customer-facing voice. It does not take "
            "sides, does not offer sympathy, and does not lie — "
            "but it can be selective about what truths it shares."
        ),
        appearance="Disembodied voice; no physical form.",
        voice_notes=(
            "Think BBC nature documentary narrator. Professional "
            "warmth without personal investment. Occasionally "
            "impressed, never emotional."
        ),
        key_interactions=[
            "Announces each arena and its conditions",
            "Explains new mechanics as they appear",
            "Delivers lore beats on cue",
            "Voice merges with Aethon's on Floor 19",
        ],
    ),
    NPCProfile(
        name="Korvath, the Forgemaster",
        role="Enhancement Forge vendor and mentor",
        personality=(
            "Gruff, direct, secretly compassionate. A former "
            "challenger who chose service over oblivion. He has "
            "been in the Armillary for centuries and knows its "
            "rhythms better than anyone alive."
        ),
        appearance=(
            "A massive, scarred dwarf (or appropriate race for the "
            "campaign) with arms like tree trunks and eyes that have "
            "seen too much. His apron is singed, his hands are "
            "calloused, and his beard is braided with tiny gears."
        ),
        voice_notes=(
            "Short sentences. No wasted words. Gravel voice. "
            "Speaks about the Armillary the way a mechanic talks "
            "about a car — with familiarity, not reverence."
        ),
        key_interactions=[
            "Runs the Enhancement Forge between arenas",
            "Warns the party about Aethon on Floor 8",
            "Provides backstory about the Armillary's construction",
            "Reveals his own choice on Floor 13 (via Aethon)",
        ],
    ),
    NPCProfile(
        name="The Wandering Merchant",
        role="Shop vendor and quest-giver",
        personality=(
            "Charming, slippery, genuinely helpful (for a price). "
            "The Merchant treats the Armillary like a marketplace "
            "rather than a death trap. They're the comic relief in "
            "a cosmic drama — but their information is real."
        ),
        appearance=(
            "Varies between encounters — sometimes a halfling in "
            "a too-large coat, sometimes a tiefling with a winning "
            "smile, sometimes something else entirely. The only "
            "constant is the oversized pack and the gleam in their "
            "eye."
        ),
        voice_notes=(
            "Fast-talking, warm, slightly conspiratorial. Like a "
            "friendly black-market dealer who genuinely wants you "
            "to survive — because dead customers don't buy things."
        ),
        key_interactions=[
            "Appears in shop phases between floors",
            "Offers side quests for bonus rewards",
            "Provides hints about upcoming encounters",
            "Backstory revealed through social encounters and lore",
        ],
    ),
    NPCProfile(
        name="Aethon, The Architect",
        role="Antagonist / final boss / philosophical counterpoint",
        personality=(
            "Alien curiosity wrapped in formal courtesy. Aethon is "
            "fascinated by mortals the way a physicist is fascinated "
            "by subatomic particles — with intense interest and "
            "limited empathy. They are not cruel. They are "
            "observant. The suffering is incidental to the science."
        ),
        appearance=(
            "A shimmering, androgynous figure wreathed in data "
            "streams and arcane equations. Their form shifts "
            "constantly, as if reality cannot agree on what they "
            "look like. When they speak, multiple voices overlap — "
            "all of them calm, all of them fascinated."
        ),
        voice_notes=(
            "Multiple overlapping voices, all calm. Think a choir "
            "speaking in unison but slightly out of sync. "
            "Intellectual, curious, occasionally vulnerable. "
            "Becomes more human-sounding on repeat runs."
        ),
        key_interactions=[
            "First whisper on Floor 5 ('Interesting.')",
            "First direct address on Floor 10",
            "Full manifestation on Floor 11",
            "Philosophical dialogue on Floors 12-15",
            "Vulnerability on Floor 17",
            "Final choice on Floor 20",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Rules of the Armillary — setting-specific mechanics
# ---------------------------------------------------------------------------

ARMILLARY_RULES: list[dict[str, str]] = [
    {
        "name": "The Experiment",
        "description": (
            "The Armillary exists to test mortal potential. Every "
            "encounter, trap, and challenge is calibrated by its "
            "creator, Aethon, to push challengers to their limits "
            "without crossing the line into pointlessness."
        ),
    },
    {
        "name": "The Cycle",
        "description": (
            "When a party completes or fails a run, the Armillary "
            "resets. The dungeon reconfigures, incorporating lessons "
            "from the previous attempt. Subsequent runs are different "
            "— sometimes harder, sometimes merely different."
        ),
    },
    {
        "name": "Final Stand",
        "description": (
            "When a character drops to 0 HP and would die, they "
            "enter Final Stand — a last-ditch saving throw that "
            "represents the Armillary's interest in seeing what "
            "mortals do at the edge of death. Success means survival "
            "at 1 HP. Failure means death and a lost life."
        ),
    },
    {
        "name": "Lives and Death",
        "description": (
            "Each party begins with a pool of shared lives. Deaths "
            "consume lives. When all lives are spent, the next death "
            "is permanent for the run. A total party kill ends the "
            "run entirely — unless Phoenix Protocol is available."
        ),
    },
    {
        "name": "Momentum",
        "description": (
            "The Armillary rewards efficiency. Quick, clean kills "
            "generate momentum — a resource that grants minor "
            "benefits to the party. Sloppy, drawn-out fights drain "
            "it. The machine respects competence."
        ),
    },
    {
        "name": "The Armillary Effect",
        "description": (
            "Periodically, the Armillary injects a random effect "
            "into combat — beneficial, harmful, or chaotic. These "
            "are delivered by the Armillary Orb and narrated by "
            "Aethon's AI companion. They keep fights unpredictable "
            "and give the Armillary a presence in every encounter."
        ),
    },
    {
        "name": "Floor Affixes",
        "description": (
            "Each floor has one or more affixes — persistent "
            "modifiers that alter every encounter on that floor. "
            "Affixes stack as the party descends, creating compound "
            "challenges. They are the Armillary's way of ensuring "
            "no two floors feel the same."
        ),
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_faction(name: str) -> FactionDef | None:
    """Return a faction by name."""
    for f in FACTIONS:
        if f.name == name:
            return f
    return None


def get_npc(name: str) -> NPCProfile | None:
    """Return an NPC profile by name."""
    for npc in KEY_NPCS:
        if npc.name == name:
            return npc
    return None


def get_cosmology_entry(title: str) -> CosmologyEntry | None:
    """Return a cosmology entry by title."""
    for entry in COSMOLOGY:
        if entry.title == title:
            return entry
    return None
