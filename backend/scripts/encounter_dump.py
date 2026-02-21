#!/usr/bin/env python3
"""Dump all encounters for a full 20-floor run: enemies + objectives per arena."""

import asyncio
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.data.encounter_themes import select_theme_for_floor
from app.database import async_session
from app.engine.combat.rest import rest_schedule_for_floor
from app.engine.difficulty.intensity_curve import compute_intensity_curve
from app.engine.difficulty.target_computer import compute_difficulty_target
from app.engine.encounter.environment_selector import select_floor_biome
from app.engine.encounter.pipeline import PipelineInput, generate_encounter
from app.engine.leveling import XP_TO_LEVEL, compute_arena_xp_award, compute_power_xp_bonus
from app.engine.scaling import get_scaling_params, get_tier
from app.models.monster import Monster


async def load_monster_dicts() -> list[dict]:
    async with async_session() as session:
        result = await session.execute(select(Monster))
        monsters = result.scalars().all()
        return [
            {
                "id": m.id, "slug": m.slug, "name": m.name,
                "cr": m.cr, "xp": m.xp, "hp": m.hp, "ac": m.ac,
                "size": m.size, "creature_type": m.creature_type,
                "tactical_role": m.tactical_role,
                "secondary_role": m.secondary_role,
                "mechanical_signature": m.mechanical_signature,
                "vulnerabilities": m.vulnerabilities or [],
                "weak_saves": m.weak_saves or [],
                "environments": m.environments or [],
                "statblock": m.statblock,
            }
            for m in monsters
        ]


async def main():
    random.seed(42)
    monster_dicts = await load_monster_dicts()
    print(f"Loaded {len(monster_dicts)} monsters\n")

    party_size = 4
    party_level = 1
    ppc = 1.0
    total_xp_per_char = 0

    lines = []
    used_floor_themes: list[str] = []

    for floor_num in range(1, 21):
        tier = get_tier(party_level)
        scaling = get_scaling_params(party_size)
        total_arenas = min(scaling.max_arenas_per_floor, 3 + (tier - 1))

        floor_biome = select_floor_biome(floor_num, party_level, monster_dicts)

        # Floor theme: select once per floor
        floor_theme_def = select_theme_for_floor(
            biome=floor_biome,
            floor_number=floor_num,
            used_themes=used_floor_themes[-3:],
        )
        floor_theme_id = floor_theme_def.id if floor_theme_def else None
        floor_theme_name = floor_theme_def.name if floor_theme_def else "None"
        if floor_theme_id:
            used_floor_themes.append(floor_theme_id)

        # Rest schedule for attrition-aware pacing
        rest_sched = rest_schedule_for_floor(total_arenas, scaling.short_rests_per_floor)

        # Floor difficulty
        intensity = compute_intensity_curve(
            1, total_arenas, floor_num, ppc, rest_schedule=rest_sched,
        )
        diff_target = compute_difficulty_target(
            base_intensity=intensity.intensity,
            party_power_coefficient=ppc,
        )

        lines.append(f"## Floor {floor_num} — Party Level {party_level} (Tier {tier})")
        lines.append(f"Biome: {floor_biome or 'Any'} | Theme: {floor_theme_name} | "
                      f"Difficulty: {diff_target.difficulty} "
                      f"(×{diff_target.xp_multiplier:.2f}) | Intensity: {intensity.intensity:.2f}")
        lines.append("")

        templates_used = []
        used_objectives = []
        exclude_monster_ids = set()
        used_environments = []
        floor_xp = 0

        for arena_num in range(1, total_arenas + 1):
            arena_intensity = compute_intensity_curve(
                arena_num, total_arenas, floor_num, ppc,
                rest_schedule=rest_sched,
            )

            is_boss = (arena_num == total_arenas and floor_num % 4 == 0)
            party_damage_types = ["slashing", "piercing", "radiant", "fire", "lightning", "cold"]

            # Compute arc position
            if arena_num == 1:
                arc_position = "opener"
            elif arena_num == total_arenas:
                arc_position = "climax"
            else:
                arc_position = "middle"

            inp = PipelineInput(
                party_level=party_level,
                party_size=party_size,
                difficulty=diff_target.difficulty,
                floor_number=floor_num,
                arena_number=arena_num,
                templates_used=templates_used,
                party_damage_types=party_damage_types,
                difficulty_multiplier=diff_target.xp_multiplier,
                used_objectives=used_objectives,
                is_boss=is_boss,
                exclude_monster_ids=exclude_monster_ids,
                biome_constraint=floor_biome,
                used_environments=used_environments,
                floor_theme=floor_theme_id,
                arena_arc_position=arc_position,
            )

            try:
                proposal = generate_encounter(inp, monster_dicts)
            except Exception as e:
                lines.append(f"### Arena {arena_num}: FAILED — {e}")
                lines.append("")
                continue

            templates_used.append(proposal.template)
            if proposal.objective_id:
                used_objectives.append(proposal.objective_id)
            if proposal.environment:
                used_environments.append(proposal.environment)
            for c in proposal.creatures:
                exclude_monster_ids.add(c.monster_id)

            # Creature summary
            creature_list = []
            for c in proposal.creatures:
                label = f"{c.name} (CR {c.cr})"
                if c.count > 1:
                    label = f"{c.count}× {label}"
                creature_list.append(label)

            raw_xp = sum(c.xp * c.count for c in proposal.creatures)
            leveling_speed = compute_power_xp_bonus(
                gacha_items_owned=0, floors_completed=floor_num - 1,
            )
            xp_award = compute_arena_xp_award(raw_xp, party_size, leveling_speed)
            floor_xp += xp_award

            lines.append(
                f"### Arena {arena_num} — {arena_intensity.phase.value.title()} "
                f"| {proposal.danger_rating}"
            )
            lines.append(f"**Template:** {proposal.template} | "
                         f"**Environment:** {proposal.environment_name}")
            lines.append(f"**Objective:** {proposal.objective_name or 'Extermination'}")
            if proposal.objective_description:
                lines.append(f"> {proposal.objective_description}")
            lines.append(f"**Theme:** {proposal.theme_name or 'None'}")
            lines.append(f"**XP Budget:** {proposal.xp_budget} | "
                         f"**Adjusted XP:** {proposal.adjusted_xp} | "
                         f"**XP Award:** {xp_award}/player")
            lines.append(f"**Creatures ({proposal.creature_count}):** "
                         + ", ".join(creature_list))
            if is_boss:
                lines.append("**[BOSS ARENA]**")
            lines.append("")

        # Level up check
        total_xp_per_char += floor_xp
        next_level_xp = XP_TO_LEVEL.get(party_level, 999999)
        leveled = False
        while next_level_xp > 0 and total_xp_per_char >= next_level_xp and party_level < 20:
            party_level += 1
            total_xp_per_char -= next_level_xp
            next_level_xp = XP_TO_LEVEL.get(party_level, 999999)
            leveled = True
        if leveled:
            lines.append(f"*Party levels up to {party_level}!*")
            lines.append("")

        lines.append("---")
        lines.append("")

    output = "\n".join(lines)
    report_path = Path(__file__).parent / "encounter_dump.md"
    report_path.write_text(output)
    print(output)
    print(f"\nSaved to {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
