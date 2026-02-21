"""DM guidance box generation.

Produces sidebar-style guidance boxes for the DM — the kind you'd see
in a published adventure module. Covers tactical tips, combo warnings,
difficulty context, and environmental suggestions.
"""

import random
from dataclasses import dataclass


@dataclass
class GuidanceBox:
    """A single DM guidance box — title + body text."""

    title: str
    content: str
    category: str  # "tactical", "combo", "difficulty", "environment", "roleplay"


# ---------------------------------------------------------------------------
# Tactical guidance by encounter template
# ---------------------------------------------------------------------------

TEMPLATE_TACTICS: dict[str, list[GuidanceBox]] = {
    "hold_and_flank": [
        GuidanceBox(
            "Running the Formation",
            "The frontline creatures should hold a chokepoint while flankers approach from "
            "behind or to the side. If the party breaks the front line early, have the flankers "
            "switch to a direct assault — they've lost their advantage and know it.",
            "tactical",
        ),
        GuidanceBox(
            "Disrupting the Plan",
            "Smart parties will try to prevent the flank by controlling the approach. Reward "
            "creative use of Wall spells, difficult terrain, or readied actions to intercept "
            "the flankers.",
            "tactical",
        ),
    ],
    "focus_fire": [
        GuidanceBox(
            "Running the Kill Zone",
            "The ranged creatures should focus fire on the same target each round. If the "
            "party spreads out, have the shooters split only when forced. Melee screens exist "
            "to buy the backline time — they don't need to deal major damage.",
            "tactical",
        ),
        GuidanceBox(
            "Closing the Distance",
            "The party needs to close range fast. If they're struggling, consider having one "
            "ranged creature use its movement to reposition rather than attack — maintaining "
            "the pressure without being merciless.",
            "tactical",
        ),
    ],
    "attrition": [
        GuidanceBox(
            "War of Endurance",
            "These creatures are built to outlast the party. They should fight defensively, "
            "using healing, damage resistance, or high HP to drag the fight out. The real "
            "threat is resource drain, not burst damage.",
            "tactical",
        ),
        GuidanceBox(
            "Resource Management",
            "Track the party's spell slot usage. If they're burning high-level slots early, "
            "the encounter is working as intended. If they're being conservative, the "
            "creatures should press harder to force expenditure.",
            "tactical",
        ),
    ],
    "area_denial": [
        GuidanceBox(
            "Controlling the Battlefield",
            "Area denial creatures should layer their effects to restrict movement. Place "
            "hazards to cut off retreat routes and force the party into unfavorable positions. "
            "The arena itself is a weapon.",
            "tactical",
        ),
    ],
    "ambush": [
        GuidanceBox(
            "Setting the Ambush",
            "Ambush creatures begin hidden. Call for Perception checks (passive or active) "
            "before the fight starts. Creatures that remain hidden get a surprise round. "
            "After the initial strike, they should try to disengage and re-hide if possible.",
            "tactical",
        ),
        GuidanceBox(
            "When the Ambush Fails",
            "If the party spots the ambush, don't force it. The creatures should adapt — "
            "a failed ambush becomes a standard fight, and the creatures know they've lost "
            "the element of surprise.",
            "tactical",
        ),
    ],
    "boss": [
        GuidanceBox(
            "Running the Boss",
            "The boss creature should use legendary actions and lair actions to maintain "
            "pressure between turns. Minions exist to absorb actions and protect the boss. "
            "If the party focuses the minions, the boss should punish them for ignoring it.",
            "tactical",
        ),
        GuidanceBox(
            "Boss Phases",
            "Consider changing the boss's behavior at half HP — more aggressive, uses "
            "different abilities, or retreats to a more defensible position. This creates "
            "a natural second phase without complex mechanics.",
            "tactical",
        ),
    ],
    "swarm_rush": [
        GuidanceBox(
            "Managing the Swarm",
            "Run the swarm creatures as groups sharing initiative. They should rush the "
            "nearest party member and try to surround. Area-effect spells will devastate "
            "them — that's the intended counter.",
            "tactical",
        ),
    ],
    "elite_duel": [
        GuidanceBox(
            "The Elite Opponent",
            "This creature fights smart and hits hard. It should target the party's biggest "
            "threat and use terrain to its advantage. Don't hold back — the encounter is "
            "designed around a single powerful foe.",
            "tactical",
        ),
    ],
    "pincer_strike": [
        GuidanceBox(
            "Converging Assault",
            "Enemies approach from multiple directions. Stagger their arrival by 1-2 rounds "
            "if the party is struggling — it creates tension without being overwhelming. If "
            "the party is strong, have everyone arrive at once.",
            "tactical",
        ),
    ],
    "dragons_court": [
        GuidanceBox(
            "The Dragon's Lair",
            "The dragon is the centerpiece. Its servants act on their own initiative but "
            "coordinate with the dragon's attacks. If the party ignores the servants to "
            "focus the dragon, have the servants target the party's healers and casters.",
            "tactical",
        ),
    ],
}

