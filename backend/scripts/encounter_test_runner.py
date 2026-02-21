#!/usr/bin/env python3
"""Encounter simulation test runner.

Generates encounters across a matrix of party sizes, levels, and floor
depths. Validates creature counts, XP budgets, objective selection,
affix stacking, and reward generation. Outputs a Markdown report.

Usage:
    cd backend
    python -m scripts.encounter_test_runner [--iterations 5]
"""

import argparse
import asyncio
import random
import sys
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import select

# ── Imports ──────────────────────────────────────────────────────────
from app.engine.encounter.pipeline import generate_encounter, PipelineInput
from app.data.arena_objectives import select_objective, ARENA_OBJECTIVES as OBJECTIVES
from app.data.floor_affixes import roll_affixes, FLOOR_AFFIXES
from app.data.reward_pool import generate_reward_choices, REWARD_POOL
from app.data.feat_definitions import get_feats_for_level, ALL_FEATS as FEATS
from app.database import async_session
from app.models.monster import Monster


# ── Test scenarios ───────────────────────────────────────────────────

SCENARIOS = [
    # (party_size, party_level, floor_number, arena_number, arena_count, floor_count)
    (4, 1, 1, 1, 4, 4),   # Standard party, floor 1 arena 1 (always Extermination)
    (4, 1, 1, 3, 4, 4),   # Standard party, floor 1 arena 3
    (4, 3, 2, 1, 4, 4),   # Mid-level, floor 2
    (4, 5, 2, 4, 4, 4),   # Mid-level, boss arena floor 2
    (4, 8, 3, 1, 4, 4),   # Higher level, floor 3
    (4, 12, 3, 3, 4, 4),  # High level, floor 3
    (4, 16, 4, 1, 4, 4),  # Very high, floor 4
    (4, 19, 4, 4, 4, 4),  # Epic level, boss arena (Epic Boons eligible)
    (2, 5, 2, 2, 4, 4),   # Small party
    (6, 5, 2, 2, 4, 4),   # Large party
    (3, 1, 1, 1, 4, 4),   # Small party, floor 1
    (5, 10, 3, 2, 4, 4),  # 5-player mid-high
]


@dataclass
class ScenarioResult:
    scenario_label: str
    iterations: int
    encounters_generated: int = 0
    errors: list[str] = field(default_factory=list)
    creature_counts: list[int] = field(default_factory=list)
    xp_budgets: list[int] = field(default_factory=list)
    templates_used: Counter = field(default_factory=Counter)
    objectives_selected: Counter = field(default_factory=Counter)
    affix_counts: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def run_encounter_scenario(
    party_size: int,
    party_level: int,
    floor_number: int,
    arena_number: int,
    arena_count: int,
    floor_count: int,
    iterations: int,
    available_monsters: list[dict] | None = None,
) -> ScenarioResult:
    label = f"P{party_size} L{party_level} F{floor_number} A{arena_number}"
    result = ScenarioResult(scenario_label=label, iterations=iterations)

    if not available_monsters:
        result.errors.append("No monsters loaded from DB")
        return result

    for _ in range(iterations):
        try:
            inp = PipelineInput(
                party_size=party_size,
                party_level=party_level,
                floor_number=floor_number,
                arena_number=arena_number,
                difficulty_multiplier=1.0,
            )

            proposal = generate_encounter(inp, available_monsters)

            result.encounters_generated += 1
            total_creatures = sum(c.count for c in proposal.creatures)
            result.creature_counts.append(total_creatures)
            result.xp_budgets.append(proposal.xp_budget)
            result.templates_used[proposal.template] += 1

            if proposal.objective_name:
                result.objectives_selected[proposal.objective_name] += 1

            if proposal.active_affixes:
                result.affix_counts.append(len(proposal.active_affixes))

            for w in proposal.warnings:
                result.warnings.append(w.message if hasattr(w, 'message') else str(w))

            # Sanity checks
            if total_creatures == 0:
                result.errors.append(f"Iteration produced 0 creatures")
            if proposal.xp_budget <= 0:
                result.errors.append(f"XP budget was {proposal.xp_budget}")

        except Exception as e:
            result.errors.append(f"{type(e).__name__}: {e}")

    return result


