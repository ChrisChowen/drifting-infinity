"""Encounter hook generation.

Produces a 1-2 sentence dramatic context for why this encounter matters —
the narrative stakes beyond "kill the monsters." Draws from the encounter
template, objective, theme, floor position, and danger rating.
"""

import random

# ---------------------------------------------------------------------------
# Hook pools by encounter template
# ---------------------------------------------------------------------------

TEMPLATE_HOOKS: dict[str, list[str]] = {
    "hold_and_flank": [
        "They've set a trap — a wall of steel to pin you down"
        " while blades come from behind. Break the formation"
        " or be ground to dust.",
        "The enemy knows this terrain. They hold the"
        " chokepoints and send their fastest to your flanks."
        " You need to outmaneuver them.",
        "A coordinated force — disciplined, organized, and"
        " waiting. They fight as a unit. Disrupt their"
        " cohesion to survive.",
    ],
    "focus_fire": [
        "Ranged death awaits. Every second in the open is a"
        " second closer to a volley that can end a life.",
        "They've chosen their kill zone. If you stand still, you die. Close the distance — fast.",
        "The backline is the real threat. Everything in front"
        " of you exists to buy them time to bring you down.",
    ],
    "attrition": [
        "These creatures are built to outlast you. This is a"
        " war of endurance — and they have the advantage.",
        "They don't need to kill you quickly. They just need to bleed you dry, one cut at a time.",
        "Durability is their weapon. If you don't focus fire"
        " and eliminate threats efficiently, your resources"
        " will run out before their hit points do.",
    ],
    "area_denial": [
        "The arena itself becomes the enemy. Every step is a"
        " calculation, every position a compromise.",
        "They don't need to reach you. They just need to make"
        " sure you can't reach them — or anyone else.",
        "Zones of pain and control spread across the"
        " battlefield. Freedom of movement is the first"
        " casualty.",
    ],
    "ambush": [
        "You're not alone. You haven't been alone since you entered. They were here first.",
        "The darkness has teeth. Something is watching, waiting for the perfect moment to strike.",
        "They know you're coming. You don't know where they are. That asymmetry is lethal.",
    ],
    "boss": [
        "One creature dominates the arena. Everything else is"
        " a distraction. Kill the king or fall to its court.",
        "This is the challenge the floor has been building"
        " toward. Everything before was preparation.",
        "A apex predator, surrounded by lesser creatures that"
        " serve its will. The hierarchy is clear.",
    ],
    "swarm_rush": [
        "They come in waves. Each one is weak, but together they are an avalanche.",
        "Numbers are the enemy. Area effects are your lifeline. Don't let them surround you.",
        "A tide of creatures surges forward. Individual threats are trivial; the mass is lethal.",
    ],
    "elite_duel": [
        "A worthy opponent. No tricks, no minions — just raw power against raw power.",
        "The arena has chosen a champion. You must answer in kind.",
        "This creature earned its place at the top of the food chain. Prove you belong above it.",
    ],
    "pincer_strike": [
        "Enemies converge from multiple directions. There is no safe facing, no protected flank.",
        "They attack from everywhere at once. Coordination"
        " and battlefield control are your only defense.",
        "A coordinated assault from multiple vectors. They planned this. Did you?",
    ],
    "dragons_court": [
        "A dragon holds court, and its servants leap to obey."
        " The wyrm is the key — and the deadliest threat.",
        "Dragonfire and claws, supported by fanatics who"
        " worship the beast. Take the head, and the body"
        " falls.",
        "The arena burns with draconic fury. Lesser creatures"
        " scatter before the dragon's wrath — but they"
        " still bite.",
    ],
}

# ---------------------------------------------------------------------------
# Danger-level modifiers
# ---------------------------------------------------------------------------

DANGER_MODIFIERS: dict[str, list[str]] = {
    "Challenging": [
        "This should be manageable — but the Armillary punishes complacency.",
        "A test, not a trial. But treat it lightly at your peril.",
    ],
    "Dangerous": [
        "The stakes are real. Mistakes here will cost hit points and spell slots.",
        "A genuine threat. Coordination and resource management will be tested.",
    ],
    "Brutal": [
        "This is where characters die. Play smart, play together, or don't play at all.",
        "The Director has escalated. Casualties are likely without excellent tactics.",
    ],
    "Lethal": [
        "The Armillary has stopped playing. This encounter is designed to end runs.",
        "Lethal. Every decision matters. There is no room for error.",
    ],
}

# ---------------------------------------------------------------------------
# Floor position modifiers
# ---------------------------------------------------------------------------

FLOOR_POSITION_FLAVOR: dict[str, list[str]] = {
    "opener": [
        "The floor begins.",
        "A new floor, a new rhythm. The Armillary tests your readiness.",
    ],
    "rising": [
        "The pressure builds. The Director is watching how you handle escalation.",
        "Each arena on this floor has been harder than the last. This trend continues.",
    ],
    "peak": [
        "This is the peak. The hardest encounter on the"
        " floor. Everything after is resolution — if you"
        " survive.",
        "The Director's intensity curve crests here. Steel yourselves.",
    ],
    "resolution": [
        "The floor nears its end. One more push and the respite of transition awaits.",
        "The worst is behind you. But 'behind you' doesn't mean 'gone.'",
    ],
}


# ---------------------------------------------------------------------------
# Theme-specific hooks — used when a floor theme is active
# ---------------------------------------------------------------------------

