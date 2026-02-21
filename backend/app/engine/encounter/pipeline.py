"""MVP Encounter Generation Pipeline.

Implements steps 1, 2, and 5 of the 10-step pipeline from the GDD:
1. Compute XP budget
2. Select encounter template
5. Greedy budget fill with creature selection

Full pipeline (Phase 2) adds: constraints, scoring, combos,
party validation, sanity checks, tactical brief.
"""

import random
from dataclasses import dataclass, field

from app.engine.encounter.candidate_pool import (
    build_candidate_pool,
    score_candidate,
)
from app.engine.encounter.environment_selector import select_environment
from app.engine.encounter.selection import (
    EncounterSelection,
    SelectedCreature,
    select_creatures,
)
from app.engine.encounter.templates import TEMPLATES, get_template
from app.engine.encounter.xp_budget import compute_xp_budget, get_cr_range_for_budget
from app.engine.scaling import classify_party_size, get_tier


@dataclass
class EncounterWarning:
    level: str  # "warn" or "reject"
    message: str
    creature_id: str = ""


@dataclass
class EncounterProposal:
    """The final output of the encounter pipeline."""

    creatures: list[SelectedCreature]
    template: str
    xp_budget: int
    adjusted_xp: int
    difficulty_tier: str
    tactical_brief: str
    warnings: list[EncounterWarning] = field(default_factory=list)
    creature_count: int = 0
    environment: str = ""
    environment_name: str = ""
    terrain_features: list[str] = field(default_factory=list)
    map_suggestions: list[str] = field(default_factory=list)
    # Objective (Phase 7A)
    objective_id: str = ""
    objective_name: str = ""
    objective_description: str = ""
    objective_dm_instructions: str = ""
    objective_win_conditions: list[str] = field(default_factory=list)
    objective_special_rules: list[str] = field(default_factory=list)
    objective_bonus_rewards: dict = field(default_factory=dict)
    # Affix-modified stats (Phase 7B)
    active_affixes: list[str] = field(default_factory=list)
    affix_modified_stats: dict = field(default_factory=dict)
    # Director AI notes (Phase 11B)
    difficulty_notes: list[str] = field(default_factory=list)
    base_intensity: float = 0.0
    adjusted_intensity: float = 0.0
    # Encounter theme (Phase 12I)
    theme_id: str = ""
    theme_name: str = ""
    # Danger rating (replaces binary "very deadly" warning)
    danger_rating: str = ""
    # Narrative content (Phase: Dynamic Sourcebook)
    read_aloud_text: str = ""
    encounter_hook: str = ""
    dm_guidance_boxes: list[dict] = field(default_factory=list)
    creature_flavor: list[dict] = field(default_factory=list)
    weakness_tips: list[str] = field(default_factory=list)
    roguelike_reference: dict = field(default_factory=dict)


@dataclass
class PipelineInput:
    """Input parameters for encounter generation."""

    party_level: int
    party_size: int
    difficulty: str = "moderate"  # "low", "moderate", "high"
    floor_number: int = 1
    arena_number: int = 1
    template_name: str | None = None  # None = auto-select
    environment: str | None = None
    exclude_monster_ids: set[str] | None = None
    templates_used: list[str] | None = None  # Already used templates this floor
    party_damage_types: list[str] | None = None  # For exploit scoring
    difficulty_multiplier: float = 1.0  # From campaign settings
    xp_budget_multiplier: float = 1.0  # From campaign balance settings
    early_game_scaling_factor: float = 1.0  # From campaign balance settings
    # Objective selection (Phase 7A)
    objective: str | None = None  # Explicit override; None = auto-select
    used_objectives: list[str] | None = None  # Already used this floor
    is_boss: bool = False
    # Floor affixes (Phase 7B)
    active_affixes: list[str] | None = None  # Active affix IDs for this floor
    # Encounter theme (Phase 12I)
    theme: str | None = None  # Explicit theme override; None = auto-select
    # Floor-level theme (strict — all arenas on this floor use this theme)
    floor_theme: str | None = None
    # Arena arc position within the floor ("opener", "middle", "climax")
    arena_arc_position: str = "middle"
    # Floor biome system (Phase 4)
    biome_constraint: str | None = None  # Restrict environments to this biome
    used_environments: list[str] | None = None  # Environments already used this floor