# ---------------------------------------------------------------------------
# Difficulty context guidance
# ---------------------------------------------------------------------------

DIFFICULTY_GUIDANCE: dict[str, list[GuidanceBox]] = {
    "Challenging": [
        GuidanceBox(
            "Difficulty: Challenging",
            "This encounter should test the party without serious risk of death. "
            "If a character drops to 0 HP, the party should have the resources to "
            "recover. Play the creatures competently but not ruthlessly.",
            "difficulty",
        ),
    ],
    "Dangerous": [
        GuidanceBox(
            "Difficulty: Dangerous",
            "This is a real fight. The party will need to use resources and coordinate. "
            "Character death is possible if they make significant tactical errors. "
            "Play the creatures at full intelligence.",
            "difficulty",
        ),
    ],
    "Brutal": [
        GuidanceBox(
            "Difficulty: Brutal",
            "Expect at least one character to drop to 0 HP. The party must play well "
            "to avoid deaths. If the fight goes badly, consider having creatures focus "
            "downed characters only if it makes tactical sense — not out of cruelty.",
            "difficulty",
        ),
        GuidanceBox(
            "Roguelike Rules Reminder",
            "Character death costs a life. Remind the party of their current life count "
            "and Final Stand rules before the fight begins.",
            "difficulty",
        ),
    ],
    "Lethal": [
        GuidanceBox(
            "Difficulty: Lethal",
            "This encounter is designed to push the party to their limits. Multiple "
            "deaths are likely. Play the creatures at maximum intelligence — they "
            "focus fire, target weaknesses, and fight to kill. The Armillary demands it.",
            "difficulty",
        ),
        GuidanceBox(
            "TPK Risk",
            "If the entire party drops, this triggers a TPK. Check Phoenix Protocol "
            "availability. If no Phoenix, the run ends here. Make sure the players "
            "understand the stakes before combat begins.",
            "difficulty",
        ),
    ],
}

# ---------------------------------------------------------------------------
# Environment tips
# ---------------------------------------------------------------------------

