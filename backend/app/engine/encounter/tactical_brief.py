"""Tactical brief generation per GDD 4.8.

Generates a tactical summary for the DM based on the encounter composition.
"""

from app.engine.encounter.combos import ComboResult
from app.engine.encounter.templates import TEMPLATES


def generate_tactical_brief(
    template_name: str,
    creature_summaries: list[dict],
    combos: list[ComboResult],
    warnings: list[str],
) -> str:
    """Generate a tactical brief for the DM.

    Args:
        template_name: The encounter template used
        creature_summaries: List of dicts with name, count, role, cr
        combos: Active combo interactions
        warnings: Any warnings from validation/sanity checks
    """
    template = TEMPLATES.get(template_name)
    parts = []

    # Template overview
    if template:
        parts.append(f"**{template.name}**: {template.tactical_brief_template}")

    # Creature lineup
    lineup = []
    for c in creature_summaries:
        count = c.get("count", 1)
        name = c.get("name", "Unknown")
        role = c.get("role", "")
        cr = c.get("cr", 0)
        if count > 1:
            lineup.append(f"{count}x {name} (CR {cr}, {role})")
        else:
            lineup.append(f"{name} (CR {cr}, {role})")

    if lineup:
        parts.append("**Creatures:** " + ", ".join(lineup))

    # Active combos
    if combos:
        combo_lines = [f"- {c.combo_name}: {c.description}" for c in combos]
        parts.append("**Active Combos:**\n" + "\n".join(combo_lines))

    # Warnings
    if warnings:
        parts.append("**Warnings:** " + "; ".join(warnings))

    return "\n\n".join(parts)