def generate_encounter(
    inp: PipelineInput,
    available_monsters: list[dict],
) -> EncounterProposal:
    """Run the MVP encounter generation pipeline.

    Args:
        inp: Pipeline input parameters
        available_monsters: List of monster dicts from the database

    Returns:
        EncounterProposal with selected creatures and metadata
    """
    tier = get_tier(inp.party_level)
    party_category = classify_party_size(inp.party_size).value

    # Step 0: Select Environment
    chosen_env = select_environment(
        monster_dicts=available_monsters,
        floor_number=inp.floor_number,
        templates_used=inp.templates_used,
        preference=inp.environment,
        biome_constraint=inp.biome_constraint,
        used_environments=inp.used_environments,
    )
    environment_key = chosen_env.key

    # Step 1: Compute XP Budget
    xp_budget = compute_xp_budget(
        party_level=inp.party_level,
        party_size=inp.party_size,
        difficulty=inp.difficulty,
        floor_number=inp.floor_number,
        arena_number=inp.arena_number,
        tier=tier,
        xp_budget_multiplier=inp.xp_budget_multiplier,
        early_game_scaling_factor=inp.early_game_scaling_factor,
    )
    # Apply DM difficulty multiplier
    xp_budget = int(xp_budget * inp.difficulty_multiplier)

    # Step 2: Select Template
    template_name = inp.template_name
    if not template_name:
        template_name = _select_template(inp.templates_used)

    template = get_template(template_name)

    # Step 3: Build Candidate Pool
    cr_min, cr_max = get_cr_range_for_budget(xp_budget, inp.party_level, inp.party_size)

    candidates = build_candidate_pool(
        monsters=available_monsters,
        cr_min=cr_min,
        cr_max=cr_max,
        environment=environment_key,
        exclude_ids=inp.exclude_monster_ids,
    )

    if not candidates:
        # Fallback: widen CR range
        candidates = build_candidate_pool(
            monsters=available_monsters,
            cr_min=0,
            cr_max=cr_max + 2,
            exclude_ids=inp.exclude_monster_ids,
        )

    # Step 3.5: Resolve encounter theme (Phase 12I)
    # Priority: explicit theme > floor_theme > per-arena auto-select
    theme_def = None
    theme_creature_types: list[str] | None = None
    theme_creature_names: list[str] | None = None
    try:
        from app.data.encounter_themes import get_theme, select_theme_for_environment

        if inp.theme:
            theme_def = get_theme(inp.theme)
        elif inp.floor_theme:
            theme_def = get_theme(inp.floor_theme)
        else:
            theme_def = select_theme_for_environment(environment_key, inp.floor_number)
        if theme_def:
            theme_creature_types = theme_def.creature_types
            theme_creature_names = theme_def.creature_names
    except ImportError:
        pass

    # Step 4: Score candidates
    scored = [
        (
            c,
            score_candidate(
                c,
                template.role_weights,
                inp.party_damage_types,
                theme_creature_types,
                theme_creature_names,
                environment=environment_key,
            ),
        )
        for c in candidates
    ]

    # Step 5: Greedy Selection
    selection = select_creatures(
        candidates=candidates,
        xp_budget=xp_budget,
        template_name=template_name,
        min_creatures=template.min_creatures,
        max_creatures=template.max_creatures,
        preferred_spread=template.preferred_cr_spread,
        party_size_category=party_category,
        scored_candidates=scored,
    )

    # Generate warnings
    warnings = _generate_warnings(selection, inp)

    # Generate tactical brief
    tactical_brief = template.tactical_brief_template

    # Step 6: Select Objective (Phase 7A)
    obj_id = ""
    obj_name = ""
    obj_description = ""
    obj_dm_instructions = ""
    obj_win_conditions: list[str] = []
    obj_special_rules: list[str] = []
    obj_bonus_rewards: dict = {}

    try:
        from app.data.arena_objectives import select_objective

        objective_def = (
            select_objective(
                floor_number=inp.floor_number,
                arena_number=inp.arena_number,
                template=template_name,
                used_objectives=inp.used_objectives,
                is_boss=inp.is_boss,
            )
            if not inp.objective
            else None
        )

        # If explicit objective override, look it up
        if inp.objective:
            from app.data.arena_objectives import get_objective

            objective_def = get_objective(inp.objective)

        if objective_def:
            obj_id = objective_def.id
            obj_name = objective_def.name
            obj_description = objective_def.description
            obj_dm_instructions = objective_def.dm_instructions
            obj_win_conditions = objective_def.win_conditions
            obj_special_rules = objective_def.special_rules
            obj_bonus_rewards = objective_def.bonus_rewards
    except ImportError:
        pass  # arena_objectives not yet created

    # Step 7: Apply Floor Affixes (Phase 7B)
    affix_ids: list[str] = []
    affix_stats: dict = {}

    if inp.active_affixes:
        try:
            from app.data.floor_affixes import get_affix

            affix_ids = list(inp.active_affixes)
            creature_buff_mods: dict = {}
            for affix_id in affix_ids:
                affix_def = get_affix(affix_id)
                if affix_def and affix_def.category == "creature_buff":
                    for k, v in affix_def.modifier.items():
                        creature_buff_mods[k] = creature_buff_mods.get(k, 0) + v
            if creature_buff_mods:
                affix_stats = {"creature_buffs": creature_buff_mods}
        except ImportError:
            pass  # floor_affixes not yet created

    # Compute danger rating (replaces binary "very deadly" warning)
    danger_rating = _compute_danger_rating(
        selection.adjusted_xp,
        inp.party_size,
        inp.party_level,
    )

    return EncounterProposal(
        creatures=selection.creatures,
        template=template_name,
        xp_budget=xp_budget,
        adjusted_xp=selection.adjusted_xp,
        difficulty_tier=inp.difficulty,
        tactical_brief=tactical_brief,
        warnings=warnings,
        creature_count=selection.creature_count,
        environment=chosen_env.key,
        environment_name=chosen_env.name,
        terrain_features=chosen_env.terrain_features,
        map_suggestions=chosen_env.map_suggestions,
        objective_id=obj_id,
        objective_name=obj_name,
        objective_description=obj_description,
        objective_dm_instructions=obj_dm_instructions,
        objective_win_conditions=obj_win_conditions,
        objective_special_rules=obj_special_rules,
        objective_bonus_rewards=obj_bonus_rewards,
        active_affixes=affix_ids,
        affix_modified_stats=affix_stats,
        theme_id=theme_def.id if theme_def else "",
        theme_name=theme_def.name if theme_def else "",
        danger_rating=danger_rating,
    )


