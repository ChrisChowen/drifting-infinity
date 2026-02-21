#!/usr/bin/env python3
"""
Drifting Infinity — Multi-Run Simulation (Meta-Progression)

Simulates 3 consecutive runs across multiple seeds to validate the
roguelike meta-progression system. Between runs:
  - Essence is earned and talents are unlocked
  - PPC decays toward 1.0
  - Characters reset to level 1 (gacha items persist)
  - Secret events and lore beats are tracked

The combat model applies a "roguelike danger factor" — the Armillary is
significantly more dangerous on a first run (no meta-talents). Enemy damage
is amplified, and without auto-stabilize/extra lives/phoenix, the party
faces a high TPK risk on higher floors. Meta-talents progressively reduce
this danger, creating the success-rate curve:
  - Run 1 (no upgrades):  ~15-25% success rate, ~50-200 Essence
  - Run 2 (2-3 talents):  ~45-60% success rate
  - Run 3 (5-6 talents):  ~65-80% success rate

Multi-seed: runs 20 seeds per configuration to get statistical rates.
"""

import asyncio
import random
import sys
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path

# ── Ensure backend is importable ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the single-run simulation
from scripts.full_run_simulation import (
    SimCharacter, create_standard_party, simulate_combat,
    apply_momentum_recovery, apply_short_rest, apply_long_rest,
    FloorResult, RunResult, CombatResult,
    load_monster_dicts, generate_report,
)

# Engine modules
from app.engine.encounter.pipeline import generate_encounter, PipelineInput
from app.engine.scaling import get_tier, get_scaling_params
from app.engine.leveling import (
    compute_arena_xp_award, check_level_up,
    compute_power_xp_bonus,
)
from app.engine.difficulty.intensity_curve import compute_intensity_curve
from app.engine.difficulty.target_computer import compute_difficulty_target
from app.engine.difficulty.party_power import (
    compute_floor_ppc_adjustment, compute_run_end_ppc_adjustment,
)
from app.engine.economy.gold import compute_arena_gold, compute_milestone_gold
from app.engine.economy.shards import compute_floor_clear_shards, compute_achievement_shards, SHARDS_PER_PULL
from app.engine.economy.shop import generate_shop_inventory, compute_item_price
from app.engine.armillary.roller import roll_armillary_effect
from app.engine.armillary.weight_adjuster import adjust_weights
from app.engine.combat.weakness_exploit import WeaknessExploitState, trigger_exploit, new_round
from app.engine.combat.rest import rest_schedule_for_floor
from app.engine.combat.death import compute_final_stand_dc
from app.engine.gacha.pull import determine_rarity
from app.engine.gacha.pity import update_pity_counters
from app.engine.gacha.banners import get_banner, select_item_from_banner

# Meta-progression modules
from app.engine.meta.talents import get_active_effects, unlock_talent, can_unlock, TALENT_TREE
from app.engine.meta.essence import compute_run_essence
from app.engine.meta.achievements import check_achievements
from app.engine.meta.lives import (
    compute_starting_lives, process_character_death, process_tpk, add_life, MAX_LIVES,
)
from app.engine.meta.run_reset import decay_ppc_between_runs

# Data modules
from app.data.secret_events import check_secret_event_triggers, roll_collector_spawn
from app.data.social_encounters import should_place_social_encounter, select_social_encounter, compute_social_dc
from app.data.lore_beats import get_lore_beats_for_floor


# ══════════════════════════════════════════════════════════════════════════
# Enhanced combat model — roguelike danger factor
# ══════════════════════════════════════════════════════════════════════════