THEME_HOOKS: dict[str, list[str]] = {
    "undead_horde": [
        "The dead here do not rest. Something commands them — find it and end this.",
        "Each corpse that falls may rise again. Strike true, and strike fast.",
    ],
    "goblinoid_warband": [
        "Goblins fight dirty. Watch for traps, feints, and flanking maneuvers.",
        "The warband is cunning but cowardly. Kill the leader and the rest may break.",
    ],
    "dragons_lair": [
        "Dragon fire reshapes the battlefield. Scatter to survive the breath, then"
        " reunite to bring the beast down.",
        "The dragon's servants exist to absorb your resources. Don't waste your best"
        " on the minions.",
    ],
    "demonic_incursion": [
        "Demons feed on chaos. Maintain formation, protect your casters, and close"
        " the rift if you can.",
        "The fiends grow stronger the longer the rift stays open. End this quickly.",
    ],
    "fey_court": [
        "Nothing here is what it seems. Trust your saves, not your eyes.",
        "The fey fight with charm and misdirection. Resist the enchantments and the"
        " real threats reveal themselves.",
    ],
    "elemental_chaos": [
        "Elemental creatures embody their element. Use opposing damage types for"
        " maximum effect.",
        "The elements are unstable here. Environmental hazards may shift mid-combat.",
    ],
    "aberrant_horror": [
        "Do not look directly at them for too long. Psychic defenses are critical.",
        "These things don't think like you. Conventional tactics may not apply.",
    ],
    "lycanthrope_pack": [
        "Silver and magic bypass their resistance. Mundane weapons alone won't win this.",
        "The pack hunts together. Isolate individuals and they become vulnerable.",
    ],
    "construct_workshop": [
        "Constructs don't tire, don't fear, and don't negotiate. Exploit their"
        " predictability — they follow programming, not instinct.",
        "Magic resistance is common in constructs. Physical damage dealers lead the charge.",
    ],
    "giant_kin": [
        "Giants hit like avalanches. Spread out to avoid being caught in the same swing.",
        "Size is both their weapon and their weakness. Use the terrain against them.",
    ],
    "serpent_cult": [
        "Poison is their weapon of choice. Keep antidotes ready and watch for ambushes.",
        "The cult fights in layers — scouts, then warriors, then the serpent priests.",
    ],
    "ooze_infestation": [
        "Slashing damage splits some oozes into smaller threats. Choose your damage"
        " types carefully.",
        "Oozes are mindless but relentless. They dissolve armor and weapons alike.",
    ],
    "spiders_web": [
        "The webs restrict movement. Fire clears them, but reveals your position.",
        "Spider venom paralyzes. Protect your frontline and don't get separated.",
    ],
    "bandit_raiders": [
        "Professional killers with humanoid intelligence. They'll target your healer first.",
        "Raiders retreat when outmatched. Press the advantage before they regroup.",
    ],
    "celestial_test": [
        "The celestials test resolve, not just strength. Showing mercy may yield"
        " unexpected rewards.",
        "Divine beings fight with purpose. Understand their test to pass it efficiently.",
    ],
    "infernal_pact": [
        "Devils exploit contracts and loopholes. Every offer is a trap with teeth.",
        "Fire resistance is essential. The Nine Hells burn everything they touch.",
    ],
    "natures_wrath": [
        "The plants fight on their own terrain. Fire is effective but dangerous in"
        " dense vegetation.",
        "Nature's creatures regenerate in natural environments. Deny them that advantage.",
    ],
    "shadow_court": [
        "Light is your weapon here. Darkness empowers them and weakens you.",
        "Shadow creatures drain strength from the living. End this before exhaustion sets in.",
    ],
    "aquatic_terror": [
        "Water is their element. Fight on dry ground where possible and deny them"
        " the advantage of depth.",
        "Aquatic creatures hit harder near water. Control the terrain or drown in the tide.",
    ],
    "clockwork_army": [
        "Clockwork soldiers follow precise protocols. Disrupt their formation and"
        " their efficiency collapses.",
        "They march in perfect coordination. Target the command unit to break the pattern.",
    ],
}


def _arena_position(arena_number: int, total_arenas: int) -> str:
    if arena_number == 1:
        return "opener"
    if total_arenas > 0 and arena_number >= total_arenas:
        return "resolution"
    ratio = arena_number / max(total_arenas, 1)
    if ratio >= 0.6:
        return "peak"
    return "rising"


def generate_encounter_hook(
    template_name: str,
    danger_rating: str,
    floor_number: int,
    arena_number: int,
    total_arenas: int = 4,
    theme_name: str = "",
    theme_id: str = "",
) -> str:
    """Generate a 1-2 sentence encounter hook for DM context.

    When a theme is active, uses theme-specific hooks 60% of the time.
    """
    # Theme hook (60% when active)
    if theme_id and theme_id in THEME_HOOKS and random.random() < 0.6:
        hook = random.choice(THEME_HOOKS[theme_id])
    else:
        pool = TEMPLATE_HOOKS.get(
            template_name, TEMPLATE_HOOKS.get("hold_and_flank", [""])
        )
        hook = random.choice(pool)

    # Optionally append danger modifier for Brutal/Lethal
    if danger_rating in ("Brutal", "Lethal"):
        modifier = random.choice(DANGER_MODIFIERS.get(danger_rating, [""]))
        hook = f"{hook} {modifier}"

    return hook