def test_objective_selection():
    """Verify objective selection logic across scenarios."""
    results = []

    # Floor 1, Arena 1 should always be Extermination
    for _ in range(10):
        obj = select_objective(1, 1, "standard", [], False)
        if obj.id != "extermination":
            results.append(f"ERROR: F1A1 got {obj.id} instead of extermination")

    # Floor 2+ should never repeat within a floor
    for _ in range(5):
        used: list[str] = []
        for arena in range(1, 5):
            obj = select_objective(2, arena, "standard", used, False)
            if obj.id in used:
                results.append(f"ERROR: Duplicate objective {obj.id} on floor 2")
            used.append(obj.id)

    # Boss template should force Extermination or Destruction
    for _ in range(10):
        obj = select_objective(3, 4, "standard", [], True)
        if obj.id not in ("extermination", "destruction"):
            results.append(f"ERROR: Boss got {obj.id}")

    return results if results else ["All objective selection tests passed"]


def test_affix_rolling():
    """Verify affix rolling logic."""
    results = []

    # Floor 1 should get exactly 1 affix
    for _ in range(10):
        affixes = roll_affixes(1)
        if len(affixes) != 1:
            results.append(f"ERROR: Floor 1 got {len(affixes)} affixes (expected 1)")

    # Floor 4 should get exactly 2
    for _ in range(10):
        affixes = roll_affixes(4)
        if len(affixes) != 2:
            results.append(f"ERROR: Floor 4 got {len(affixes)} affixes (expected 2)")

    # No duplicate affixes in a single roll
    for _ in range(20):
        affixes = roll_affixes(3)
        ids = [a.id for a in affixes]
        if len(ids) != len(set(ids)):
            results.append(f"ERROR: Duplicate affixes in single roll: {ids}")

    return results if results else ["All affix rolling tests passed"]


def test_reward_generation():
    """Verify reward pool generation."""
    results = []

    # Floor 1: should produce rewards
    choices = generate_reward_choices(1, count=3)
    if len(choices) != 3:
        results.append(f"ERROR: Floor 1 got {len(choices)} choices (expected 3)")

    # Feat rewards exist
    feat_choices = generate_reward_choices(2, count=3, categories=["feat"])
    if not feat_choices:
        results.append("ERROR: No feat rewards available at floor 2")

    # Epic Boon should only appear at floor 4+
    epic = [r for r in REWARD_POOL if r.id == "rew_feat_epic_boon"]
    if epic and epic[0].floor_min < 4:
        results.append(f"ERROR: Epic Boon floor_min is {epic[0].floor_min} (should be 4+)")

    return results if results else ["All reward generation tests passed"]


def test_feat_definitions():
    """Verify feat catalog."""
    results = []

    level_1_feats = get_feats_for_level(1)
    if len(level_1_feats) == 0:
        results.append("ERROR: No feats available at level 1")

    # Origin feats should be available at level 1
    origins = [f for f in level_1_feats if f.category == "origin"]
    if len(origins) == 0:
        results.append("ERROR: No origin feats at level 1")

    # Epic Boons should only appear at level 19+
    level_18_feats = get_feats_for_level(18)
    epic_at_18 = [f for f in level_18_feats if f.category == "epic_boon"]
    if len(epic_at_18) > 0:
        results.append(f"ERROR: {len(epic_at_18)} epic boons at level 18 (should be 0)")

    level_19_feats = get_feats_for_level(19)
    epic_at_19 = [f for f in level_19_feats if f.category == "epic_boon"]
    if len(epic_at_19) == 0:
        results.append("ERROR: No epic boons at level 19")

    results.append(f"Total feats: {len(FEATS)}")
    return results if results else [f"All feat tests passed ({len(FEATS)} feats)"]


