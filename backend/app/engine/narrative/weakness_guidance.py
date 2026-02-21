"""Weakness exploit guidance for DMs.

Converts the mechanical Weakness Exploit system (GDD 2.4) into DM-readable
tips about how the party can exploit creature vulnerabilities and weak saves.
This replaces the state-tracking WeaknessExploitState with static guidance text.
"""

from dataclasses import dataclass


@dataclass
class WeaknessTip:
    """A single weakness exploit tip for the DM."""

    creature_name: str
    exploit_type: str  # "vulnerability" or "weak_save"
    detail: str  # e.g., "fire" or "DEX"
    tip_text: str


# ---------------------------------------------------------------------------
# Rules reference text
# ---------------------------------------------------------------------------

WEAKNESS_EXPLOIT_RULES = (
    "**Weakness Exploit ('One More' System):** When a party member hits a creature's "
    "vulnerability or targets a weak save, trigger a Weakness Exploit event. An ally "
    "gains a Bonus Reaction. Cap: 2 exploits per round. Chain bonus: 3+ consecutive "
    "exploits grants +2 damage per hit."
)

FINAL_STAND_RULES = (
    "**Final Stand:** When a character drops to 0 HP, they get one final action before "
    "falling unconscious. The DC is 10 + (deaths this run × 2). On success: one action "
    "(attack, spell, or Help). On failure: fall unconscious immediately. This costs a "
    "life if the character actually dies."
)

MOMENTUM_RECOVERY_RULES = (
    "**Momentum Recovery:** Between arenas on the same floor, the party recovers based "
    "on performance. Fast clear (≤3 rounds): short rest equivalent. Standard clear: "
    "hit dice recovery only. Slow clear (≥8 rounds): no recovery — the Armillary "
    "doesn't reward hesitation."
)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


def generate_weakness_tips(creatures: list[dict]) -> list[WeaknessTip]:
    """Generate weakness exploit tips from creature data.

    Args:
        creatures: List of creature dicts with name, vulnerabilities, weak_saves
    """
    tips: list[WeaknessTip] = []

    for creature in creatures:
        name = creature.get("name", "Unknown")
        vulns = creature.get("vulnerabilities", [])
        weak_saves = creature.get("weak_saves", [])
        count = creature.get("count", 1)

        name_display = f"{name} (×{count})" if count > 1 else name

        for vuln in vulns:
            tip = WeaknessTip(
                creature_name=name_display,
                exploit_type="vulnerability",
                detail=str(vuln),
                tip_text=(
                    f"{name_display} is vulnerable to {vuln} damage. Attacks dealing "
                    f"{vuln} damage trigger a Weakness Exploit — grant a Bonus Reaction "
                    f"to an ally."
                ),
            )
            tips.append(tip)

        for save in weak_saves:
            # weak_saves may be dicts like {"ability": "int", "modifier": -3}
            # or simple strings like "int". Normalise to a readable label.
            if isinstance(save, dict):
                ability = save.get("ability", "unknown")
                modifier = save.get("modifier", 0)
                save_label = ability.upper()
                detail = f"{save_label} ({modifier:+d})"
            else:
                save_label = str(save).upper()
                detail = save_label

            tip = WeaknessTip(
                creature_name=name_display,
                exploit_type="weak_save",
                detail=detail,
                tip_text=(
                    f"{name_display} has a weak {save_label} save ({detail}). "
                    f"Spells and abilities targeting {save_label} saves are "
                    f"significantly more likely to land and trigger Weakness Exploit."
                ),
            )
            tips.append(tip)

    return tips


def build_roguelike_reference() -> dict[str, str]:
    """Build a quick-reference dict of roguelike rules for DM display."""
    return {
        "weakness_exploit": WEAKNESS_EXPLOIT_RULES,
        "final_stand": FINAL_STAND_RULES,
        "momentum_recovery": MOMENTUM_RECOVERY_RULES,
    }