def _select_template(templates_used: list[str] | None) -> str:
    """Select a template, preferring ones not recently used."""
    all_templates = list(TEMPLATES.keys())

    if not templates_used:
        return random.choice(all_templates)

    # Prefer templates not yet used this floor
    unused = [t for t in all_templates if t not in templates_used]
    if unused:
        return random.choice(unused)

    return random.choice(all_templates)


def _compute_danger_rating(
    adjusted_xp: int,
    party_size: int,
    party_level: int,
) -> str:
    """Compute a 4-tier danger label based on XP ratio vs DMG thresholds.

    Uses actual 2024 DMG thresholds as baseline rather than a flat formula.
    Roguelike encounters are *meant* to be dangerous, so the tiers communicate
    relative threat level rather than a simple pass/fail.
    """
    from app.data.xp_thresholds import XP_THRESHOLDS

    thresholds = XP_THRESHOLDS.get(party_level, XP_THRESHOLDS[1])
    moderate_total = thresholds["moderate"] * party_size
    high_total = thresholds["high"] * party_size

    if moderate_total <= 0:
        return "Dangerous"

    # Compare adjusted XP against the moderate and high thresholds
    if adjusted_xp <= moderate_total * 0.8:
        return "Challenging"
    elif adjusted_xp <= moderate_total * 1.3:
        return "Dangerous"
    elif adjusted_xp <= high_total * 1.2:
        return "Brutal"
    else:
        return "Lethal"


def _generate_warnings(
    selection: EncounterSelection,
    inp: PipelineInput,
) -> list[EncounterWarning]:
    """Generate warnings about potential encounter issues."""
    warnings = []

    if selection.creature_count == 0:
        warnings.append(
            EncounterWarning(
                level="reject",
                message="No creatures could be selected for this encounter.",
            )
        )
        return warnings

    # Warn about specific threat flags
    for creature in selection.creatures:
        # Placeholder for per-creature threat analysis
        pass

    return warnings