def simulate_combat_meta(
    party: list[SimCharacter],
    creatures: list[dict],
    floor_number: int,
    arena_number: int,
    ppc: float = 1.0,
    gacha_items: int = 0,
    meta_effects: dict | None = None,
) -> CombatResult:
    """Simulate combat with roguelike danger factor + meta-talent effects.

    Differences from base simulate_combat:
    - Enemy damage is amplified by a floor-scaling danger factor
    - Danger factor is reduced by meta-talents (insight branch previewing
      means party is better prepared, reducing effective damage taken)
    - Auto-stabilize (resilience_2) gives a free stabilize on first down
    - Final Stand saves improved by resilience_4
    """
    meta = meta_effects or {}

    # Danger factor: scales up on higher floors.
    # Without meta-talents, floors 10+ become dangerous.
    # Insight talents reduce effective danger (party is better prepared).
    # Tuned so ~20% of Run 1 (no talents) survive, ~55% Run 2, ~75% Run 3.
    base_danger = 1.0 + max(0, floor_number - 6) * 0.033  # 1.0 at F1-6, 1.46 at F20
    insight_mitigation = 0.0
    if meta.get("preview_difficulty"):
        insight_mitigation += 0.04   # Know what's coming
    if meta.get("preview_vulnerability"):
        insight_mitigation += 0.04   # Exploit weaknesses better
    if meta.get("preview_armillary_effect"):
        insight_mitigation += 0.04   # Avoid worst effects
    if meta.get("choose_template"):
        insight_mitigation += 0.06   # Pick favorable encounters

    danger_factor = max(1.0, base_danger - insight_mitigation)

    # Auto-stabilize: first time each character goes down, they auto-stabilize
    auto_stab_available = {}
    if meta.get("auto_stabilize"):
        for c in party:
            auto_stab_available[c.name] = True

    # Final stand improvement: +5 to save if resilience_4
    final_stand_bonus = 3 if meta.get("final_stand_saves") else 0

    living_party = [c for c in party if not c.is_dead]
    if not living_party:
        return CombatResult(
            rounds=0, party_survived=False,
            damage_taken_total=0, damage_dealt_total=0,
            weakness_exploits=0, chain_bonuses=0,
            characters_downed=0, final_stand_checks=0, final_stand_deaths=0,
        )

    gacha_attack_bonus = gacha_items // 3
    gacha_damage_bonus = (gacha_items // 3) * 2

    enemies = []
    for creature in creatures:
        for _ in range(creature["count"]):
            enemies.append({
                "name": creature["name"],
                "hp": creature["hp"],
                "max_hp": creature["hp"],
                "ac": creature["ac"],
                "cr": creature["cr"],
                "xp": creature["xp"],
                "tactical_role": creature["tactical_role"],
                "vulnerabilities": creature.get("vulnerabilities", []),
                "alive": True,
            })

    total_dmg_taken = 0
    total_dmg_dealt = 0
    weakness_exploits = 0
    chain_bonuses = 0
    characters_downed = 0
    final_stand_checks = 0
    final_stand_deaths = 0
    rounds_on_final_stand = {}
    armillary_events = []

    we_state = WeaknessExploitState()
    party_level = living_party[0].level

    avg_hp = sum(c.hp_pct() for c in living_party) / len(living_party)
    arm_weights = adjust_weights(
        base_weights={"hostile": 40, "beneficial": 20, "environmental": 25, "wild": 15},
        average_hp_percentage=avg_hp,
        any_dead=any(c.is_dead for c in party),
        cumulative_stress=max(0, 1.0 - avg_hp),
        arena_number=arena_number,
        floor_number=floor_number,
        party_power_coefficient=ppc,
    )

    max_rounds = 20
    for round_num in range(1, max_rounds + 1):
        # Armillary event
        if round_num >= 2 and round_num % 2 == 0:
            try:
                arm_result = roll_armillary_effect(
                    round_number=round_num,
                    category_weights=arm_weights,
                )
                armillary_events.append({
                    "round": round_num,
                    "key": arm_result.effect.key,
                    "category": arm_result.effect.category,
                    "severity": arm_result.effect.severity,
                })
                if arm_result.effect.category == "hostile":
                    dmg = int((arm_result.effect.severity * 3 + party_level) * danger_factor)
                    target = random.choice(living_party)
                    target.current_hp -= dmg
                    total_dmg_taken += dmg
                elif arm_result.effect.category == "beneficial":
                    heal = arm_result.effect.severity * 2 + party_level
                    target = min(living_party, key=lambda c: c.hp_pct())
                    target.current_hp = min(target.max_hp, target.current_hp + heal)
            except Exception:
                pass

        we_state = new_round(we_state)

        # Party attacks (same as base)
        living_enemies = [e for e in enemies if e["alive"]]
        if not living_enemies:
            break

        for char in living_party:
            if char.is_dead or char.current_hp <= 0:
                continue
            target = random.choice(living_enemies)
            roll = random.randint(1, 20) + char.attack_bonus + gacha_attack_bonus
            if roll >= target["ac"]:
                damage = max(1, char.avg_damage + gacha_damage_bonus + random.randint(-3, 3))
                for dmg_type in char.damage_types:
                    if dmg_type in target.get("vulnerabilities", []):
                        we_state, trig = trigger_exploit(
                            we_state, char.name, target["name"],
                            "vulnerability", dmg_type,
                        )
                        if trig:
                            weakness_exploits += 1
                            damage = int(damage * 1.5)
                        if we_state.chain_bonus_active:
                            chain_bonuses += 1
                            damage += we_state.chain_bonus_damage
                        break
                target["hp"] -= damage
                total_dmg_dealt += damage
                if target["hp"] <= 0:
                    target["alive"] = False
                    living_enemies = [e for e in enemies if e["alive"]]
                    if not living_enemies:
                        break

        if not living_enemies:
            break

        # Enemy attacks — AMPLIFIED by danger factor
        for enemy in living_enemies:
            if not enemy["alive"]:
                continue
            valid_targets = [c for c in living_party if not c.is_dead and c.current_hp > 0]
            if not valid_targets:
                break
            target_char = random.choice(valid_targets)

            enemy_dmg = max(1, int((enemy["cr"] * 2.5 + 2) * danger_factor) + random.randint(-2, 2))
            roll = random.randint(1, 20) + int(enemy["cr"] * 0.6 + 3)
            if roll >= target_char.ac:
                target_char.current_hp -= enemy_dmg
                total_dmg_taken += enemy_dmg

                if target_char.current_hp <= 0 and not target_char.is_dead:
                    characters_downed += 1

                    # Auto-stabilize check (meta talent)
                    if auto_stab_available.get(target_char.name, False):
                        auto_stab_available[target_char.name] = False
                        target_char.current_hp = 1
                        continue  # Saved by auto-stabilize

                    if target_char.name not in rounds_on_final_stand:
                        rounds_on_final_stand[target_char.name] = 0
                    rounds_on_final_stand[target_char.name] += 1

                    dc = compute_final_stand_dc(rounds_on_final_stand[target_char.name])
                    con_roll = random.randint(1, 20) + target_char.con_save_bonus + final_stand_bonus
                    final_stand_checks += 1

                    if con_roll >= dc:
                        target_char.current_hp = 1
                    else:
                        target_char.is_dead = True
                        target_char.deaths += 1
                        final_stand_deaths += 1

        # Cleric healing
        healers = [c for c in living_party if c.char_class == "Cleric" and not c.is_dead and c.current_hp > 0 and c.spell_slots_used < c.spell_slots_max]
        for healer in healers:
            wounded = [c for c in living_party if not c.is_dead and c.current_hp > 0 and c.hp_pct() < 0.4]
            if wounded:
                target_heal = min(wounded, key=lambda c: c.hp_pct())
                heal_amount = max(4, healer.level + random.randint(1, 8))
                target_heal.current_hp = min(target_heal.max_hp, target_heal.current_hp + heal_amount)
                healer.spell_slots_used += 1

        alive_count = sum(1 for c in living_party if not c.is_dead and c.current_hp > 0)
        if alive_count == 0:
            return CombatResult(
                rounds=round_num, party_survived=False,
                damage_taken_total=total_dmg_taken, damage_dealt_total=total_dmg_dealt,
                weakness_exploits=weakness_exploits, chain_bonuses=chain_bonuses,
                characters_downed=characters_downed,
                final_stand_checks=final_stand_checks, final_stand_deaths=final_stand_deaths,
                armillary_events=armillary_events,
            )

    return CombatResult(
        rounds=min(round_num, max_rounds), party_survived=True,
        damage_taken_total=total_dmg_taken, damage_dealt_total=total_dmg_dealt,
        weakness_exploits=weakness_exploits, chain_bonuses=chain_bonuses,
        characters_downed=characters_downed,
        final_stand_checks=final_stand_checks, final_stand_deaths=final_stand_deaths,
        armillary_events=armillary_events,
    )


# ══════════════════════════════════════════════════════════════════════════
# Campaign meta-state
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class CampaignState:
    """Persistent state between runs."""
    essence_balance: int = 0
    essence_lifetime: int = 0
    unlocked_talents: list = field(default_factory=list)
    achievements: list = field(default_factory=list)
    total_runs_completed: int = 0
    total_runs_won: int = 0
    highest_floor_reached: int = 0
    total_floors_cleared: int = 0
    total_deaths_all_runs: int = 0
    ppc: float = 1.0
    gacha_items_count: int = 0
    owned_gacha_ids: set = field(default_factory=set)
    lore_fragments_found: list = field(default_factory=list)
    secret_floors_discovered: list = field(default_factory=list)
    total_social_successes: int = 0


@dataclass
class MultiRunResult:
    """Results across all runs in the simulation."""
    runs: list = field(default_factory=list)
    campaign_state_snapshots: list = field(default_factory=list)


# ══════════════════════════════════════════════════════════════════════════
# Single run with meta-progression
# ══════════════════════════════════════════════════════════════════════════

async def simulate_run_with_meta(
    run_number: int,
    campaign: CampaignState,
    monster_dicts: list[dict],
    seed: int = 42,
) -> tuple[RunResult, dict]:
    """Simulate a single run with meta-progression effects applied.

    Returns:
        Tuple of (RunResult, run_stats_dict for achievement checking)
    """
    random.seed(seed + run_number * 1000)

    # Compute meta effects for this run
    meta_effects = get_active_effects(campaign.unlocked_talents)
    starting_lives = compute_starting_lives(campaign.unlocked_talents)

    # Create fresh party (level 1 each run)
    party = create_standard_party()
    scaling = get_scaling_params(len(party))

    ppc = campaign.ppc
    total_gold = 0
    total_shards = 0
    gold_spent = 0
    lives_remaining = starting_lives
    phoenix_used = False
    run_result = RunResult(floors=[])

    # Gacha state (pity resets each run, but owned items persist)
    pity_state = {
        "pulls_since_rare": 0,
        "pulls_since_very_rare": 0,
        "pulls_since_legendary": 0,
        "total_pulls": 0,
    }
    gacha_items_count = campaign.gacha_items_count
    owned_gacha_ids = set(campaign.owned_gacha_ids)
    owned_investment_ids: set[str] = set()

    # Apply meta fortune effects
    shop_discount = meta_effects.get("shop_discount_pct", 0) / 100.0
    gold_bonus_pct = meta_effects.get("gold_bonus_pct", 0) / 100.0
    bonus_shards_per_floor = meta_effects.get("bonus_shards_per_floor", 0)
    pity_head_start = meta_effects.get("pity_head_start", 0)
    pity_state["pulls_since_rare"] = pity_head_start
    pity_state["pulls_since_very_rare"] = pity_head_start
    pity_state["pulls_since_legendary"] = pity_head_start

    # Run tracking
    total_deaths = 0
    boss_kills = 0
    templates_used_all: list[str] = []
    secret_events: list[str] = []
    lore_beats_fired: list[str] = []
    social_encounters_this_run: list[str] = []
    social_successes = 0
    had_deathless_floor = False
    collector_killed = False
    first_boss_killed = False

    max_floors = 20

    for floor_num in range(1, max_floors + 1):
        party_level = party[0].level
        tier = get_tier(party_level)
        total_arenas = min(scaling.max_arenas_per_floor, 3 + (tier - 1))
        is_calibration = floor_num <= 2
        is_boss_floor = (floor_num == 20)

        # Check for secret floor events at transition
        secret_event = check_secret_event_triggers(
            floor_number=floor_num,
            arena_number=0,
            run_stats={"total_deaths": total_deaths, "floors_completed": floor_num - 1},
            campaign_runs_completed=campaign.total_runs_completed,
            trigger_type="floor_transition",
        )
        if secret_event:
            secret_events.append(secret_event.id)
            if secret_event.id not in campaign.secret_floors_discovered:
                campaign.secret_floors_discovered.append(secret_event.id)

        # Fire lore beats for floor start
        beats = get_lore_beats_for_floor(
            floor_number=floor_num,
            run_number=run_number,
            trigger="floor_start",
            context={"deaths_this_run": total_deaths},
        )
        for beat in beats:
            lore_beats_fired.append(beat.id)
            if beat.lore_fragment_id and beat.lore_fragment_id not in campaign.lore_fragments_found:
                campaign.lore_fragments_found.append(beat.lore_fragment_id)

        # Rest schedule
        schedule = rest_schedule_for_floor(total_arenas, scaling.short_rests_per_floor)

        floor_result = FloorResult(
            floor_number=floor_num, party_level=party_level, tier=tier,
            arenas_completed=0, total_arenas=total_arenas,
            party_survived=True, gold_earned=0, shards_earned=0,
            xp_earned_per_char=0, level_ups=[], encounters=[], combat_results=[],
            ppc=ppc, recovery_schedule=schedule,
        )

        templates_used = []
        used_objectives = []
        exclude_monster_ids = set()
        floor_gold = 0
        floor_xp_per_char = 0
        deaths_this_floor = 0
        social_placed_this_floor = False

        leveling_speed = compute_power_xp_bonus(
            gacha_items_owned=gacha_items_count,
            floors_completed=floor_num - 1,
        )

        # --- Between-floor difficulty target (computed ONCE per floor) ---
        prev_floor = run_result.floors[-1] if run_result.floors else None
        prev_hp = prev_floor.hp_at_end if prev_floor else 1.0
        prev_deaths = prev_floor.deaths_this_floor if prev_floor else 0
        prev_tpk = not prev_floor.party_survived if prev_floor else False
        prev_assessment = (
            "healthy" if prev_hp > 0.6
            else ("strained" if prev_hp > 0.3 else "critical")
        )
        floor_base_intensity = compute_intensity_curve(
            arena_number=1, total_arenas=total_arenas,
            floor_number=floor_num, party_power_coefficient=ppc,
            rest_schedule=schedule,
        )
        floor_diff_target = compute_difficulty_target(
            base_intensity=floor_base_intensity.intensity,
            previous_floor_avg_hp=prev_hp,
            previous_floor_deaths=prev_deaths,
            previous_floor_tpk=prev_tpk,
            party_power_coefficient=ppc,
            dm_assessment=prev_assessment,
        )

        for arena_num in range(1, total_arenas + 1):
            # --- Check for social encounter ---
            if should_place_social_encounter(
                floor_number=floor_num,
                arena_number=arena_num,
                total_arenas=total_arenas,
                is_boss_floor=is_boss_floor,
                social_placed_this_floor=social_placed_this_floor,
            ):
                social_enc = select_social_encounter(floor_num, social_encounters_this_run)
                social_encounters_this_run.append(social_enc.id)
                social_placed_this_floor = True

                # Simulate social checks (average skill bonus = level // 2 + 2)
                skill_bonus = party_level // 2 + 2
                successes = 0
                for sc in social_enc.skill_checks:
                    dc = compute_social_dc(sc.dc_base, party_level, floor_num)
                    roll = random.randint(1, 20) + skill_bonus
                    if roll >= dc:
                        successes += 1

                overall_success = successes >= (len(social_enc.skill_checks) + 1) // 2
                if overall_success:
                    social_successes += 1
                    floor_gold += social_enc.success_rewards.get("gold_bonus", 0)
                    if social_enc.lore_fragment_id and social_enc.lore_fragment_id not in campaign.lore_fragments_found:
                        campaign.lore_fragments_found.append(social_enc.lore_fragment_id)

                enc_info = {
                    "arena": arena_num,
                    "template": "social",
                    "xp_budget": 0,
                    "raw_xp": 0,
                    "adjusted_xp": 0,
                    "difficulty": "social",
                    "intensity": 0,
                    "phase": "social",
                    "environment": "",
                    "objective": social_enc.name,
                    "theme": "",
                    "creature_count": 0,
                    "creatures": [],
                    "terrain": [],
                    "tactical_brief": social_enc.dm_prompt[:150],
                    "warnings": [],
                    "is_boss": False,
                    "is_social": True,
                    "social_success": overall_success,
                }
                floor_result.encounters.append(enc_info)
                floor_result.arenas_completed = arena_num
                continue

            # --- Standard combat encounter ---
            intensity = compute_intensity_curve(
                arena_num, total_arenas, floor_num,
                party_power_coefficient=ppc,
                rest_schedule=schedule,
            )

            living = [c for c in party if not c.is_dead and not getattr(c, '_permanently_dead', False)]
            if not living:
                floor_result.party_survived = False
                break

            # Use floor-level difficulty target with arena pacing
            diff_target = floor_diff_target

            party_damage_types = list(set(dt for c in living for dt in c.damage_types))
            is_boss = (arena_num == total_arenas and floor_num % 4 == 0)

            inp = PipelineInput(
                party_level=party_level,
                party_size=len(living),
                difficulty=diff_target.difficulty,
                floor_number=floor_num,
                arena_number=arena_num,
                templates_used=templates_used,
                party_damage_types=party_damage_types,
                difficulty_multiplier=diff_target.xp_multiplier,
                used_objectives=used_objectives,
                is_boss=is_boss,
                exclude_monster_ids=exclude_monster_ids,
            )

            try:
                proposal = generate_encounter(inp, monster_dicts)
            except Exception as e:
                floor_result.difficulty_notes.append(f"Arena {arena_num}: Encounter generation failed: {e}")
                continue

            templates_used.append(proposal.template)
            templates_used_all.append(proposal.template)
            if proposal.objective_id:
                used_objectives.append(proposal.objective_id)

            for creature in proposal.creatures:
                exclude_monster_ids.add(creature.monster_id)

            # Check for The Collector spawn
            collector_spawned = roll_collector_spawn(arena_num, floor_num)

            enc_info = {
                "arena": arena_num,
                "template": proposal.template,
                "xp_budget": proposal.xp_budget,
                "raw_xp": proposal.adjusted_xp,
                "adjusted_xp": proposal.adjusted_xp,
                "difficulty": diff_target.difficulty,
                "intensity": intensity.intensity,
                "phase": intensity.phase.value,
                "environment": proposal.environment_name,
                "objective": proposal.objective_name,
                "theme": proposal.theme_name,
                "creature_count": proposal.creature_count,
                "creatures": [
                    {"name": c.name, "cr": c.cr, "hp": c.hp, "ac": c.ac, "count": c.count,
                     "tactical_role": c.tactical_role, "xp": c.xp, "vulnerabilities": []}
                    for c in proposal.creatures
                ],
                "terrain": proposal.terrain_features[:3],
                "tactical_brief": proposal.tactical_brief[:150],
                "warnings": [w.message for w in proposal.warnings],
                "is_boss": is_boss,
                "collector_spawned": collector_spawned,
            }
            floor_result.encounters.append(enc_info)

            # Build creature dicts
            creature_dicts = []
            for c in proposal.creatures:
                vulns = []
                for md in monster_dicts:
                    if md["id"] == c.monster_id:
                        vulns = md.get("vulnerabilities", [])
                        break
                creature_dicts.append({
                    "name": c.name, "cr": c.cr, "hp": c.hp,
                    "ac": c.ac, "count": c.count,
                    "tactical_role": c.tactical_role, "xp": c.xp,
                    "vulnerabilities": vulns, "weak_saves": [],
                })

            # Simulate combat (with meta-talent effects)
            combat = simulate_combat_meta(
                party, creature_dicts, floor_num, arena_num,
                ppc=ppc, gacha_items=gacha_items_count,
                meta_effects=meta_effects,
            )
            floor_result.combat_results.append(combat)

            if not combat.party_survived:
                # TPK check
                deaths_this_floor += combat.final_stand_deaths
                total_deaths += combat.final_stand_deaths

                tpk_result = process_tpk(lives_remaining, campaign.unlocked_talents, phoenix_used)

                if tpk_result.saved_by_phoenix:
                    # Phoenix Protocol saves the run
                    phoenix_used = True
                    lives_remaining = tpk_result.lives_remaining
                    for c in party:
                        c.is_dead = False
                        c.current_hp = 1
                    floor_result.difficulty_notes.append("Phoenix Protocol activated! TPK averted.")
                else:
                    # Run over
                    floor_result.party_survived = False
                    floor_result.arenas_completed = arena_num
                    break
            else:
                floor_result.arenas_completed = arena_num
                deaths_this_floor += combat.final_stand_deaths
                total_deaths += combat.final_stand_deaths

                # Process NEW deaths this arena (lives cost)
                for c in party:
                    if c.is_dead and not getattr(c, '_death_processed_this_floor', False):
                        death_result = process_character_death(lives_remaining, c.deaths)
                        lives_remaining = death_result.lives_remaining
                        c._death_processed_this_floor = True
                        if death_result.permanently_dead:
                            c._permanently_dead = True

                if is_boss and combat.party_survived:
                    boss_kills += 1
                    if not first_boss_killed:
                        first_boss_killed = True

                # Collector killed check (simplified: 60% chance if spawned and party survived)
                if collector_spawned and combat.party_survived and random.random() < 0.6:
                    collector_killed = True
                    floor_gold += 500 * party_level  # Collector loot

                # XP award
                raw_xp = sum(c.xp * c.count for c in proposal.creatures)
                xp_award = compute_arena_xp_award(raw_xp, len([c for c in party if not c.is_dead]), leveling_speed)
                floor_xp_per_char += xp_award
                for c in party:
                    if not c.is_dead:
                        c.xp += xp_award

                # Gold award (with meta bonus)
                arena_gold = compute_arena_gold(arena_num, party_level, diff_target.difficulty)
                arena_gold = int(arena_gold * (1.0 + gold_bonus_pct))
                floor_gold += arena_gold


            # Between-arena recovery
            if arena_num < total_arenas and floor_result.party_survived:
                gap_idx = arena_num - 1
                if gap_idx < len(schedule):
                    if schedule[gap_idx] == "short_rest":
                        apply_short_rest(party)
                    else:
                        apply_momentum_recovery(party)
                else:
                    apply_momentum_recovery(party)

        # --- Floor completion ---
        floor_result.deaths_this_floor = deaths_this_floor
        if deaths_this_floor == 0:
            had_deathless_floor = True

        if floor_result.party_survived:
            floor_gold += compute_milestone_gold(floor_num, party_level)
            floor_gold = int(floor_gold * (1.0 + gold_bonus_pct))

            floor_shards = compute_floor_clear_shards(floor_num)
            floor_shards += bonus_shards_per_floor
            floor_shards += compute_achievement_shards(
                first_boss_kill=(boss_kills == 1 and first_boss_killed),
                no_deaths_this_floor=(deaths_this_floor == 0),
                full_clear=(floor_result.arenas_completed == total_arenas),
            )
            floor_result.shards_earned = floor_shards

            # Update campaign high floor
            if floor_num > campaign.highest_floor_reached:
                campaign.highest_floor_reached = floor_num
            campaign.total_floors_cleared += 1
        else:
            floor_result.shards_earned = 0

        floor_result.gold_earned = floor_gold
        total_gold += floor_result.gold_earned
        total_shards += floor_result.shards_earned
        floor_result.xp_earned_per_char = floor_xp_per_char

        # Level-up check
        for c in party:
            if not c.is_dead and check_level_up(c.level, c.xp):
                old_level = c.level
                c.level_up()
                floor_result.level_ups.append(f"{c.name} ({c.char_class}): {old_level} → {c.level}")

        # End-of-floor HP + PPC update (between-floor calibration)
        living_at_end = [c for c in party if not c.is_dead]
        avg_hp_end = sum(c.hp_pct() for c in living_at_end) / max(1, len(living_at_end)) if living_at_end else 0.0
        floor_result.hp_at_end = avg_hp_end

        dm_floor_assessment = (
            "healthy" if avg_hp_end > 0.6
            else ("strained" if avg_hp_end > 0.3 else "critical")
        )
        if not floor_result.party_survived:
            dm_floor_assessment = "dire"

        ppc = compute_floor_ppc_adjustment(
            current_ppc=ppc,
            floor_cleared=floor_result.party_survived,
            average_hp_at_floor_end=avg_hp_end,
            deaths_on_floor=deaths_this_floor,
            dm_assessment=dm_floor_assessment,
            is_calibration=is_calibration,
        )
        floor_result.ppc = ppc

        # Shop (simplified)
        available_gold = total_gold - gold_spent
        if available_gold > 100 and floor_result.party_survived:
            shop = generate_shop_inventory(
                party_level=party_level, floor_number=floor_num,
                owned_investment_ids=owned_investment_ids, discount=shop_discount,
            )
            affordable = [i for i in shop.items if compute_item_price(i, shop.discount) <= available_gold]
            if affordable:
                priority = {"investment": 0, "party_buff": 1, "individual": 2, "consumable": 3}
                affordable.sort(key=lambda i: (priority.get(i.category.value, 4), -i.base_price))
                bought = affordable[0]
                price = compute_item_price(bought, shop.discount)
                gold_spent += price
                floor_result.shop_purchases.append(f"{bought.name} ({price}g)")
                if bought.category.value == "investment":
                    owned_investment_ids.add(bought.id)

        # Gacha pull
        available_shards = total_shards - sum(SHARDS_PER_PULL for g in run_result.gacha_results)
        if available_shards >= SHARDS_PER_PULL:
            pull_result = determine_rarity(
                pulls_since_rare=pity_state["pulls_since_rare"],
                pulls_since_very_rare=pity_state["pulls_since_very_rare"],
                pulls_since_legendary=pity_state["pulls_since_legendary"],
                floor_number=floor_num,
            )
            banner_keys = ["the_armory", "the_reliquary", "echoes_of_power"]
            banner = get_banner(banner_keys[floor_num % len(banner_keys)])
            if banner:
                item = select_item_from_banner(
                    banner, pull_result.rarity,
                    owned_item_ids=owned_gacha_ids,
                    party_level=party_level,
                )
                if item:
                    owned_gacha_ids.add(item.id)
                    gacha_items_count += 1
                    run_result.gacha_results.append({
                        "floor": floor_num, "rarity": pull_result.rarity,
                        "item": item.name, "banner": banner.name,
                        "was_pity": pull_result.was_pity,
                    })
            pity_state = update_pity_counters(pity_state, pull_result.rarity)

        # Long rest at floor end (meta-talent: improved_revive_hp)
        for c in party:
            c._death_processed_this_floor = False  # Reset for next floor
            if getattr(c, '_permanently_dead', False):
                continue  # Permanently dead — no revive
            if c.is_dead:
                c.is_dead = False
                if meta_effects.get("improved_revive_hp"):
                    c.current_hp = c.max_hp // 2  # 50% HP revive
                else:
                    c.current_hp = max(1, c.max_hp // 4)  # 25% HP revive (harsher base)
            else:
                c.current_hp = c.max_hp
            c.spell_slots_used = 0

        # Sync levels
        max_level = max(c.level for c in party)
        for c in party:
            while c.level < max_level:
                c.level_up()

        # Fire floor_end lore beats
        beats = get_lore_beats_for_floor(
            floor_number=floor_num,
            run_number=run_number,
            trigger="floor_end",
            context={"deaths_this_run": total_deaths},
        )
        for beat in beats:
            lore_beats_fired.append(beat.id)
            if beat.lore_fragment_id and beat.lore_fragment_id not in campaign.lore_fragments_found:
                campaign.lore_fragments_found.append(beat.lore_fragment_id)

        run_result.floors.append(floor_result)

        if not floor_result.party_survived:
            run_result.tpk_count += 1
            # Run ends on TPK (unless phoenix saved it, which is handled above)
            break

        if party[0].level >= 20:
            break

    # Final stats
    run_result.total_gold = total_gold
    run_result.total_shards = total_shards
    run_result.gold_spent = gold_spent
    run_result.final_level = party[0].level
    run_result.run_completed = party[0].level >= 20 and run_result.tpk_count == 0

    # Build run stats for achievement checking
    run_stats = {
        "floors_completed": len(run_result.floors),
        "total_deaths": total_deaths,
        "run_won": run_result.run_completed,
        "had_deathless_floor": had_deathless_floor,
        "templates_used": templates_used_all,
        "gold_spent": gold_spent,
        "secret_events": secret_events,
        "collector_killed": collector_killed,
        "total_social_successes": campaign.total_social_successes + social_successes,
        "total_runs_completed": campaign.total_runs_completed + 1,
        "total_shards_lifetime": total_shards,
        "total_lore_fragments": len(campaign.lore_fragments_found),
        "tpk_saved": phoenix_used,
        "aethon_defeated": run_result.run_completed,
    }

    # Update campaign persistent state
    campaign.gacha_items_count = gacha_items_count
    campaign.owned_gacha_ids = owned_gacha_ids
    campaign.total_social_successes += social_successes
    campaign.total_deaths_all_runs += total_deaths
    campaign.ppc = ppc

    return run_result, run_stats


# ══════════════════════════════════════════════════════════════════════════
# Talent spending strategy
# ══════════════════════════════════════════════════════════════════════════

def auto_spend_essence(campaign: CampaignState):
    """Automatically spend essence on talents (simulates player choices).

    Strategy: alternate between resilience and insight, then fortune.
    """
    # Priority order: resilience first (survival), then insight, then fortune
    priority = [
        "resilience_1", "insight_1", "resilience_2", "fortune_1",
        "insight_2", "resilience_3", "fortune_2", "insight_3",
        "resilience_4", "fortune_3", "insight_4", "fortune_4",
        "resilience_5", "insight_5", "fortune_5",
    ]

    for talent_id in priority:
        if can_unlock(talent_id, campaign.unlocked_talents, campaign.essence_balance):
            campaign.unlocked_talents, campaign.essence_balance = unlock_talent(
                talent_id, campaign.unlocked_talents, campaign.essence_balance,
            )


# ══════════════════════════════════════════════════════════════════════════
# Multi-run simulation
# ══════════════════════════════════════════════════════════════════════════

async def simulate_3_run_campaign(
    monster_dicts: list[dict],
    base_seed: int = 42,
    verbose: bool = False,
) -> dict:
    """Simulate a 3-run campaign. Returns summary dict.

    The campaign state carries across runs (essence, talents, PPC, etc.)
    just like a real player's campaign would.
    """
    campaign = CampaignState()
    results = []

    for run_num in range(1, 4):
        # Snapshot before
        talents_before = len(campaign.unlocked_talents)
        ppc_before = campaign.ppc

        run_result, run_stats = await simulate_run_with_meta(
            run_number=run_num,
            campaign=campaign,
            monster_dicts=monster_dicts,
            seed=base_seed,
        )

        # Compute essence
        essence_earned = compute_run_essence(
            floors_completed=len(run_result.floors),
            boss_kills=sum(1 for f in run_result.floors for e in f.encounters if e.get("is_boss") and f.party_survived),
            achievements_earned=0,
            run_won=run_result.run_completed,
        )

        new_achievements = check_achievements(run_stats, campaign.achievements)
        for ach_id in new_achievements:
            campaign.achievements.append(ach_id)
            essence_earned += 15

        campaign.essence_balance += essence_earned
        campaign.essence_lifetime += essence_earned
        campaign.total_runs_completed += 1
        if run_result.run_completed:
            campaign.total_runs_won += 1

        campaign.ppc = decay_ppc_between_runs(campaign.ppc)

        results.append({
            "run_number": run_num,
            "won": run_result.run_completed,
            "final_level": run_result.final_level,
            "floors": len(run_result.floors),
            "tpks": run_result.tpk_count,
            "deaths": run_stats["total_deaths"],
            "essence": essence_earned,
            "talents_before": talents_before,
            "ppc_before": ppc_before,
            "achievements": new_achievements,
        })

        if verbose:
            status = "WON" if run_result.run_completed else f"LOST (floor {len(run_result.floors)})"
            print(f"    Run {run_num}: {status} | Lvl {run_result.final_level} | Deaths: {run_stats['total_deaths']} | Talents: {talents_before}")

        # Spend essence between runs
        auto_spend_essence(campaign)

    return {
        "results": results,
        "campaign": campaign,
    }


async def simulate_multi_run_statistical(num_seeds: int = 20, verbose: bool = True):
    """Run the 3-run campaign across many seeds for statistical analysis.

    This is the core validation: we want to see the success-rate curve
    across Run 1 → Run 2 → Run 3 converge to the design targets.
    """
    monster_dicts = await load_monster_dicts()

    print("=" * 70)
    print("  DRIFTING INFINITY — META-PROGRESSION STATISTICAL ANALYSIS")
    print(f"  Simulating 3-run campaigns across {num_seeds} seeds")
    print("  Party: Fighter, Cleric, Rogue, Wizard")
    print("=" * 70)

    # Aggregate stats per run-tier
    run_wins = {1: 0, 2: 0, 3: 0}
    run_floors = {1: [], 2: [], 3: []}
    run_deaths = {1: [], 2: [], 3: []}
    run_levels = {1: [], 2: [], 3: []}
    run_essence = {1: [], 2: [], 3: []}

    # Also track one detailed campaign for the report
    best_campaign = None

    for seed_idx in range(num_seeds):
        base_seed = 100 + seed_idx * 137  # Spread seeds

        if verbose:
            print(f"\n  Seed {seed_idx + 1}/{num_seeds} (base_seed={base_seed}):")

        campaign_result = await simulate_3_run_campaign(
            monster_dicts=monster_dicts,
            base_seed=base_seed,
            verbose=verbose,
        )

        for r in campaign_result["results"]:
            rn = r["run_number"]
            run_wins[rn] += int(r["won"])
            run_floors[rn].append(r["floors"])
            run_deaths[rn].append(r["deaths"])
            run_levels[rn].append(r["final_level"])
            run_essence[rn].append(r["essence"])

        # Keep the first campaign as the detailed example
        if best_campaign is None:
            best_campaign = campaign_result

    # ── Statistical report ────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  STATISTICAL RESULTS")
    print("=" * 70)

    out = StringIO()
    p = lambda *args, **kwargs: print(*args, **kwargs, file=out)

    p("# Drifting Infinity — Multi-Run Meta-Progression Report")
    p()
    p(f"**Seeds:** {num_seeds}")
    p(f"**Campaigns:** {num_seeds} × 3 runs each")
    p()

    p("## Success Rate Curve")
    p()
    p("| Run | Win Rate | Avg Level | Avg Floors | Avg Deaths | Avg Essence | Target |")
    p("|-----|----------|-----------|------------|------------|-------------|--------|")
    targets = {1: "15-25%", 2: "45-60%", 3: "65-80%"}
    for rn in [1, 2, 3]:
        win_rate = run_wins[rn] / num_seeds * 100
        avg_lvl = sum(run_levels[rn]) / len(run_levels[rn])
        avg_floors = sum(run_floors[rn]) / len(run_floors[rn])
        avg_deaths = sum(run_deaths[rn]) / len(run_deaths[rn])
        avg_essence = sum(run_essence[rn]) / len(run_essence[rn])
        p(f"| {rn} | **{win_rate:.0f}%** ({run_wins[rn]}/{num_seeds}) | {avg_lvl:.1f} | {avg_floors:.1f} | {avg_deaths:.1f} | {avg_essence:.0f} | {targets[rn]} |")
    p()

    # Validation verdicts
    p("## Balance Validation")
    p()
    for rn in [1, 2, 3]:
        rate = run_wins[rn] / num_seeds * 100
        if rn == 1:
            if 10 <= rate <= 30:
                verdict = "PASS"
            elif rate < 10:
                verdict = "WARN: Too hard (increase base survival)"
            else:
                verdict = f"WARN: Too easy ({rate:.0f}% > 30%)"
        elif rn == 2:
            if 35 <= rate <= 70:
                verdict = "PASS"
            elif rate < 35:
                verdict = "WARN: Too hard (meta-talents not helping enough)"
            else:
                verdict = f"WARN: Too easy ({rate:.0f}% > 70%)"
        else:
            if 55 <= rate <= 90:
                verdict = "PASS"
            elif rate < 55:
                verdict = "WARN: Too hard (talent tree not impactful enough)"
            else:
                verdict = f"WARN: Too easy ({rate:.0f}% > 90%)"
        p(f"- Run {rn}: {rate:.0f}% win rate — Target: {targets[rn]} — **{verdict}**")
    p()

    # Detailed example campaign
    if best_campaign:
        camp = best_campaign["campaign"]
        p("## Example Campaign (Seed 1)")
        p()
        p(f"**Final Essence:** {camp.essence_balance} (lifetime: {camp.essence_lifetime})")
        p(f"**Talents Unlocked:** {len(camp.unlocked_talents)}")
        p(f"**Achievements:** {len(camp.achievements)}")
        p(f"**Lore Fragments:** {len(camp.lore_fragments_found)}")
        p(f"**Gacha Items:** {camp.gacha_items_count}")
        p()

        p("**Talent Tree Progress:**")
        for talent_id in camp.unlocked_talents:
            from app.engine.meta.talents import get_talent
            t = get_talent(talent_id)
            if t:
                p(f"- [{t.branch}] {t.name} (Tier {t.tier}): {t.description}")
        p()

        p("**Achievements Earned:**")
        for ach_id in camp.achievements:
            from app.engine.meta.achievements import get_achievement
            a = get_achievement(ach_id)
            if a:
                p(f"- {a.name}: {a.description} (+{a.essence_reward} essence)")
        p()

        p(f"**Lore Fragments Found:** {len(camp.lore_fragments_found)}")
        for frag_id in camp.lore_fragments_found[:10]:
            from app.data.lore_fragments import get_lore_fragment
            frag = get_lore_fragment(frag_id)
            if frag:
                p(f"- [{frag.category}] {frag.title}")
        if len(camp.lore_fragments_found) > 10:
            p(f"- ... and {len(camp.lore_fragments_found) - 10} more")
        p()

    report_text = out.getvalue()
    print(report_text)

    output_path = Path(__file__).parent / "multi_run_report.md"
    output_path.write_text(report_text)
    print(f"\nReport saved to: {output_path}")


# ══════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    asyncio.run(simulate_multi_run_statistical(num_seeds=20, verbose=True))
