"""Collectible lore fragments for the Chronicle/Archive.

Fragments are earned from lore beats, secret events, social encounters,
and achievements.  They populate the Chronicle with discoverable narrative.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoreFragmentDef:
    id: str
    title: str
    text: str
    category: str       # "armillary", "aethon", "korvath", "merchant", "history", "meta"
    source: str          # What grants this fragment (beat id, event id, etc.)


# ---------------------------------------------------------------------------
# Fragment catalogue
# ---------------------------------------------------------------------------

LORE_FRAGMENTS: list[LoreFragmentDef] = [
    # === ARMILLARY ===
    LoreFragmentDef(
        id="frag_coordination",
        title="Directed Malice",
        text="The creatures in the Armillary don't merely attack — they coordinate. Not as animals hunting, but as pieces on a board. Something is directing them. Something that knows tactics.",
        category="armillary",
        source="act1_floor3",
    ),
    LoreFragmentDef(
        id="frag_first_whisper",
        title="The First Whisper",
        text="A single word, spoken by something that is neither the Arbiter nor the arena itself. 'Interesting.' It carries the weight of millennia of observation.",
        category="aethon",
        source="act1_floor5",
    ),
    LoreFragmentDef(
        id="frag_death_fascination",
        title="The Arena's Appetite",
        text="When a champion falls, the arena doesn't celebrate. It... studies. Every death is a data point. Every resurrection is a second experiment. The Armillary is learning from your pain.",
        category="armillary",
        source="act2_floor7_death",
    ),
    # === KORVATH ===
    LoreFragmentDef(
        id="frag_korvath_warning",
        title="Korvath's Warning",
        text="'I have served this place for longer than I care to remember,' Korvath says, hammering a blade into shape. 'The Forge speaks to me. And lately, it speaks of you. Someone behind the walls has taken notice. That is both a blessing and a curse.'",
        category="korvath",
        source="act2_floor8",
    ),
    LoreFragmentDef(
        id="frag_korvath_choice",
        title="The Artificer's Choice",
        text="Korvath was once a challenger, like you. He reached the end and was given a choice: oblivion, or eternal service. He chose the Forge. He chose to create rather than to end. Some days, he wonders if it was the right choice.",
        category="korvath",
        source="act3_floor13",
    ),
    # === AETHON ===
    LoreFragmentDef(
        id="frag_aethon_attention",
        title="The Watcher's Gaze",
        text="'Ten floors. Most break by seven.' The voice is not cruel. It's clinical. Whatever watches from behind the Armillary isn't interested in suffering — it's interested in what happens when suffering doesn't break you.",
        category="aethon",
        source="act2_floor10",
    ),
    LoreFragmentDef(
        id="frag_aethon_reveal",
        title="Aethon",
        text="The entity calls itself Aethon. It appears as something between a person and an idea — shifting, shimmering, impossible to pin down. It built the Armillary. Not as a weapon, not as a prison, but as an experiment. A thesis given physical form.",
        category="aethon",
        source="act3_floor11",
    ),
    LoreFragmentDef(
        id="frag_aethon_thesis",
        title="The Thesis",
        text="'Mortal beings, given sufficient adversity, can exceed their design.' This is Aethon's thesis. The Armillary exists to test it. Every floor, every creature, every trap — it's all in service of this one cosmic question.",
        category="aethon",
        source="act3_floor15",
    ),
    LoreFragmentDef(
        id="frag_aethon_doubt",
        title="Doubt",
        text="For the first time, Aethon seems uncertain. 'What happens if you prove me right?' they ask, and for a moment you see something behind the cosmic detachment: fear. If mortals can truly exceed their design, what does that mean for beings like Aethon?",
        category="aethon",
        source="act4_floor17",
    ),
    LoreFragmentDef(
        id="frag_threshold",
        title="The Threshold",
        text="The boundary between Arbiter and Architect dissolves. For a moment, you hear them speak as one — the voice that narrates your story and the voice that wrote it. 'Come,' they say together.",
        category="aethon",
        source="act4_floor19",
    ),
    LoreFragmentDef(
        id="frag_armillary_truth",
        title="The True Armillary",
        text="Beyond the arena walls, visible for the first time: the Armillary's true form. An orrery of impossible complexity, mapping not planets but possibilities. Every choice you've made, every path not taken — it's all here, spinning in light and shadow.",
        category="armillary",
        source="act5_floor20_start",
    ),
    LoreFragmentDef(
        id="frag_final_choice",
        title="The Choice",
        text="Join or fight. Service or freedom. Korvath chose service. The Merchant chose to break the rules entirely. Aethon offers you the same choice, but with one difference: you know what you're choosing.",
        category="aethon",
        source="act5_floor20_end",
    ),
    LoreFragmentDef(
        id="frag_thesis_proven",
        title="Thesis Proven",
        text="The Armillary acknowledges you. Not as challengers, not as data — as proof. Aethon's millennia-old experiment has an answer: yes, mortals can exceed their design. The question now is what comes next.",
        category="aethon",
        source="act5_victory",
    ),
    # === MERCHANT ===
    LoreFragmentDef(
        id="frag_merchant_secret",
        title="Between the Cracks",
        text="The Wandering Merchant's sanctum exists in a fold of reality that the Armillary can't quite reach. 'I found a blind spot,' the Merchant explains. 'Every great machine has one. You just have to know where to look.'",
        category="merchant",
        source="merchants_sanctum",
    ),
    LoreFragmentDef(
        id="frag_merchant_past",
        title="The Merchant's True Name",
        text="The Merchant was once a planar traveler who stumbled into the Armillary by accident. Unable to leave, they found a way to exist between its rules. Now they profit from both sides — selling to challengers and to the arena itself.",
        category="merchant",
        source="merchants_request",
    ),
    LoreFragmentDef(
        id="frag_merchant_rival",
        title="The Rival",
        text="The Merchant's immunity comes from a deal with Aethon's rival — a being who believes mortals should be protected, not tested. This rival cannot enter the Armillary, but they can extend limited protection to their agents.",
        category="merchant",
        source="act3_return_floor11",
    ),
    # === SECRETS ===
    LoreFragmentDef(
        id="frag_vault_origin",
        title="The Shattered Vault",
        text="This vault once held the Armillary's core — the heart of the machine. It was shattered long ago, its contents scattered across the floors. What remains is the overflow: treasures too numerous for the arena to use.",
        category="armillary",
        source="shattered_vault",
    ),
    LoreFragmentDef(
        id="frag_echoes_truth",
        title="Echoes of the Fallen",
        text="The Armillary doesn't just record deaths — it replays them. Every fallen challenger becomes a ghost in the machine, their tactics and abilities preserved. This is how the arena learns. This is what happens to the essence of those who fall.",
        category="armillary",
        source="crucible_of_echoes",
    ),
    LoreFragmentDef(
        id="frag_beyond_armillary",
        title="Beyond the Walls",
        text="Something exists outside the Armillary — something that is not Aethon's creation. The Rift proves it. There are things in the spaces between planes that even the Architect didn't anticipate. The universe is bigger than one entity's thesis.",
        category="history",
        source="the_rift",
    ),
    LoreFragmentDef(
        id="frag_arbiter_truth",
        title="The Arbiter's Role",
        text="The Arbiter was never just a narrator. They are Aethon's instrument — chosen, like Korvath, to serve a purpose. But unlike Korvath, they don't know it. The Arbiter believes they are the Armillary's voice. The truth is more complex.",
        category="aethon",
        source="arbiters_trial",
    ),
    LoreFragmentDef(
        id="frag_prisoner_tale",
        title="A Prisoner's Story",
        text="The creature speaks of being summoned against its will, pulled from its home plane to fight in an arena it doesn't understand. 'The machine takes what it needs,' it says. 'It doesn't ask.'",
        category="armillary",
        source="desperate_prisoner",
    ),
    LoreFragmentDef(
        id="frag_lost_explorer",
        title="The Explorer's Last Words",
        text="The ghost of a previous challenger whispers of reaching floor 15 before falling. 'I saw something in the walls,' they say. 'A face. Watching. Smiling. It wasn't cruel — it was curious. That was worse.'",
        category="history",
        source="lost_explorer",
    ),
    LoreFragmentDef(
        id="frag_armillary_honesty",
        title="The Arena's Honour",
        text="The Armillary always keeps its deals. This is Aethon's one unbreakable rule: the test must be fair. Punishing, brutal, overwhelming — but fair. A rigged experiment proves nothing.",
        category="aethon",
        source="armillarys_bargain",
    ),
    LoreFragmentDef(
        id="frag_arena_past",
        title="Memory of the First",
        text="The arena's memory shows the very first expedition — three warriors and a mage, centuries ago. They made it to floor 12. Aethon's voice is audible in the memory, younger somehow: 'They're better than I expected.'",
        category="history",
        source="arenas_memory",
    ),
    LoreFragmentDef(
        id="frag_secret_discovered",
        title="Hidden Chambers",
        text="The Armillary is larger than it appears. Hidden chambers, sealed passages, forgotten vaults — they exist between the floors, accessible only to those the arena deems worthy. Or interesting.",
        category="armillary",
        source="first_secret_event",
    ),
    # === ACHIEVEMENT-GATED ===
    LoreFragmentDef(
        id="frag_deathless",
        title="Untouchable",
        text="To pass through the Armillary without a single death is almost unprecedented. The arena's records show it has happened exactly four times in its history. You are the fifth.",
        category="meta",
        source="deathless_run",
    ),
    LoreFragmentDef(
        id="frag_victory",
        title="The End of the Beginning",
        text="Completing the Armillary doesn't close it — it resets. Like any good experiment, the data demands replication. New variables are introduced. New hypotheses are tested. The cycle begins again.",
        category="meta",
        source="armillarys_equal",
    ),
    LoreFragmentDef(
        id="frag_lore_master",
        title="The Full Picture",
        text="With enough fragments, the story becomes clear: the Armillary is not a prison, not a game, not a test. It is a conversation — between a cosmic entity and the mortal beings it can't stop being fascinated by.",
        category="meta",
        source="lore_master",
    ),
    LoreFragmentDef(
        id="frag_aethon_truth",
        title="What Aethon Is",
        text="Aethon is not a god. Not a demon. Not an aberration. Aethon is an idea given form — the belief that the only way to know what something is capable of is to push it past its limits. The Armillary is that belief made real.",
        category="aethon",
        source="aethon_defied",
    ),
]


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

_FRAGMENT_INDEX: dict[str, LoreFragmentDef] = {f.id: f for f in LORE_FRAGMENTS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_lore_fragment(fragment_id: str) -> LoreFragmentDef | None:
    """Return a lore fragment by id."""
    return _FRAGMENT_INDEX.get(fragment_id)


def get_fragments_by_category(category: str) -> list[LoreFragmentDef]:
    """Return all fragments in a category."""
    return [f for f in LORE_FRAGMENTS if f.category == category]


def get_undiscovered_fragments(found_ids: list[str]) -> list[LoreFragmentDef]:
    """Return fragments the player hasn't found yet."""
    found = set(found_ids or [])
    return [f for f in LORE_FRAGMENTS if f.id not in found]