ENVIRONMENT_TIPS: dict[str, list[GuidanceBox]] = {
    "forest": [
        GuidanceBox(
            "Forest Terrain Tips",
            "Trees provide three-quarters cover. Creatures with ranged attacks should "
            "use the trees to break line of sight after attacking. The undergrowth "
            "creates natural difficult terrain — use it to slow melee rushes.",
            "environment",
        ),
    ],
    "underdark": [
        GuidanceBox(
            "Darkvision Matters",
            "Most Underdark creatures have darkvision or blindsight. If the party relies "
            "on torchlight, they're broadcasting their position. Consider tracking light "
            "sources — creatures will target the light-bearer.",
            "environment",
        ),
    ],
    "swamp": [
        GuidanceBox(
            "Swamp Movement",
            "Waist-deep water makes most of the battlefield difficult terrain. Creatures "
            "native to the swamp should ignore this penalty. This gives them a massive "
            "mobility advantage — use it.",
            "environment",
        ),
    ],
    "volcanic_caldera": [
        GuidanceBox(
            "Lava Hazards",
            "Lava rivers deal 6d10 fire damage. Use them as barriers, not traps. Creatures "
            "should try to push or grapple party members toward lava — the threat alone "
            "changes positioning decisions.",
            "environment",
        ),
    ],
    "planar": [
        GuidanceBox(
            "Planar Chaos",
            "Reality is unreliable here. Use gravity shifts and teleportation portals to "
            "keep the battlefield dynamic. Roll randomly for gravity direction changes if "
            "using that optional rule.",
            "environment",
        ),
    ],
    "feywild_glade": [
        GuidanceBox(
            "Fey Trickery",
            "The Feywild plays by different rules. Illusions and teleportation are common. "
            "Have terrain shift between rounds — move a terrain piece 10 feet to keep "
            "the party off-balance.",
            "environment",
        ),
    ],
    "shadowfell_wastes": [
        GuidanceBox(
            "Despair and Darkness",
            "The Shadowfell drains hope. Consider imposing disadvantage on Charisma saves "
            "near shadow pools. Bright light sources have halved radius here — the "
            "darkness fights back.",
            "environment",
        ),
    ],
}


# ---------------------------------------------------------------------------
# Weakness exploit tips (DM-facing guidance)
# ---------------------------------------------------------------------------

WEAKNESS_TIP_TEMPLATES: list[str] = [
    "{creature_name} is vulnerable to {damage_type} damage. If the party exploits this, "
    "grant a Bonus Reaction to an ally — the 'One More' system rewards smart targeting.",
    "{creature_name} has a weak {save_type} save. Spells and abilities targeting this save "
    "are significantly more effective. This triggers Weakness Exploit if the party notices.",
    "Multiple creatures share a vulnerability to {damage_type}. Area-effect spells of that "
    "type will be devastating — and trigger exploit chains for bonus damage.",
]


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


def generate_dm_guidance(
    template_name: str,
    danger_rating: str,
    environment_key: str,
    creatures: list[dict],
) -> list[GuidanceBox]:
    """Generate DM guidance boxes for an encounter.

    Args:
        template_name: Encounter template name
        danger_rating: Danger rating string (Challenging/Dangerous/Brutal/Lethal)
        environment_key: Environment key
        creatures: List of creature dicts with name, vulnerabilities, weak_saves
    """
    boxes: list[GuidanceBox] = []

    # Template tactical guidance
    template_pool = TEMPLATE_TACTICS.get(template_name, [])
    if template_pool:
        boxes.append(random.choice(template_pool))

    # Difficulty context
    diff_pool = DIFFICULTY_GUIDANCE.get(danger_rating, [])
    boxes.extend(diff_pool)

    # Environment tips
    env_pool = ENVIRONMENT_TIPS.get(environment_key, [])
    if env_pool:
        boxes.append(random.choice(env_pool))

    # Weakness tips — generated from creature data
    for creature in creatures:
        name = creature.get("name", "Unknown")
        vulns = creature.get("vulnerabilities", [])
        weak_saves = creature.get("weak_saves", [])

        if vulns:
            tip = WEAKNESS_TIP_TEMPLATES[0].format(
                creature_name=name,
                damage_type=vulns[0],
            )
            boxes.append(GuidanceBox("Weakness Exploit Opportunity", tip, "tactical"))
            break  # One weakness tip is enough to avoid clutter

        if weak_saves:
            # weak_saves may be dicts or strings — normalise
            first_save = weak_saves[0]
            if isinstance(first_save, dict):
                save_label = first_save.get("ability", "unknown").upper()
            else:
                save_label = str(first_save).upper()
            tip = WEAKNESS_TIP_TEMPLATES[1].format(
                creature_name=name,
                save_type=save_label,
            )
            boxes.append(GuidanceBox("Weak Save Opportunity", tip, "tactical"))
            break

    return boxes