def generate_report(
    scenario_results: list[ScenarioResult],
    objective_tests: list[str],
    affix_tests: list[str],
    reward_tests: list[str],
    feat_tests: list[str],
) -> str:
    lines = [
        "# Encounter Test Report",
        "",
        f"**Scenarios:** {len(scenario_results)} | "
        f"**Objectives:** {len(OBJECTIVES)} | "
        f"**Affixes:** {len(FLOOR_AFFIXES)} | "
        f"**Rewards:** {len(REWARD_POOL)} | "
        f"**Feats:** {len(FEATS)}",
        "",
    ]

    # Scenario results table
    lines.append("## Encounter Generation Scenarios")
    lines.append("")
    lines.append("| Scenario | Gen | Errors | Avg Creatures | Avg XP | Templates | Objectives |")
    lines.append("|----------|-----|--------|---------------|--------|-----------|------------|")

    total_errors = 0
    for r in scenario_results:
        avg_c = f"{sum(r.creature_counts)/len(r.creature_counts):.1f}" if r.creature_counts else "N/A"
        avg_xp = f"{sum(r.xp_budgets)/len(r.xp_budgets):.0f}" if r.xp_budgets else "N/A"
        templates = ", ".join(f"{k}({v})" for k, v in r.templates_used.most_common(3))
        objectives = ", ".join(f"{k}({v})" for k, v in r.objectives_selected.most_common(3))
        total_errors += len(r.errors)
        lines.append(
            f"| {r.scenario_label} | {r.encounters_generated}/{r.iterations} | "
            f"{len(r.errors)} | {avg_c} | {avg_xp} | {templates} | {objectives} |"
        )

    lines.append("")

    # Unit tests
    lines.append("## Objective Selection Tests")
    for t in objective_tests:
        lines.append(f"- {t}")
    lines.append("")

    lines.append("## Affix Rolling Tests")
    for t in affix_tests:
        lines.append(f"- {t}")
    lines.append("")

    lines.append("## Reward Generation Tests")
    for t in reward_tests:
        lines.append(f"- {t}")
    lines.append("")

    lines.append("## Feat Definition Tests")
    for t in feat_tests:
        lines.append(f"- {t}")
    lines.append("")

    # Errors
    if total_errors > 0:
        lines.append("## Errors")
        for r in scenario_results:
            for e in r.errors:
                lines.append(f"- [{r.scenario_label}] {e}")
        lines.append("")

    # Summary
    total_gen = sum(r.encounters_generated for r in scenario_results)
    total_iter = sum(r.iterations for r in scenario_results)
    lines.append("## Summary")
    lines.append(f"- **Encounters generated:** {total_gen}/{total_iter}")
    lines.append(f"- **Errors:** {total_errors}")
    has_unit_errors = any("ERROR" in t for t in objective_tests + affix_tests + reward_tests + feat_tests)
    lines.append(f"- **Unit test errors:** {'YES' if has_unit_errors else 'None'}")
    db_note = " (requires populated monster DB)" if total_gen == 0 else ""
    lines.append(f"- **Encounter generation:** {total_gen}/{total_iter}{db_note}")
    lines.append(f"- **Unit tests:** {'PASS' if not has_unit_errors else 'FAIL'}")
    lines.append(f"- **Status:** {'PASS' if not has_unit_errors else 'FAIL'}")

    return "\n".join(lines)


async def load_monster_dicts() -> list[dict]:
    """Load all monsters from DB as dicts for the pipeline."""
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


def main():
    parser = argparse.ArgumentParser(description="Encounter simulation test runner")
    parser.add_argument("--iterations", type=int, default=5, help="Iterations per scenario")
    args = parser.parse_args()

    # Load monsters from DB
    print("Loading monsters from database...")
    monster_dicts = asyncio.run(load_monster_dicts())
    print(f"Loaded {len(monster_dicts)} monsters")

    print(f"Running {len(SCENARIOS)} scenarios x {args.iterations} iterations...")

    # Run encounter scenarios
    scenario_results = []
    for params in SCENARIOS:
        r = run_encounter_scenario(*params, iterations=args.iterations, available_monsters=monster_dicts)
        scenario_results.append(r)
        status = "OK" if not r.errors else f"{len(r.errors)} errors"
        print(f"  {r.scenario_label}: {r.encounters_generated}/{r.iterations} generated ({status})")

    # Run unit tests
    print("\nRunning unit tests...")
    objective_tests = test_objective_selection()
    affix_tests = test_affix_rolling()
    reward_tests = test_reward_generation()
    feat_tests = test_feat_definitions()

    # Generate report
    report = generate_report(scenario_results, objective_tests, affix_tests, reward_tests, feat_tests)

    output_path = "scripts/encounter_test_report.md"
    with open(output_path, "w") as f:
        f.write(report)

    print(f"\nReport written to {output_path}")
    print(report)

    # Exit with error code only for unit test failures (encounter gen needs DB)
    has_unit_errors = any("ERROR" in t for t in objective_tests + affix_tests + reward_tests + feat_tests)
    sys.exit(1 if has_unit_errors else 0)


if __name__ == "__main__":
    main()
