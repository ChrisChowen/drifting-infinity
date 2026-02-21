"""NPC profile generation for social encounters and recurring characters.

Generates personality, voice, and motivation text for NPCs the DM needs
to roleplay — social encounter characters, the Wandering Merchant,
Korvath the Forgemaster, and the Arbiter.
"""

import random
from dataclasses import dataclass


@dataclass
class NPCProfile:
    """A generated NPC profile for DM use."""

    name: str
    role: str
    personality: str
    voice_direction: str
    motivation: str
    appearance: str


# ---------------------------------------------------------------------------
# Recurring NPCs — fixed profiles with variation
# ---------------------------------------------------------------------------

ARBITER_PROFILES: list[NPCProfile] = [
    NPCProfile(
        name="The Arbiter",
        role="Announcer & Rules Enforcer",
        personality="Impersonal and precise. The Arbiter is the voice of the Armillary — "
        "mechanical, fair, and utterly without mercy or malice.",
        voice_direction="Speak in a flat, measured cadence. No emotion. Like a courtroom "
        "clerk reading charges. Use formal phrasing: 'The arena recognizes...' "
        "'The conditions are met.' 'Proceed.'",
        motivation="The Arbiter enforces the Armillary's rules. It has no opinion "
        "about the party's survival. It simply administers.",
        appearance="A disembodied voice that resonates from the arena walls. Occasionally "
        "manifests as glowing text on surfaces or a geometric light pattern.",
    ),
]

KORVATH_PROFILES: list[NPCProfile] = [
    NPCProfile(
        name="Korvath the Forgemaster",
        role="Enhancement Vendor & Lore Source",
        personality="Gruff, practical, and surprisingly warm beneath the exterior. "
        "Korvath is a craftsman bound to the Armillary — he chose service over death "
        "and has made peace with it, mostly.",
        voice_direction="Speak with a rough, deep voice. Short sentences. Drops articles. "
        "'Good steel, that. Took it off a knight who didn't need it anymore.' "
        "Occasionally melancholic when discussing the Armillary.",
        motivation="Korvath genuinely wants the party to succeed. He's seen too many "
        "expeditions fail. But he's bound by rules — he can't give things away or "
        "reveal too much about Aethon.",
        appearance="A broad-shouldered dwarf with burn-scarred arms and a leather apron. "
        "His forge glows with an unnatural blue-white light. One eye is milky — "
        "replaced by the Armillary with something that sees more than it should.",
    ),
]

MERCHANT_PROFILES: list[NPCProfile] = [
    NPCProfile(
        name="The Wandering Merchant",
        role="Shop Vendor & Wildcard",
        personality="Enigmatic, cheerful, and slightly unsettling. The Merchant moves "
        "freely through the Armillary — the only being that does. They know more "
        "than they let on and find everything amusing.",
        voice_direction="Light, almost playful tone. Speaks in riddles occasionally. "
        "'Everything has a price, and every price has a story. Which would you "
        "like first?' Always deflects personal questions with humor.",
        motivation="The Merchant made a deal with Aethon's rival — a being who "
        "believes mortals should be sheltered. This grants freedom of movement "
        "but binds them to commerce. They profit from the Armillary's existence.",
        appearance="Changes slightly each time they appear. Sometimes tall, sometimes "
        "short. Always wearing a coat with too many pockets. A wide-brimmed hat "
        "shadows their face. Their merchandise floats around them.",
    ),
]


# ---------------------------------------------------------------------------
# Social encounter NPC generation
# ---------------------------------------------------------------------------

SOCIAL_NPC_PERSONALITIES: dict[str, list[str]] = {
    "desperate_prisoner": [
        "Trembling and hollow-eyed, this creature has been caged for what feels like "
        "centuries. Its gratitude is overwhelming if freed — almost suspiciously so.",
        "Defiant despite captivity. It speaks through clenched teeth and refuses to beg, "
        "but its eyes plead for help.",
    ],
    "broken_mechanism": [
        "The mechanism has no personality — but the Armillary reacts to tampering with "
        "audible groans and sparks, as if in pain.",
    ],
    "armillarys_bargain": [
        "The Arbiter's voice shifts deeper when channeling this offer. There's a warmth "
        "to it that the Arbiter normally lacks — this is the Armillary speaking directly.",
    ],
    "lost_explorer": [
        "A translucent figure that doesn't fully realize it's dead. It mutters about "
        "supply lists and expedition plans. Heartbreaking in its normalcy.",
        "Angry and confused. This ghost died unfairly and knows it. It lashes out "
        "verbally before calming down — if the party is patient.",
    ],
    "merchants_request": [
        "The Merchant drops their usual playful facade. Whatever they need, it matters "
        "to them personally — a rare vulnerability.",
    ],
    "arenas_memory": [
        "The memory plays like a ghostly theater performance. Phantom warriors fight "
        "phantom monsters while the real arena watches in silence.",
    ],
    "the_deserter": [
        "A creature that should be hostile but has broken free of the Armillary's "
        "compulsion. It's scared, pragmatic, and willing to trade information for "
        "its life. It keeps glancing over its shoulder.",
    ],
    "the_wager": [
        "The crystalline orbs pulse with inner light. A low chime fills the arena — "
        "the Armillary is enjoying itself.",
    ],
}


def generate_social_npc_profile(encounter_id: str) -> str:
    """Generate personality text for a social encounter NPC."""
    pool = SOCIAL_NPC_PERSONALITIES.get(encounter_id, [])
    if pool:
        return random.choice(pool)
    return "A figure emerges from the arena's depths. Its intentions are unclear."


def get_recurring_npc(npc_name: str) -> NPCProfile | None:
    """Get a profile for a recurring NPC."""
    profiles: dict[str, list[NPCProfile]] = {
        "arbiter": ARBITER_PROFILES,
        "korvath": KORVATH_PROFILES,
        "merchant": MERCHANT_PROFILES,
    }
    pool = profiles.get(npc_name.lower())
    if pool:
        return pool[0]  # Fixed profiles for recurring NPCs
    return None
