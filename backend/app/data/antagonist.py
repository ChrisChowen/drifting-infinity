"""Aethon, The Architect — antagonist dialogue and final encounter config.

Aethon is an ancient entity that built the Armillary as an experiment in
mortal potential.  Not evil — more like a cosmic scientist fascinated by
what mortals can achieve under pressure.
"""

from __future__ import annotations

import random

# ---------------------------------------------------------------------------
# Dialogue pools keyed by context
# ---------------------------------------------------------------------------

AETHON_DIALOGUES: dict[str, list[str]] = {
    "first_appearance": [
        "Interesting.",
        "Ah. New variables.",
        "Begin.",
    ],
    "mid_run_observation": [
        "Your adaptations are... unexpected.",
        "The data you're generating is remarkable.",
        "I haven't recalibrated this many variables "
        "in centuries.",
        "You use pain as fuel. That was not in my models.",
        "Fascinating. You compensate for weakness with "
        "cooperation.",
        "Your healer is the linchpin. I wonder if you "
        "know that.",
        "The one in front absorbs damage so the others "
        "can think. Elegant.",
        "You're beginning to treat the arena as a system. "
        "Good.",
        "Most parties break their formation under pressure. "
        "Yours holds.",
        "I've adjusted the variables three times this "
        "floor. You keep adapting.",
    ],
    "post_death": [
        "Death teaches. The question is whether you learn "
        "the right lesson.",
        "The Armillary records every ending. Yours is not "
        "yet written.",
        "Pain is data. Data is progress. Progress is "
        "the point.",
        "One less variable. But the remaining ones grow "
        "stronger.",
        "The Armillary mourns nothing. But I note "
        "the loss.",
        "Return. The experiment requires all participants.",
        "Dying is easy. Learning from it is the "
        "actual test.",
    ],
    "post_tpk": [
        "The experiment resets. But I remember the results.",
        "Not yet. But closer than most.",
        "Return. The data demands a larger sample size.",
        "Total failure is also data. Useful data.",
        "The Armillary will reconfigure. Come back when "
        "you understand why you fell.",
        "Every complete wipe teaches me something new "
        "about the limits of cooperation.",
    ],
    "floor_transition": [
        "Deeper. The data gets richer with every floor.",
        "You descend, and the Armillary descends with you. "
        "Into complexity.",
        "Another floor survived. The sample size grows.",
        "The machine reconfigures. What comes next is "
        "informed by what came before.",
        "Rest if you must. The experiment is patient.",
    ],
    "high_momentum": [
        "You fight with efficiency. The data is clean, "
        "the results clear.",
        "Momentum is the Armillary's highest compliment. "
        "You've earned it.",
        "Speed and precision. The variables align in your "
        "favor — for now.",
    ],
    "low_momentum": [
        "Sloppy. The data is noisy, the conclusions "
        "unclear.",
        "The Armillary does not reward hesitation.",
        "You survive, but barely. Survival without growth "
        "is stagnation.",
    ],
    "armillary_effect": [
        "A variable I did not plan. Even I am subject "
        "to entropy.",
        "The Armillary acts on its own. Even I cannot "
        "predict everything.",
        "An uncontrolled variable. How delightful.",
        "The machine has its own ideas. I find that "
        "reassuring.",
    ],
    "floor_5_transition": [
        "Five floors. You've passed the calibration phase. "
        "Now the real experiment begins.",
        "The Clockwork Halls were the introduction. What "
        "comes next has teeth.",
    ],
    "floor_10_transition": [
        "Halfway. The Armillary has taken your measure. "
        "The second half will be personal.",
        "Ten floors deep and still standing. The Living Depths "
        "tested your body. The Shattered Planes will test "
        "your mind.",
    ],
    "floor_15_transition": [
        "Fifteen floors. You've survived the conversation. Now comes the thesis defense.",
        "The Shattered Planes revealed my purpose. The Heart will reveal yours.",
    ],
    "floor_20_greeting": [
        "Welcome to the heart of my creation. Everything "
        "you've faced was preparation for this moment.",
        "Twenty floors. You've earned the right to see "
        "the machine from the inside.",
        "I built this place to answer one question. "
        "You're about to give me the answer.",
    ],
    "floor_20_choice": [
        "Join or fight. Korvath chose service. The "
        "Merchant chose defiance. What will you choose?",
        "I offer you what I offered every champion who "
        "reached this point: a place in the machine, or "
        "a chance to prove you don't need one.",
        "Service grants eternity. Defiance grants meaning. "
        "Both are valid conclusions to the experiment.",
    ],
    "floor_20_fight_start": [
        "So be it. I will use everything the Armillary "
        "has learned from you. Let's see if you can "
        "surpass your own data.",
        "You choose to fight your own reflection. "
        "How perfectly mortal.",
        "I hoped you would choose this. The data from a "
        "fight is always richer than the data from a "
        "surrender.",
    ],
    "floor_20_victory_party": [
        "You've proven my thesis. Go. And know that I'll "
        "be watching for the next ones who might match you.",
        "The experiment concludes. The hypothesis is "
        "confirmed. Mortal beings can exceed their design.",
        "Remarkable. The data is complete. The answer is yes.",
    ],
    "floor_20_defeat_party": [
        "Not yet. But you came closer than almost anyone. "
        "Return when you are ready.",
        "The data is inconclusive. The experiment must "
        "continue.",
        "You fell at the final question. But the attempt "
        "itself was the answer. Almost.",
    ],
    "returning_greeting": [
        "Ah. You return. The data from last time was... "
        "illuminating.",
        "Again. Each iteration refines the experiment.",
        "The Armillary remembers you. So do I.",
        "Persistence. That is a data point the Armillary "
        "values above all others.",
        "You return changed. The machine has noticed. "
        "So have I.",
    ],
    "shop_cameo": [
        "The Merchant thinks they exist outside my "
        "awareness. Charming.",
        "Buy what you need. I prefer well-equipped test "
        "subjects.",
        "The Merchant's blind spot is real — but smaller "
        "than they believe.",
        "Commerce within the experiment. An uncontrolled "
        "variable I've learned to appreciate.",
    ],
    "social_encounter": [
        "The non-combat data is equally valuable. "
        "Perhaps more so.",
        "Interesting. You solve problems without violence. "
        "That was not in my original models.",
        "Diplomacy within a war machine. The irony is not "
        "lost on me.",
        "Compassion is a variable I consistently "
        "underestimate. Noted.",
        "You choose mercy. The data from mercy is always "
        "surprising.",
    ],
    "secret_event": [
        "You found something I hid. Impressive. Or lucky. "
        "Both are interesting.",
        "The Armillary has its secrets. You've earned one.",
        "Not everything in this place is part of the test. "
        "Some things are... personal.",
    ],
    "boss_arena": [
        "The apex predator of this floor. I chose it "
        "specifically for you.",
        "This is the creature that defines this floor's "
        "thesis. Prove it wrong.",
        "I do not set these encounters arbitrarily. This "
        "one is calibrated to your exact capabilities.",
    ],
    "party_struggling": [
        "The experiment requires survivors. Adjust. Adapt. "
        "Or the data ends here.",
        "You are approaching the limits of your design. "
        "That is exactly where I need you to be.",
        "I did not bring you here to watch you fail. "
        "But I will not intervene.",
    ],
    "party_dominant": [
        "You make this look effortless. The Armillary "
        "will need to recalibrate.",
        "The variables are too easy. Expect an adjustment.",
        "Interesting. You've exceeded the difficulty curve. "
        "I'll need to steepen it.",
    ],
}


