"""Lore beat definitions — narrative moments across 20 floors.

The story of Aethon, The Architect, unfolds in 5 acts as the party
descends.  Lore beats fire at specific floors and conditions, with
different text for first runs vs returning expeditions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoreBeatDef:
    id: str
    floor: int
    trigger: str  # "floor_start", "floor_end", "arena_end", "death", "social"
    act: int  # 1-5
    arbiter_text: str  # What the Arbiter says/narrates
    aethon_text: str | None  # What Aethon says (None if not yet revealed)
    dm_stage_direction: str  # How to present this moment
    condition: str | None = None  # Optional: "run_number >= 2", "deaths > 3", etc.
    lore_fragment_id: str | None = None


# ---------------------------------------------------------------------------
# Lore beat catalogue — 5 Acts across 20 Floors
# ---------------------------------------------------------------------------

LORE_BEATS: list[LoreBeatDef] = [
    # === ACT 1: THE MACHINE (Floors 1-5) ===
    LoreBeatDef(
        id="act1_floor1",
        floor=1,
        trigger="floor_start",
        act=1,
        arbiter_text=(
            "The arena hums with ancient purpose. Gears turn "
            "in the walls. The air tastes of ozone and old "
            "magic."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "Read this as the party enters their first arena. "
            "Set the tone: mechanical, impersonal, vast."
        ),
    ),
    LoreBeatDef(
        id="act1_floor2",
        floor=2,
        trigger="floor_start",
        act=1,
        arbiter_text=(
            "The descent continues. The Armillary's mechanisms "
            "are more intricate here — as if the arena is "
            "paying closer attention."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "Subtle: the arena is slightly more responsive. "
            "Lights follow the party. Doors open before they "
            "reach them."
        ),
    ),
    LoreBeatDef(
        id="act1_floor3",
        floor=3,
        trigger="floor_end",
        act=1,
        arbiter_text=(
            "You notice the Armillary's creatures seemed... "
            "coordinated. Almost as if directed by something "
            "more than instinct."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "Plant the seed: the encounters felt designed, "
            "not random. Something is curating the experience."
        ),
        lore_fragment_id="frag_coordination",
    ),
    LoreBeatDef(
        id="act1_floor5",
        floor=5,
        trigger="floor_end",
        act=1,
        arbiter_text=(
            "As the last creature falls, a whisper echoes "
            "through the arena. Not the Arbiter. Something "
            "else entirely."
        ),
        aethon_text="Interesting.",
        dm_stage_direction=(
            "This is the first hint of Aethon. The single "
            "word should be delivered differently from the "
            "Arbiter's voice — alien, contemplative, "
            "pleased. The party should feel observed."
        ),
        lore_fragment_id="frag_first_whisper",
    ),
    LoreBeatDef(
        id="act1_floor4",
        floor=4,
        trigger="floor_start",
        act=1,
        arbiter_text=(
            "The corridors narrow. The mechanisms here are more "
            "precise, more attentive. Locks engage and disengage "
            "as you pass, as if the arena is opening a path — "
            "and closing the ones behind you."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "Build the sense of being guided. The Armillary is "
            "funneling the party. Doors open ahead and seal "
            "behind. They aren't lost — they're being directed."
        ),
    ),
    # Returning players
    LoreBeatDef(
        id="act1_return_floor1",
        floor=1,
        trigger="floor_start",
        act=1,
        arbiter_text=(
            "The Armillary stirs... but differently this time. "
            "The mechanisms move with recognition. It remembers "
            "you."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "For returning expeditions: the arena recognizes the "
            "party. Small details are different — trophies from "
            "the last run, scorch marks that match previous "
            "battles."
        ),
        condition="run_number >= 2",
    ),
    LoreBeatDef(
        id="act1_return_floor3",
        floor=3,
        trigger="floor_end",
        act=1,
        arbiter_text=(
            "The creatures here fought differently — adapting to "
            "tactics you used last time. The Armillary learned."
        ),
        aethon_text="You taught the machine. Now it teaches back.",
        dm_stage_direction=(
            "For returning expeditions: emphasize that the "
            "Armillary has adapted. Creatures use counter-tactics "
            "to strategies the party relied on previously."
        ),
        condition="run_number >= 2",
    ),
    # === ACT 2: THE WATCHER (Floors 6-10) ===
    LoreBeatDef(
        id="act2_floor6",
        floor=6,
        trigger="floor_start",
        act=2,
        arbiter_text=(
            "The Armillary's effects seem tailored to your "
            "party's weaknesses. This feels deliberate. "
            "Personal."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "The Armillary targets the party's specific "
            "vulnerabilities. Note: this should feel "
            "uncomfortable, not unfair."
        ),
    ),
    LoreBeatDef(
        id="act2_floor7_start",
        floor=7,
        trigger="floor_start",
        act=2,
        arbiter_text=(
            "The Living Depths pulse with a rhythm that matches "
            "your heartbeat. The walls are warm. The stone "
            "breathes."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "The organic nature of the Living Depths should be "
            "visceral now. The Armillary's 'heartbeat' syncs "
            "with the party — describe it when they notice."
        ),
    ),
    LoreBeatDef(
        id="act2_floor7_death",
        floor=7,
        trigger="death",
        act=2,
        arbiter_text=(
            "As the champion falls, the arena pulses. Not in "
            "triumph — in fascination. Something is drinking in "
            "the data."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "Trigger on any character death on floor 7+. The "
            "arena's reaction to death should feel scientific, "
            "not sadistic."
        ),
        lore_fragment_id="frag_death_fascination",
    ),
    LoreBeatDef(
        id="act2_floor8",
        floor=8,
        trigger="floor_start",
        act=2,
        arbiter_text=("Korvath pulls you aside between floors. His eyes are troubled."),
        aethon_text=None,
        dm_stage_direction=(
            "Korvath speaks: 'The Forge tells me things. In the "
            "vibrations of the metal, the whispers of the flame. "
            "Someone is watching you. Specifically. Not the arena "
            "— someone behind it. Be careful, Arbiter.'"
        ),
        lore_fragment_id="frag_korvath_warning",
    ),
    LoreBeatDef(
        id="act2_floor9",
        floor=9,
        trigger="floor_end",
        act=2,
        arbiter_text=(
            "The arena hums with something new — anticipation. "
            "The mechanisms around you accelerate, as if the "
            "machine is excited about what comes next."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "Build tension for Floor 10's reveal. The Armillary "
            "is preparing for Aethon's first direct address. "
            "The anticipation should feel palpable — like the "
            "air before a thunderstorm."
        ),
    ),
    LoreBeatDef(
        id="act2_floor10",
        floor=10,
        trigger="floor_end",
        act=2,
        arbiter_text=(
            "The arena falls silent for a heartbeat. Then a "
            "voice, clear as crystal, speaks directly to the "
            "party."
        ),
        aethon_text=(
            "Ten floors. Most break by seven. You have my "
            "attention."
        ),
        dm_stage_direction=(
            "This is Aethon's first direct address. The voice "
            "should be calm, curious, almost warm — like a "
            "scientist who just got an exciting result. After "
            "this, the Armillary's behavior subtly shifts: "
            "more challenging, but also more fair. The entity "
            "is playing honestly now."
        ),
        lore_fragment_id="frag_aethon_attention",
    ),
    # Returning players
    LoreBeatDef(
        id="act2_return_floor6",
        floor=6,
        trigger="floor_start",
        act=2,
        arbiter_text=(
            "The arena's mechanisms are different this time. "
            "Faster. More complex. As if it learned from "
            "last time."
        ),
        aethon_text=(
            "Ah. You return. The data from last time was... "
            "illuminating. Let's see what you've learned."
        ),
        dm_stage_direction=(
            "For returning expeditions: Aethon speaks earlier "
            "and more openly. The arena has been redesigned "
            "based on the previous run's data."
        ),
        condition="run_number >= 2",
    ),
    # === ACT 3: THE CONVERSATION (Floors 11-15) ===
    LoreBeatDef(
        id="act3_floor11",
        floor=11,
        trigger="floor_start",
        act=3,
        arbiter_text=(
            "Between floors, reality stutters. A figure "
            "appears — humanoid but wrong, like a painting "
            "that moves. It speaks."
        ),
        aethon_text=(
            "I am the reason this place exists. And you are "
            "the reason I'm still interested. I am called "
            "Aethon."
        ),
        dm_stage_direction=(
            "Aethon manifests visually for the first time. "
            "Describe them as shimmering, androgynous, "
            "constantly shifting — as if reality can't quite "
            "agree on what they look like. They're not "
            "threatening. They're fascinated."
        ),
        lore_fragment_id="frag_aethon_reveal",
    ),
    LoreBeatDef(
        id="act3_floor12",
        floor=12,
        trigger="floor_end",
        act=3,
        arbiter_text=(
            "Aethon appears again, briefly, as the floor's "
            "final creature dissolves."
        ),
        aethon_text=(
            "The Armillary was never meant to kill. It's "
            "meant to measure. Every spell you cast, every "
            "wound you survive — it's all data. Beautiful, "
            "violent data."
        ),
        dm_stage_direction=(
            "Reinforce Aethon's nature: not malicious, but "
            "coldly scientific. The party is data to them "
            "— valuable data."
        ),
    ),
    LoreBeatDef(
        id="act3_floor13",
        floor=13,
        trigger="floor_start",
        act=3,
        arbiter_text=(
            "Aethon is waiting between floors, as if they've "
            "been there for a long time."
        ),
        aethon_text=(
            "Korvath chose service over oblivion. The "
            "Merchant chose to ignore my rules entirely "
            "— impressive, honestly. What will you choose, "
            "I wonder?"
        ),
        dm_stage_direction=(
            "Answers two lore hooks: Korvath's binding and "
            "the Merchant's immunity. Aethon respects the "
            "Merchant's defiance. This should make the party "
            "wonder what choices they'll face."
        ),
        lore_fragment_id="frag_korvath_choice",
    ),
    LoreBeatDef(
        id="act3_floor14",
        floor=14,
        trigger="floor_start",
        act=3,
        arbiter_text=(
            "The Shattered Planes grow stranger still. Reality "
            "overlaps — you can see through walls into other "
            "arenas, other floors, other possibilities."
        ),
        aethon_text=(
            "The Armillary maps every possibility. What you see "
            "through the walls are other versions of this moment "
            "— other parties, other choices, other outcomes. "
            "All of them are real. All of them are mine."
        ),
        dm_stage_direction=(
            "The multiverse glimpses are disorienting but not "
            "dangerous. Describe other parties fighting other "
            "encounters — some winning, some losing. It "
            "reinforces the scale of Aethon's experiment."
        ),
    ),
    LoreBeatDef(
        id="act3_floor14_death",
        floor=14,
        trigger="death",
        act=3,
        arbiter_text=(
            "Aethon appears as the champion falls. For the first "
            "time, their expression is not curiosity — it's "
            "something closer to regret."
        ),
        aethon_text=(
            "That one had potential. The data from their loss is "
            "valuable, but I confess... I would have preferred "
            "the data from their survival."
        ),
        dm_stage_direction=(
            "This is subtle character development for Aethon. "
            "They are beginning to care, however slightly, "
            "about the individual subjects — not just the "
            "aggregate data."
        ),
    ),
    LoreBeatDef(
        id="act3_floor15",
        floor=15,
        trigger="floor_end",
        act=3,
        arbiter_text=(
            "Aethon lingers longer this time. For the first time, they seem almost... emotional."
        ),
        aethon_text=(
            "The arena is my thesis — that mortal beings, given "
            "sufficient adversity, can exceed their design. "
            "Fifteen floors. You are the data that supports my "
            "argument. Don't stop now."
        ),
        dm_stage_direction=(
            "This is the philosophical heart of the narrative. "
            "Aethon built the Armillary to prove that mortals "
            "can transcend. The party is the best evidence "
            "they've ever found."
        ),
        lore_fragment_id="frag_aethon_thesis",
    ),
    # Returning players — deeper truths
    LoreBeatDef(
        id="act3_return_floor11",
        floor=11,
        trigger="floor_start",
        act=3,
        arbiter_text="Aethon appears without preamble, as to an old friend.",
        aethon_text=(
            "The Merchant made a deal with my rival — a "
            "being who believes mortals should be sheltered, "
            "not tested. That's why the Merchant can move "
            "freely. A compromise I tolerate because it adds "
            "an uncontrolled variable. More interesting data."
        ),
        dm_stage_direction=(
            "For returning expeditions: Aethon reveals the "
            "Merchant's backstory. There's a second entity "
            "— Aethon's philosophical rival — who disagrees "
            "with the testing approach."
        ),
        condition="run_number >= 3",
        lore_fragment_id="frag_merchant_rival",
    ),
    # === ACT 4: THE THESIS (Floors 16-19) ===
    LoreBeatDef(
        id="act4_floor16",
        floor=16,
        trigger="floor_start",
        act=4,
        arbiter_text=(
            "Something has changed. The Armillary's hostility "
            "softens — not in difficulty, but in intent. You "
            "feel it rooting for you. And that's somehow more "
            "frightening."
        ),
        aethon_text=None,
        dm_stage_direction=(
            "The arena becomes an ally, sort of. Beneficial "
            "effects are slightly more common. But encounters "
            "are harder than ever, because Aethon wants "
            "irrefutable proof."
        ),
    ),
    LoreBeatDef(
        id="act4_floor17",
        floor=17,
        trigger="floor_end",
        act=4,
        arbiter_text="Aethon's voice is different now. Quieter. More present.",
        aethon_text=(
            "I have watched a thousand expeditions. Most "
            "fail. Some succeed. But none have ever made me "
            "wonder if I should be afraid of the answer."
        ),
        dm_stage_direction=(
            "Aethon is vulnerable for the first time. The "
            "possibility that the party might actually prove "
            "the thesis — that mortals can exceed their "
            "design — has implications Aethon hasn't "
            "considered."
        ),
        lore_fragment_id="frag_aethon_doubt",
    ),
    LoreBeatDef(
        id="act4_floor18",
        floor=18,
        trigger="floor_start",
        act=4,
        arbiter_text="Aethon appears with unusual gravity.",
        aethon_text=(
            "One more thing stands between you and the proof "
            "I've sought for millennia. I will not make it "
            "easy. That would invalidate everything."
        ),
        dm_stage_direction=(
            "The stakes are explicit. Floor 18-19 should be "
            "the hardest combat of the run. Aethon needs the "
            "proof to be earned."
        ),
    ),
    LoreBeatDef(
        id="act4_floor19",
        floor=19,
        trigger="floor_end",
        act=4,
        arbiter_text=(
            "The Arbiter's voice merges with Aethon's. For "
            "a moment, you cannot tell them apart."
        ),
        aethon_text=(
            "You have earned what comes next. The final "
            "floor is not a test — it is a conversation. "
            "Come."
        ),
        dm_stage_direction=(
            "The boundary between Arbiter and Aethon blurs. "
            "This is the threshold moment before the finale."
        ),
        lore_fragment_id="frag_threshold",
    ),
    # === ACT 5: THE REVELATION (Floor 20) ===
    LoreBeatDef(
        id="act5_floor20_start",
        floor=20,
        trigger="floor_start",
        act=5,
        arbiter_text=(
            "The arena is different here. The walls are "
            "translucent. Beyond them: the void between "
            "planes. The Armillary's true form — an "
            "impossibly complex orrery of light and shadow "
            "— is visible for the first time."
        ),
        aethon_text=(
            "Welcome to the heart of my creation. Everything "
            "you've faced was preparation for this moment."
        ),
        dm_stage_direction=(
            "Floor 20 should feel transcendent. The arena is "
            "no longer a dungeon — it's the core of a cosmic "
            "machine. Describe it with wonder, not just "
            "danger."
        ),
        lore_fragment_id="frag_armillary_truth",
    ),
    LoreBeatDef(
        id="act5_floor20_end",
        floor=20,
        trigger="floor_end",
        act=5,
        arbiter_text=(
            "Aethon stands before you. Not as a hologram or "
            "a voice — as a physical being, for the first "
            "time. The Armillary hums with anticipation."
        ),
        aethon_text=(
            "You've reached the end. I built this place to "
            "answer one question: can mortals exceed their "
            "design? You have one final choice. Join the "
            "Armillary as my champion — like Korvath, but "
            "with full knowledge of what you become. Or "
            "challenge me, and prove that mortals don't need "
            "a thesis to be extraordinary."
        ),
        dm_stage_direction=(
            "This is THE moment. Present the choice clearly. "
            "Both options are valid endings. If they fight: "
            "proceed to the Aethon encounter. If they join: "
            "describe the transformation and what it means "
            "for the next run."
        ),
        lore_fragment_id="frag_final_choice",
    ),
    LoreBeatDef(
        id="act5_victory",
        floor=20,
        trigger="arena_end",
        act=5,
        arbiter_text=(
            "Aethon falls — not in defeat, but in "
            "satisfaction. The Armillary pulses once, twice, "
            "then settles."
        ),
        aethon_text=(
            "You've proven my thesis. Go. And know that "
            "I'll be watching for the next ones who might "
            "match you. Another cycle begins."
        ),
        dm_stage_direction=(
            "Aethon is not destroyed — they acknowledge the "
            "result. The Armillary resets, hinting at the "
            "meta-progression loop. Credits moment."
        ),
        condition="aethon_defeated",
        lore_fragment_id="frag_thesis_proven",
    ),
    LoreBeatDef(
        id="act5_defeat",
        floor=20,
        trigger="arena_end",
        act=5,
        arbiter_text="The party falls. Aethon stands in silence for a long moment.",
        aethon_text=(
            "Not yet. But you came closer than almost "
            "anyone. The Armillary will remember this "
            "attempt. Return when you are ready."
        ),
        dm_stage_direction=(
            "Even in defeat, this should feel earned and "
            "meaningful. The party pushed to the final "
            "encounter. Aethon's respect is genuine."
        ),
        condition="aethon_not_defeated",
    ),
    # Returning players — final run
    LoreBeatDef(
        id="act5_return_floor20",
        floor=20,
        trigger="floor_start",
        act=5,
        arbiter_text=(
            "Aethon is already waiting. They look different "
            "— more human, less alien. As if your repeated "
            "challenges have changed them."
        ),
        aethon_text=(
            "You come back. Again and again. Do you know "
            "what that means? It means you've already "
            "exceeded your design. The fight is a formality "
            "now. But I still need the data."
        ),
        dm_stage_direction=(
            "For returning expeditions: Aethon has evolved. "
            "Each run changes them a little. They're more "
            "respectful, more honest, more... human."
        ),
        condition="run_number >= 2",
    ),
]


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

_BEAT_INDEX: dict[str, LoreBeatDef] = {b.id: b for b in LORE_BEATS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_lore_beat(beat_id: str) -> LoreBeatDef | None:
    """Return a lore beat by id."""
    return _BEAT_INDEX.get(beat_id)


def get_lore_beats_for_floor(
    floor_number: int,
    run_number: int = 1,
    trigger: str | None = None,
    context: dict | None = None,
) -> list[LoreBeatDef]:
    """Return all lore beats that should fire for a given floor and context.

    Args:
        floor_number: Current floor.
        run_number: Which run this is (1-indexed).
        trigger: Filter by trigger type ("floor_start", "floor_end", etc.).
        context: Dict with keys like "deaths_this_run", "aethon_defeated", etc.

    Returns:
        List of applicable lore beats, sorted by act.
    """
    ctx = context or {}
    results: list[LoreBeatDef] = []

    for beat in LORE_BEATS:
        if beat.floor != floor_number:
            continue
        if trigger and beat.trigger != trigger:
            continue
        if not _check_condition(beat.condition, run_number, ctx):
            continue
        results.append(beat)

    return sorted(results, key=lambda b: b.act)


def _check_condition(condition: str | None, run_number: int, context: dict) -> bool:
    """Evaluate a simple condition string against run context."""
    if condition is None:
        return True

    if condition == "run_number >= 2":
        return run_number >= 2
    if condition == "run_number >= 3":
        return run_number >= 3
    if condition == "aethon_defeated":
        return context.get("aethon_defeated", False)
    if condition == "aethon_not_defeated":
        return not context.get("aethon_defeated", False)
    if condition.startswith("deaths >"):
        threshold = int(condition.split(">")[1].strip())
        return context.get("deaths_this_run", 0) > threshold

    return True