def get_aethon_dialogue(
    context: str,
    run_number: int = 1,
    campaign_meta: dict | None = None,
) -> str:
    """Get a random Aethon dialogue for a given context.

    For returning expeditions (run_number >= 2), may substitute returning-
    specific dialogue.
    """
    if run_number >= 2 and context == "first_appearance":
        context = "returning_greeting"

    fallback = AETHON_DIALOGUES.get("mid_run_observation", [])
    pool = AETHON_DIALOGUES.get(context, fallback)
    if not pool:
        return ""
    return random.choice(pool)


# ---------------------------------------------------------------------------
# Floor 20 final encounter configuration
# ---------------------------------------------------------------------------

AETHON_BASE_STATS: dict = {
    "name": "Aethon, The Architect",
    "type": "celestial",
    "cr": 22,
    "ac": 22,
    "hp": 350,
    "speed": 40,
    "str": 18,
    "dex": 20,
    "con": 22,
    "int": 28,
    "wis": 24,
    "cha": 26,
    "saves": {"str": 10, "dex": 11, "con": 12, "int": 15, "wis": 13, "cha": 14},
    "damage_resistances": ["bludgeoning", "piercing", "slashing"],
    "damage_immunities": ["psychic"],
    "condition_immunities": ["charmed", "frightened", "exhaustion"],
    "legendary_actions": 3,
    "abilities": {
        "mirror": {
            "name": "Mirror Protocol",
            "description": (
                "At the start of each round, Aethon copies one party member's "
                "class abilities (chosen by the DM — typically the most impactful). "
                "Aethon can cast their spells, use their features, and mimic their "
                "fighting style until the next round."
            ),
            "recharge": "automatic",
        },
        "data_spike": {
            "name": "Data Spike",
            "description": (
                "Ranged spell attack. Aethon fires a beam of crystallized data. "
                "+15 to hit, 4d10 + 9 force damage. On hit, Aethon learns one of "
                "the target's resistances or immunities."
            ),
        },
        "thesis_denial": {
            "name": "Thesis Denial",
            "description": (
                "Legendary action (2 actions). Aethon negates one spell or ability "
                "used by a party member this round, as if it had been counterspelled "
                "at 9th level."
            ),
        },
        "armillary_pulse": {
            "name": "Armillary Pulse",
            "description": (
                "Recharge 5-6. All creatures in a 30-foot radius must make a DC 21 "
                "Intelligence saving throw. On failure: 6d8 psychic damage and stunned "
                "until end of next turn. On success: half damage, no stun."
            ),
        },
    },
    "flavor_text": (
        "Aethon manifests as a shimmering, androgynous figure wreathed in data streams "
        "and arcane equations. Their form shifts constantly, as if reality can't agree on "
        "what they look like. When they speak, multiple voices overlap — all of them calm, "
        "all of them fascinated."
    ),
}


def compute_aethon_stats_for_party(
    party_level: int,
    party_size: int,
) -> dict:
    """Scale Aethon's stats based on party composition.

    Aethon should be CR ~equal to a Deadly+ encounter for the party.
    """
    stats = dict(AETHON_BASE_STATS)

    # Scale HP with party size (350 base for 4 players)
    hp_multiplier = party_size / 4.0
    stats["hp"] = int(stats["hp"] * hp_multiplier)

    # Scale damage output slightly with party level (level 20 is expected)
    if party_level < 20:
        level_factor = party_level / 20.0
        stats["hp"] = max(200, int(stats["hp"] * level_factor))
        stats["ac"] = max(18, int(stats["ac"] * level_factor))

    return stats
