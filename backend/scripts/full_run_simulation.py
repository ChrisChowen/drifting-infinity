#!/usr/bin/env python3
"""
Drifting Infinity — Full Run Simulation (Levels 1–20)

Simulates the complete DM experience from a party starting at level 1
through approximately 20 floors, exercising every major system:
  - Encounter generation pipeline (XP budgets, templates, creatures)
  - Difficulty Director (intensity curves, party power coefficient)
  - Combat simulation (weakness exploits, momentum, Final Stand)
  - Rest system (momentum, short rests, long rests)
  - Armillary dynamic events (weighted rolling, category adjustment)
  - Economy (gold payouts, milestones, shop, astral shards)
  - Leveling (XP awards, power-based speed bonus, level-up tracking)
  - Rewards & gacha (pulls, pity system, duplicate protection)

Outputs a detailed floor-by-floor report to stdout AND a markdown file.
"""

import asyncio
import random
import sys
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path

# ── Ensure backend is importable ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.data.cr_averages import CR_AVERAGES
from app.data.encounter_themes import select_theme_for_floor
from app.database import async_session
from app.engine.armillary.roller import roll_armillary_effect
from app.engine.armillary.weight_adjuster import adjust_weights
from app.engine.combat.death import compute_final_stand_dc
from app.engine.combat.rest import rest_schedule_for_floor
from app.engine.combat.weakness_exploit import (
    WeaknessExploitState,
    new_round,
    trigger_exploit,
)
from app.engine.difficulty.intensity_curve import compute_intensity_curve
from app.engine.difficulty.party_power import (
    compute_floor_ppc_adjustment,
)
from app.engine.difficulty.target_computer import compute_difficulty_target
from app.engine.economy.gold import (
    compute_arena_gold,
    compute_milestone_gold,
)
from app.engine.economy.shards import (
    SHARDS_PER_PULL,
    compute_achievement_shards,
    compute_floor_clear_shards,
)
from app.engine.economy.shop import compute_item_price, generate_shop_inventory
from app.engine.encounter.environment_selector import select_floor_biome

# Engine modules
from app.engine.encounter.pipeline import PipelineInput, generate_encounter
from app.engine.gacha.banners import get_banner, select_item_from_banner
from app.engine.gacha.pity import update_pity_counters
from app.engine.gacha.pull import determine_rarity
from app.engine.leveling import (
    check_level_up,
    compute_arena_xp_award,
    compute_power_xp_bonus,
)
from app.engine.scaling import get_scaling_params, get_tier
from app.models.monster import Monster

# ══════════════════════════════════════════════════════════════════════════
# Party / Character data structures
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class SimCharacter:
    name: str
    char_class: str
    level: int
    max_hp: int
    current_hp: int
    ac: int
    xp: int = 0
    is_dead: bool = False
    deaths: int = 0
    damage_types: list[str] = field(default_factory=list)
    # Core combat stats
    attack_bonus: int = 5
    avg_damage: int = 7
    con_save_bonus: int = 2
    spell_slots_max: int = 0
    spell_slots_used: int = 0
    # Class features
    attacks_per_round: int = 1
    has_aoe: bool = False
    aoe_damage: int = 0
    aoe_uses: int = 0
    aoe_uses_max: int = 0
    # Per-encounter resources — Fighter
    action_surge_uses: int = 0
    second_wind_uses: int = 0
    # Paladin
    smite_uses: int = 0
    lay_on_hands_pool: int = 0
    # Barbarian
    rage_uses: int = 0
    rage_damage_bonus: int = 0
    is_raging: bool = False
    # Rogue
    sneak_attack_bonus: int = 0
    cunning_action_ac: int = 0
    # Monk
    ki_points: int = 0
    ki_points_max: int = 0
    flurry_attacks: int = 0
    # Bard
    bardic_inspiration_uses: int = 0
    # Druid
    wild_shape_hp: int = 0
    # Cleric
    channel_divinity_uses: int = 0
    # Wizard
    shield_uses: int = 0
    # Sorcerer
    quicken_uses: int = 0
    # Warlock
    hex_damage: int = 0
    # Ranger
    hunters_mark_damage: int = 0
    # Enhancement bonuses from shop purchases
    bonus_hp: int = 0
    bonus_ac: int = 0
    bonus_damage: int = 0
    bonus_attack: int = 0

    def hp_pct(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return max(0.0, self.current_hp / self.max_hp)

    def level_up(self):
        self.level += 1
        hp_gains = {
            "Fighter": 7, "Paladin": 7, "Barbarian": 8,
            "Ranger": 6, "Rogue": 5, "Cleric": 5,
            "Wizard": 4, "Sorcerer": 4, "Warlock": 5,
            "Bard": 5, "Druid": 5, "Monk": 5,
        }
        hp_gain = hp_gains.get(self.char_class, 6) + 2
        self.max_hp += hp_gain
        self.current_hp += hp_gain
        self.xp = 0
        # Proficiency bonus: +2 at 1, +3 at 5, +4 at 9, etc.
        prof = 2 + (self.level - 1) // 4
        # Primary ability mod: starts at +3, +4 at 4, +5 at 8
        ability_mod = min(5, 3 + (self.level // 4))
        self.attack_bonus = prof + ability_mod
        self.con_save_bonus = 2 + (self.level // 4)
        # Scale AC slightly (better gear at tier breakpoints)
        if self.level in (5, 11, 17):
            self.ac += 1
        # Spell slots for full casters
        full_casters = (
            "Cleric", "Wizard", "Druid", "Sorcerer", "Bard",
        )
        if self.char_class in full_casters:
            self.spell_slots_max = max(
                self.spell_slots_max, 2 + self.level,
            )
        elif self.char_class == "Warlock":
            self.spell_slots_max = max(
                self.spell_slots_max, 2 + (self.level // 5),
            )
        elif self.char_class in ("Paladin", "Ranger"):
            self.spell_slots_max = max(
                self.spell_slots_max, max(0, self.level - 1),
            )
        # ── Class-specific features ──────────────────────────
        self._apply_class_features(ability_mod)

    def _apply_class_features(self, ability_mod: int):
        """Set class-specific combat stats based on level."""
        lvl = self.level
        cls = self.char_class

        if cls == "Fighter":
            self.avg_damage = 9 + ability_mod
            if lvl >= 5:
                self.attacks_per_round = 2
            if lvl >= 11:
                self.attacks_per_round = 3
            if lvl >= 20:
                self.attacks_per_round = 4
            self.action_surge_uses = (
                1 if lvl >= 2 else 0
            )
            if lvl >= 17:
                self.action_surge_uses = 2
            self.second_wind_uses = 1

        elif cls == "Paladin":
            self.avg_damage = 8 + ability_mod
            if lvl >= 5:
                self.attacks_per_round = 2
            self.smite_uses = self.spell_slots_max
            self.lay_on_hands_pool = lvl * 5

        elif cls == "Barbarian":
            self.avg_damage = 8 + ability_mod
            if lvl >= 5:
                self.attacks_per_round = 2
            if lvl >= 1:
                self.rage_uses = 2
            if lvl >= 3:
                self.rage_uses = 3
            if lvl >= 6:
                self.rage_uses = 4
            if lvl >= 12:
                self.rage_uses = 5
            if lvl >= 17:
                self.rage_uses = 6
            self.rage_damage_bonus = 2
            if lvl >= 9:
                self.rage_damage_bonus = 3
            if lvl >= 16:
                self.rage_damage_bonus = 4

        elif cls == "Rogue":
            self.avg_damage = 5 + ability_mod
            self.attacks_per_round = 1  # Always 1
            self.sneak_attack_bonus = (
                ((lvl + 1) // 2) * 3
            )
            self.cunning_action_ac = 2

        elif cls == "Cleric":
            self.avg_damage = 5 + ability_mod
            self.attacks_per_round = 1
            if lvl >= 2:
                self.channel_divinity_uses = 1
            if lvl >= 6:
                self.channel_divinity_uses = 2
            if lvl >= 18:
                self.channel_divinity_uses = 3
            if lvl >= 5:
                self.has_aoe = True
                self.aoe_damage = lvl + 8
                self.aoe_uses_max = max(
                    1, self.spell_slots_max // 4,
                )
                self.aoe_uses = self.aoe_uses_max

        elif cls == "Wizard":
            self.avg_damage = 6 + ability_mod
            self.attacks_per_round = 1
            if lvl >= 5:
                self.has_aoe = True
                self.aoe_damage = lvl * 2 + 5
                self.aoe_uses_max = max(
                    1, (self.spell_slots_max - 2) // 3,
                )
                self.aoe_uses = self.aoe_uses_max
            self.shield_uses = lvl // 3

        elif cls == "Sorcerer":
            self.avg_damage = 6 + ability_mod
            self.attacks_per_round = 1
            if lvl >= 5:
                self.has_aoe = True
                self.aoe_damage = lvl * 2 + 5
                self.aoe_uses_max = max(
                    1, (self.spell_slots_max - 2) // 3,
                )
                self.aoe_uses = self.aoe_uses_max
            self.quicken_uses = lvl // 2

        elif cls == "Warlock":
            # Eldritch Blast beam scaling
            beams = 1
            if lvl >= 5:
                beams = 2
            if lvl >= 11:
                beams = 3
            if lvl >= 17:
                beams = 4
            self.attacks_per_round = beams
            self.avg_damage = 8  # Per beam
            self.hex_damage = 3  # Per hit

        elif cls == "Ranger":
            self.avg_damage = 7 + ability_mod
            if lvl >= 5:
                self.attacks_per_round = 2
            self.hunters_mark_damage = 3

        elif cls == "Bard":
            self.avg_damage = 5 + ability_mod
            self.attacks_per_round = 1
            self.bardic_inspiration_uses = max(
                3, 3 + lvl // 4,
            )
            if lvl >= 10:
                self.has_aoe = True
                self.aoe_damage = lvl + 8
                self.aoe_uses_max = max(
                    1, self.spell_slots_max // 4,
                )
                self.aoe_uses = self.aoe_uses_max

        elif cls == "Druid":
            self.avg_damage = 5 + ability_mod
            self.attacks_per_round = 1
            if 2 <= lvl <= 4:
                self.wild_shape_hp = lvl * 4
            if lvl >= 5:
                self.has_aoe = True
                self.aoe_damage = lvl + 4
                self.aoe_uses_max = max(
                    1, self.spell_slots_max // 4,
                )
                self.aoe_uses = self.aoe_uses_max
            if lvl >= 9:
                self.attacks_per_round = 2  # Conjure

        elif cls == "Monk":
            self.avg_damage = 5 + ability_mod
            self.attacks_per_round = 2  # Always 2
            self.ki_points_max = lvl
            self.ki_points = lvl
            self.flurry_attacks = 2

        else:
            # Generic class fallback
            self.avg_damage = 7 + ability_mod
            if lvl >= 5:
                self.attacks_per_round = 2

    def reset_encounter_resources(self):
        """Reset per-encounter resources (not per-rest)."""
        self.is_raging = False


def create_standard_party() -> list[SimCharacter]:
    """Create a classic 4-person party at level 1."""
    return [
        SimCharacter(
            name="Kael", char_class="Fighter", level=1,
            max_hp=12, current_hp=12, ac=16,
            damage_types=["slashing", "piercing"],
            attack_bonus=5, avg_damage=9,
            con_save_bonus=4,
        ),
        SimCharacter(
            name="Liora", char_class="Cleric", level=1,
            max_hp=10, current_hp=10, ac=18,
            damage_types=["radiant", "bludgeoning"],
            attack_bonus=4, avg_damage=6,
            con_save_bonus=2, spell_slots_max=2,
        ),
        SimCharacter(
            name="Zephyr", char_class="Rogue", level=1,
            max_hp=9, current_hp=9, ac=14,
            damage_types=["piercing", "poison"],
            attack_bonus=5, avg_damage=5,
            con_save_bonus=1, sneak_attack_bonus=3,
        ),
        SimCharacter(
            name="Elara", char_class="Wizard", level=1,
            max_hp=8, current_hp=8, ac=12,
            damage_types=["fire", "lightning", "cold"],
            attack_bonus=5, avg_damage=7,
            con_save_bonus=1, spell_slots_max=2,
        ),
    ]


# ══════════════════════════════════════════════════════════════════════════
# Combat simulation
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class CombatResult:
    rounds: int
    party_survived: bool
    damage_taken_total: int
    damage_dealt_total: int
    weakness_exploits: int
    chain_bonuses: int
    characters_downed: int
    final_stand_checks: int
    final_stand_deaths: int
    armillary_events: list[dict] = field(default_factory=list)


def _get_enemy_stats(cr: float) -> dict:
    """Look up DPR, attack bonus, save DC from CR averages."""
    nearest = min(CR_AVERAGES.keys(), key=lambda k: abs(k - cr))
    avg = CR_AVERAGES[nearest]
    return {
        "dpr": avg["dpr"],
        "attack_bonus": int(avg["attack_bonus"]),
        "save_dc": int(avg["save_dc"]),
    }


def _do_attack_roll(
    atk_bonus: int,
    target_ac: int,
    base_damage: int,
) -> tuple[int, bool]:
    """Roll a d20 attack. Returns (damage, was_crit).

    Returns 0 damage on miss. Crits deal 1.75x.
    """
    d20 = random.randint(1, 20)
    is_crit = d20 == 20
    if is_crit:
        return int(base_damage * 1.75), True
    if d20 + atk_bonus >= target_ac:
        return base_damage, False
    return 0, False


def simulate_combat(
    party: list[SimCharacter],
    creatures: list[dict],
    floor_number: int,
    arena_number: int,
    ppc: float = 1.0,
    gacha_items: int = 0,
) -> CombatResult:
    """Simulate a combat encounter with per-class features.

    Models multi-attack, AoE, class resources (smite, rage,
    sneak attack, etc.), and uses CR_AVERAGES for enemy DPR.
    """
    living_party = [c for c in party if not c.is_dead]
    if not living_party:
        return CombatResult(
            rounds=0, party_survived=False,
            damage_taken_total=0, damage_dealt_total=0,
            weakness_exploits=0, chain_bonuses=0,
            characters_downed=0,
            final_stand_checks=0,
            final_stand_deaths=0,
        )

    # Gacha item bonus: +1 to hit and +2 dmg per 3 items
    gacha_atk = gacha_items // 3
    gacha_dmg = (gacha_items // 3) * 2

    # Build enemy list from creature dicts
    enemies: list[dict] = []
    for creature in creatures:
        stats = _get_enemy_stats(creature["cr"])
        num_attacks = 1 if creature["cr"] < 3 else 2
        per_hit = max(1, stats["dpr"] // num_attacks)
        for _ in range(creature["count"]):
            enemies.append({
                "name": creature["name"],
                "hp": creature["hp"],
                "max_hp": creature["hp"],
                "ac": creature["ac"],
                "cr": creature["cr"],
                "xp": creature["xp"],
                "tactical_role": creature["tactical_role"],
                "vulnerabilities": creature.get(
                    "vulnerabilities", [],
                ),
                "weak_saves": creature.get(
                    "weak_saves", [],
                ),
                "alive": True,
                "stunned": False,
                # From CR_AVERAGES
                "dpr": stats["dpr"],
                "attack_bonus": stats["attack_bonus"],
                "save_dc": stats["save_dc"],
                "num_attacks": num_attacks,
                "per_hit_damage": per_hit,
            })

    total_dmg_taken = 0
    total_dmg_dealt = 0
    weakness_exploits = 0
    chain_bonuses = 0
    characters_downed = 0
    final_stand_checks = 0
    final_stand_deaths = 0
    rounds_on_final_stand: dict[str, int] = {}
    armillary_events: list[dict] = []
    # Track once-per-encounter resources
    action_surge_used: dict[str, int] = {}


    we_state = WeaknessExploitState()
    party_level = living_party[0].level

    avg_hp = (
        sum(c.hp_pct() for c in living_party)
        / len(living_party)
    )
    arm_weights = adjust_weights(
        base_weights={
            "hostile": 40, "beneficial": 20,
            "environmental": 25, "wild": 15,
        },
        average_hp_percentage=avg_hp,
        any_dead=any(c.is_dead for c in party),
        cumulative_stress=max(0, 1.0 - avg_hp),
        arena_number=arena_number,
        floor_number=floor_number,
        party_power_coefficient=ppc,
    )

    max_rounds = 20
    for round_num in range(1, max_rounds + 1):
        # --- Armillary event (every other round from R2) ---
        if round_num >= 2 and round_num % 2 == 0:
            try:
                arm_result = roll_armillary_effect(
                    round_number=round_num,
                    category_weights=arm_weights,
                )
                armillary_events.append({
                    "round": round_num,
                    "key": arm_result.effect.key,
                    "name": arm_result.effect.name,
                    "category": arm_result.effect.category,
                    "severity": arm_result.effect.severity,
                    "description": (
                        arm_result.effect.description
                    ),
                })
                if arm_result.effect.category == "hostile":
                    dmg = (
                        arm_result.effect.severity * 3
                        + party_level
                    )
                    tgt = random.choice(living_party)
                    tgt.current_hp -= dmg
                    total_dmg_taken += dmg
                elif (
                    arm_result.effect.category == "beneficial"
                ):
                    heal = (
                        arm_result.effect.severity * 2
                        + party_level
                    )
                    tgt = min(
                        living_party,
                        key=lambda c: c.hp_pct(),
                    )
                    tgt.current_hp = min(
                        tgt.max_hp, tgt.current_hp + heal,
                    )
            except Exception:
                pass

        we_state = new_round(we_state)

        # Clear stun flags from previous round
        for e in enemies:
            e["stunned"] = False

        # ═══ PARTY ATTACK PHASE ═══════════════════════════
        living_enemies = [e for e in enemies if e["alive"]]
        if not living_enemies:
            break

        for char in living_party:
            if char.is_dead or char.current_hp <= 0:
                continue

            living_enemies = [
                e for e in enemies if e["alive"]
            ]
            if not living_enemies:
                break

            atk_bonus = (
                char.attack_bonus + gacha_atk
                + char.bonus_attack
            )
            base_dmg = (
                char.avg_damage + gacha_dmg
                + char.bonus_damage
            )
            cls = char.char_class

            # ── Cleric: heal lowest ally if below 30% ──
            if cls == "Cleric":
                wounded = [
                    c for c in living_party
                    if not c.is_dead
                    and c.current_hp > 0
                    and c.hp_pct() < 0.3
                ]
                if (
                    wounded
                    and char.spell_slots_used
                    < char.spell_slots_max
                ):
                    heal_tgt = min(
                        wounded, key=lambda c: c.hp_pct(),
                    )
                    heal_amt = 6 + random.randint(0, 2)
                    heal_tgt.current_hp = min(
                        heal_tgt.max_hp,
                        heal_tgt.current_hp + heal_amt,
                    )
                    char.spell_slots_used += 1

            # ── AoE check: caster with 3+ enemies ──
            if (
                char.has_aoe
                and char.aoe_uses > 0
                and len(living_enemies) >= 3
            ):
                targets = random.sample(
                    living_enemies,
                    min(3, len(living_enemies)),
                )
                for tgt in targets:
                    dmg = max(
                        1,
                        char.aoe_damage
                        + random.randint(-2, 2),
                    )
                    tgt["hp"] -= dmg
                    total_dmg_dealt += dmg
                    if tgt["hp"] <= 0:
                        tgt["alive"] = False
                char.aoe_uses -= 1
                living_enemies = [
                    e for e in enemies if e["alive"]
                ]
                continue  # AoE replaces attacks

            # ── Barbarian: start raging round 1 ──
            if (
                cls == "Barbarian"
                and not char.is_raging
                and char.rage_uses > 0
            ):
                char.is_raging = True
                char.rage_uses -= 1

            # ── Normal attacks ──
            num_attacks = char.attacks_per_round
            first_hit_done = False

            for _atk_idx in range(num_attacks):
                living_enemies = [
                    e for e in enemies if e["alive"]
                ]
                if not living_enemies:
                    break

                tgt = random.choice(living_enemies)
                hit_dmg = base_dmg + random.randint(-2, 2)

                # Per-hit class bonuses
                if cls == "Barbarian" and char.is_raging:
                    hit_dmg += char.rage_damage_bonus
                if cls == "Warlock":
                    hit_dmg += char.hex_damage
                if cls == "Ranger":
                    hit_dmg += char.hunters_mark_damage

                d20 = random.randint(1, 20)
                is_crit = d20 == 20
                hit = is_crit or (
                    d20 + atk_bonus >= tgt["ac"]
                )

                if hit:
                    dmg = max(1, hit_dmg)
                    if is_crit:
                        dmg = int(dmg * 1.75)

                    # Rogue: sneak attack on first hit
                    if (
                        cls == "Rogue"
                        and not first_hit_done
                    ):
                        dmg += char.sneak_attack_bonus

                    # Paladin: smite on first hit
                    if (
                        cls == "Paladin"
                        and not first_hit_done
                        and char.smite_uses > 0
                    ):
                        dmg += 9
                        char.smite_uses -= 1

                    first_hit_done = True

                    # Weakness exploit check
                    for dmg_type in char.damage_types:
                        vulns = tgt.get(
                            "vulnerabilities", [],
                        )
                        if dmg_type in vulns:
                            we_state, trig = trigger_exploit(
                                we_state,
                                char.name,
                                tgt["name"],
                                "vulnerability",
                                dmg_type,
                            )
                            if trig:
                                weakness_exploits += 1
                                dmg = int(dmg * 1.5)
                            if we_state.chain_bonus_active:
                                chain_bonuses += 1
                                dmg += (
                                    we_state.chain_bonus_damage
                                )
                            break

                    tgt["hp"] -= dmg
                    total_dmg_dealt += dmg

                    if tgt["hp"] <= 0:
                        tgt["alive"] = False

            # ── Monk: Flurry of Blows ──
            if (
                cls == "Monk"
                and char.ki_points > 0
            ):
                char.ki_points -= 1
                for _f in range(char.flurry_attacks):
                    living_enemies = [
                        e for e in enemies if e["alive"]
                    ]
                    if not living_enemies:
                        break
                    tgt = random.choice(living_enemies)
                    d20 = random.randint(1, 20)
                    if d20 == 20 or (
                        d20 + atk_bonus >= tgt["ac"]
                    ):
                        dmg = max(
                            1,
                            base_dmg
                            + random.randint(-1, 1),
                        )
                        if d20 == 20:
                            dmg = int(dmg * 1.75)
                        tgt["hp"] -= dmg
                        total_dmg_dealt += dmg
                        if tgt["hp"] <= 0:
                            tgt["alive"] = False
                        # Stunning Strike: 25% chance
                        if (
                            char.ki_points > 0
                            and random.random() < 0.25
                        ):
                            char.ki_points -= 1
                            tgt["stunned"] = True

            # ── Sorcerer: Quickened cantrip ──
            if cls == "Sorcerer" and char.quicken_uses > 0:
                living_enemies = [
                    e for e in enemies if e["alive"]
                ]
                if living_enemies:
                    char.quicken_uses -= 1
                    tgt = random.choice(living_enemies)
                    d20 = random.randint(1, 20)
                    if d20 == 20 or (
                        d20 + atk_bonus >= tgt["ac"]
                    ):
                        dmg = max(
                            1,
                            base_dmg
                            + random.randint(-1, 1),
                        )
                        if d20 == 20:
                            dmg = int(dmg * 1.75)
                        tgt["hp"] -= dmg
                        total_dmg_dealt += dmg
                        if tgt["hp"] <= 0:
                            tgt["alive"] = False

            # ── Fighter: Action Surge (once/encounter) ──
            if (
                cls == "Fighter"
                and char.action_surge_uses > 0
                and action_surge_used.get(
                    char.name, 0,
                ) < 1
            ):
                action_surge_used[char.name] = (
                    action_surge_used.get(char.name, 0)
                    + 1
                )
                char.action_surge_uses -= 1
                for _s in range(char.attacks_per_round):
                    living_enemies = [
                        e for e in enemies
                        if e["alive"]
                    ]
                    if not living_enemies:
                        break
                    tgt = random.choice(living_enemies)
                    d20 = random.randint(1, 20)
                    if d20 == 20 or (
                        d20 + atk_bonus >= tgt["ac"]
                    ):
                        dmg = max(
                            1,
                            base_dmg
                            + random.randint(-2, 2),
                        )
                        if d20 == 20:
                            dmg = int(dmg * 1.75)
                        tgt["hp"] -= dmg
                        total_dmg_dealt += dmg
                        if tgt["hp"] <= 0:
                            tgt["alive"] = False

        living_enemies = [e for e in enemies if e["alive"]]
        if not living_enemies:
            break

        # ═══ ENEMY ATTACK PHASE ═══════════════════════════
        for enemy in living_enemies:
            if not enemy["alive"]:
                continue
            if enemy.get("stunned"):
                continue  # Stunned enemies skip turn

            valid_targets = [
                c for c in living_party
                if not c.is_dead and c.current_hp > 0
            ]
            if not valid_targets:
                break

            target_char = random.choice(valid_targets)
            e_atk = enemy["attack_bonus"]
            e_dc = enemy["save_dc"]
            n_atk = enemy["num_attacks"]
            per_hit = enemy["per_hit_damage"]

            for _ea in range(n_atk):
                valid_targets = [
                    c for c in living_party
                    if not c.is_dead
                    and c.current_hp > 0
                ]
                if not valid_targets:
                    break
                target_char = random.choice(valid_targets)

                # Effective AC (Rogue cunning action)
                eff_ac = target_char.ac + (
                    target_char.cunning_action_ac
                    if target_char.char_class == "Rogue"
                    else 0
                )

                # 30% save-based attacks at CR 5+
                is_save_atk = (
                    enemy["cr"] >= 5
                    and random.random() < 0.30
                )

                if is_save_atk:
                    save_roll = (
                        random.randint(1, 20)
                        + target_char.con_save_bonus
                    )
                    if save_roll >= e_dc:
                        dmg = max(1, per_hit // 2)
                    else:
                        dmg = per_hit
                    # Rogue evasion (lvl 7+): halve
                    if (
                        target_char.char_class == "Rogue"
                        and target_char.level >= 7
                    ):
                        dmg = dmg // 2
                else:
                    # Normal attack roll
                    d20 = random.randint(1, 20)
                    is_crit = d20 == 20
                    hit_roll = d20 + e_atk

                    # Wizard Shield spell
                    if (
                        target_char.char_class == "Wizard"
                        and target_char.shield_uses > 0
                        and hit_roll >= eff_ac
                        and hit_roll < eff_ac + 5
                        and random.random() < 0.5
                    ):
                        target_char.shield_uses -= 1
                        continue  # Shield negates hit

                    if not (
                        is_crit
                        or hit_roll >= eff_ac
                    ):
                        continue  # Miss

                    dmg = per_hit
                    if is_crit:
                        dmg = int(dmg * 1.75)

                # Barbarian rage: halve physical dmg
                if (
                    target_char.char_class == "Barbarian"
                    and target_char.is_raging
                ):
                    dmg = dmg // 2

                dmg = max(1, dmg + random.randint(-2, 2))
                target_char.current_hp -= dmg
                total_dmg_taken += dmg

                # Check for downing
                if (
                    target_char.current_hp <= 0
                    and not target_char.is_dead
                ):
                    characters_downed += 1
                    key = target_char.name
                    if key not in rounds_on_final_stand:
                        rounds_on_final_stand[key] = 0
                    rounds_on_final_stand[key] += 1

                    dc = compute_final_stand_dc(
                        rounds_on_final_stand[key],
                    )
                    con_roll = (
                        random.randint(1, 20)
                        + target_char.con_save_bonus
                    )
                    final_stand_checks += 1

                    if con_roll >= dc:
                        target_char.current_hp = 1
                    else:
                        target_char.is_dead = True
                        target_char.deaths += 1
                        final_stand_deaths += 1

        # ── End-of-round party status check ──
        alive_count = sum(
            1 for c in living_party
            if not c.is_dead and c.current_hp > 0
        )
        if alive_count == 0:
            return CombatResult(
                rounds=round_num,
                party_survived=False,
                damage_taken_total=total_dmg_taken,
                damage_dealt_total=total_dmg_dealt,
                weakness_exploits=weakness_exploits,
                chain_bonuses=chain_bonuses,
                characters_downed=characters_downed,
                final_stand_checks=final_stand_checks,
                final_stand_deaths=final_stand_deaths,
                armillary_events=armillary_events,
            )

    return CombatResult(
        rounds=min(round_num, max_rounds),
        party_survived=True,
        damage_taken_total=total_dmg_taken,
        damage_dealt_total=total_dmg_dealt,
        weakness_exploits=weakness_exploits,
        chain_bonuses=chain_bonuses,
        characters_downed=characters_downed,
        final_stand_checks=final_stand_checks,
        final_stand_deaths=final_stand_deaths,
        armillary_events=armillary_events,
    )


# ══════════════════════════════════════════════════════════════════════════
# Recovery functions
# ══════════════════════════════════════════════════════════════════════════

def apply_momentum_recovery(party: list[SimCharacter]):
    """Simulate between-arena momentum recovery."""
    for char in party:
        if char.is_dead:
            continue
        # ~15% HP recovery
        heal = max(1, char.max_hp // 6)
        char.current_hp = min(
            char.max_hp, char.current_hp + heal,
        )
        if char.spell_slots_used > 0:
            char.spell_slots_used = max(
                0, char.spell_slots_used - 1,
            )
        # Reset per-encounter flags
        char.reset_encounter_resources()


def apply_short_rest(party: list[SimCharacter]):
    """Short rest: hit dice, short-rest abilities."""
    for char in party:
        if char.is_dead:
            continue
        heal = max(1, char.max_hp // 3)
        char.current_hp = min(
            char.max_hp, char.current_hp + heal,
        )
        # Recover short-rest spell slots + abilities
        char.spell_slots_used = max(
            0, char.spell_slots_used - 2,
        )
        # Fighter: recover Action Surge + Second Wind
        if char.char_class == "Fighter":
            char.action_surge_uses = (
                1 if char.level >= 2 else 0
            )
            if char.level >= 17:
                char.action_surge_uses = 2
            char.second_wind_uses = 1
        # Warlock: recover pact slots fully
        if char.char_class == "Warlock":
            char.spell_slots_used = 0
        # Monk: recover all ki
        if char.char_class == "Monk":
            char.ki_points = char.ki_points_max
        # Bard: recover Bardic Inspiration
        if char.char_class == "Bard":
            char.bardic_inspiration_uses = max(
                3, 3 + char.level // 4,
            )
        char.reset_encounter_resources()


def apply_long_rest(party: list[SimCharacter]):
    """Long rest: full HP, all resources recovered."""
    for char in party:
        if char.is_dead:
            char.is_dead = False
            char.current_hp = char.max_hp // 2
        else:
            char.current_hp = char.max_hp
        char.spell_slots_used = 0
        char.reset_encounter_resources()
        # Restore all class resources
        char._apply_class_features(
            min(5, 3 + (char.level // 4)),
        )


# ══════════════════════════════════════════════════════════════════════════
# Main simulation
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class FloorResult:
    floor_number: int
    party_level: int
    tier: int
    arenas_completed: int
    total_arenas: int
    party_survived: bool
    gold_earned: int
    shards_earned: int
    xp_earned_per_char: int
    level_ups: list[str]
    encounters: list[dict]
    combat_results: list[CombatResult]
    difficulty_notes: list[str] = field(default_factory=list)
    ppc: float = 1.0
    hp_at_end: float = 1.0
    deaths_this_floor: int = 0
    recovery_schedule: list[str] = field(default_factory=list)
    shop_purchases: list[str] = field(default_factory=list)


@dataclass
class RunResult:
    floors: list[FloorResult]
    total_gold: int = 0
    total_shards: int = 0
    total_xp: int = 0
    final_level: int = 1
    run_completed: bool = False
    tpk_count: int = 0
    gacha_results: list[dict] = field(default_factory=list)
    gold_spent: int = 0


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


async def simulate_full_run(seed: int = 42) -> RunResult:
    """Run the complete 1-to-20 simulation."""
    random.seed(seed)

    party = create_standard_party()
    monster_dicts = await load_monster_dicts()
    print(f"  Loaded {len(monster_dicts)} monsters from database")
    scaling = get_scaling_params(len(party))

    ppc = 1.0
    total_gold = 0
    total_shards = 0
    gold_spent = 0
    run_result = RunResult(floors=[])

    # Gacha state
    pity_state = {
        "pulls_since_rare": 0,
        "pulls_since_very_rare": 0,
        "pulls_since_legendary": 0,
        "total_pulls": 0,
    }
    owned_gacha_ids: set[str] = set()
    gacha_items_count = 0
    owned_investment_ids: set[str] = set()
    shop_discount = 0.0
    first_boss_killed = False

    max_floors = 20
    used_floor_themes: list[str] = []

    for floor_num in range(1, max_floors + 1):
        party_level = party[0].level
        tier = get_tier(party_level)
        total_arenas = min(scaling.max_arenas_per_floor, 3 + (tier - 1))
        is_calibration = floor_num <= 2

        # Generate rest schedule for this floor
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
        snapshots = []
        had_boss_kill = False

        # Floor biome selection (Phase 4)
        floor_biome = select_floor_biome(
            floor_num, party_level, monster_dicts,
        )
        used_environments: list[str] = []

        # Floor theme selection
        floor_theme_def = select_theme_for_floor(
            biome=floor_biome,
            floor_number=floor_num,
            used_themes=used_floor_themes[-3:],
        )
        floor_theme_id = (
            floor_theme_def.id if floor_theme_def else None
        )
        if floor_theme_id:
            used_floor_themes.append(floor_theme_id)

        # Compute leveling speed from accumulated power
        leveling_speed = compute_power_xp_bonus(
            gacha_items_owned=gacha_items_count,
            floors_completed=floor_num - 1,
        )

        # --- Between-floor difficulty target (computed ONCE per floor) ---
        # Uses previous floor's end-state for calibration
        prev_floor = run_result.floors[-1] if run_result.floors else None
        prev_hp = prev_floor.hp_at_end if prev_floor else 1.0
        prev_deaths = prev_floor.deaths_this_floor if prev_floor else 0
        prev_tpk = not prev_floor.party_survived if prev_floor else False
        prev_assessment = (
            "healthy" if prev_hp > 0.6
            else ("strained" if prev_hp > 0.3 else "critical")
        )

        # Compute floor-level difficulty target (same for all arenas)
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
            # --- Intensity curve with attrition-aware pacing ---
            intensity = compute_intensity_curve(
                arena_num, total_arenas, floor_num,
                party_power_coefficient=ppc,
                rest_schedule=schedule,
            )

            # --- Check party is alive ---
            living = [c for c in party if not c.is_dead]
            if not living:
                floor_result.party_survived = False
                break

            # Use the floor-level difficulty target with arena pacing
            diff_target = floor_diff_target

            # --- Generate encounter ---
            party_damage_types = list(set(
                dt for c in living for dt in c.damage_types
            ))

            is_boss = (arena_num == total_arenas and floor_num % 4 == 0)
            inp = PipelineInput(
                party_level=party_level,
                party_size=len(living),
                difficulty=diff_target.difficulty,
                floor_number=floor_num,
                arena_number=arena_num,
                templates_used=templates_used,
                party_damage_types=party_damage_types,
                difficulty_multiplier=(
                    diff_target.xp_multiplier
                ),
                used_objectives=used_objectives,
                is_boss=is_boss,
                exclude_monster_ids=exclude_monster_ids,
                biome_constraint=floor_biome,
                used_environments=used_environments,
                floor_theme=floor_theme_id,
            )

            try:
                proposal = generate_encounter(inp, monster_dicts)
            except Exception as e:
                floor_result.difficulty_notes.append(
                    f"Arena {arena_num}: Encounter generation failed: {e}"
                )
                continue

            templates_used.append(proposal.template)
            if proposal.objective_id:
                used_objectives.append(proposal.objective_id)
            if proposal.environment_name:
                used_environments.append(proposal.environment_name)

            for creature in proposal.creatures:
                exclude_monster_ids.add(creature.monster_id)

            enc_info = {
                "arena": arena_num,
                "template": proposal.template,
                "xp_budget": proposal.xp_budget,
                "raw_xp": (
                    proposal.total_raw_xp
                    if hasattr(proposal, "total_raw_xp")
                    else proposal.adjusted_xp
                ),
                "adjusted_xp": proposal.adjusted_xp,
                "difficulty": diff_target.difficulty,
                "intensity": intensity.intensity,
                "phase": intensity.phase.value,
                "environment": proposal.environment_name,
                "objective": proposal.objective_name,
                "theme": proposal.theme_name,
                "creature_count": proposal.creature_count,
                "creatures": [
                    {
                        "name": c.name, "cr": c.cr, "hp": c.hp,
                        "ac": c.ac, "count": c.count,
                        "tactical_role": c.tactical_role,
                        "xp": c.xp,
                        "vulnerabilities": [],
                    }
                    for c in proposal.creatures
                ],
                "terrain": proposal.terrain_features[:3],
                "tactical_brief": proposal.tactical_brief[:150],
                "warnings": [w.message for w in proposal.warnings],
                "danger_rating": proposal.danger_rating,
                "is_boss": is_boss,
                "biome": floor_biome,
            }
            floor_result.encounters.append(enc_info)

            # --- Build creature dicts with vulnerability data ---
            creature_dicts = []
            for c in proposal.creatures:
                # Find vulnerabilities from monster_dicts
                vulns = []
                for md in monster_dicts:
                    if md["id"] == c.monster_id:
                        vulns = md.get("vulnerabilities", [])
                        break
                creature_dicts.append({
                    "name": c.name, "cr": c.cr, "hp": c.hp,
                    "ac": c.ac, "count": c.count,
                    "tactical_role": c.tactical_role, "xp": c.xp,
                    "vulnerabilities": vulns,
                    "weak_saves": [],
                })

            # --- Simulate combat ---
            combat = simulate_combat(
                party, creature_dicts,
                floor_num, arena_num,
                ppc=ppc,
                gacha_items=gacha_items_count,
            )
            floor_result.combat_results.append(combat)

            if not combat.party_survived:
                floor_result.party_survived = False
                floor_result.arenas_completed = arena_num
                deaths_this_floor += combat.final_stand_deaths
                break

            floor_result.arenas_completed = arena_num
            deaths_this_floor += combat.final_stand_deaths

            if is_boss and combat.party_survived:
                had_boss_kill = True
                if not first_boss_killed:
                    first_boss_killed = True

            # --- XP award (uses RAW XP, not adjusted) ---
            raw_xp = sum(c.xp * c.count for c in proposal.creatures)
            xp_award = compute_arena_xp_award(raw_xp, len(living), leveling_speed)
            floor_xp_per_char += xp_award
            for c in party:
                if not c.is_dead:
                    c.xp += xp_award

            # --- Gold award ---
            arena_gold = compute_arena_gold(arena_num, party_level, diff_target.difficulty)
            floor_gold += arena_gold

            # --- Snapshot (for end-of-floor assessment) ---
            living_after = [c for c in party if not c.is_dead]
            avg_hp_after = sum(c.hp_pct() for c in living_after) / max(1, len(living_after))
            snapshot = {
                "average_hp_percentage": avg_hp_after,
                "any_dead": any(c.is_dead for c in party),
                "dm_combat_perception": (
                    "too_easy" if avg_hp_after > 0.8
                    else ("just_right" if avg_hp_after > 0.4
                          else ("too_hard" if avg_hp_after > 0.15
                                else "near_tpk"))
                ),
            }
            snapshots.append(snapshot)

            # --- Between-arena recovery ---
            if arena_num < total_arenas:
                gap_idx = arena_num - 1  # 0-indexed gap
                if gap_idx < len(schedule):
                    if schedule[gap_idx] == "short_rest":
                        apply_short_rest(party)
                    else:
                        apply_momentum_recovery(party)
                else:
                    apply_momentum_recovery(party)

        # --- Floor completion ---
        floor_result.deaths_this_floor = deaths_this_floor

        # Milestone bonus
        if floor_result.party_survived:
            floor_gold += compute_milestone_gold(floor_num, party_level)

            # Shard rewards (scaled with floor)
            floor_shards = compute_floor_clear_shards(floor_num)
            floor_shards += compute_achievement_shards(
                first_boss_kill=(had_boss_kill and first_boss_killed),
                no_deaths_this_floor=(deaths_this_floor == 0),
                full_clear=(floor_result.arenas_completed == total_arenas),
            )
            floor_result.shards_earned = floor_shards
        else:
            floor_result.shards_earned = 0

        floor_result.gold_earned = floor_gold
        total_gold += floor_result.gold_earned
        total_shards += floor_result.shards_earned
        floor_result.xp_earned_per_char = floor_xp_per_char

        # --- Level-up check ---
        for c in party:
            if not c.is_dead and check_level_up(c.level, c.xp):
                old_level = c.level
                c.level_up()
                floor_result.level_ups.append(f"{c.name} ({c.char_class}): {old_level} → {c.level}")

        # --- End-of-floor HP + PPC update (between-floor calibration) ---
        living_at_end = [c for c in party if not c.is_dead]
        avg_hp_end = (
            sum(c.hp_pct() for c in living_at_end)
            / max(1, len(living_at_end))
            if living_at_end
            else 0.0
        )
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

        # --- Shop (spend gold between floors) ---
        available_gold = total_gold - gold_spent
        if available_gold > 100 and floor_result.party_survived:
            shop = generate_shop_inventory(
                party_level=party_level,
                floor_number=floor_num,
                owned_investment_ids=owned_investment_ids,
                discount=shop_discount,
            )
            # Buy the best affordable item (tier-scaled pricing)
            affordable = [
                i for i in shop.items
                if compute_item_price(i, shop.discount, party_level) <= available_gold
            ]
            if affordable:
                # Prefer prestige > investments > party buffs > individual > consumables
                priority = {
                    "prestige": 0, "investment": 1,
                    "party_buff": 2, "individual": 3,
                    "consumable": 4,
                }
                affordable.sort(key=lambda i: (priority.get(i.category.value, 5), -i.base_price))
                bought = affordable[0]
                price = compute_item_price(bought, shop.discount, party_level)
                gold_spent += price
                floor_result.shop_purchases.append(f"{bought.name} ({price}g)")
                if bought.category.value == "investment":
                    owned_investment_ids.add(bought.id)
                    if "shop_discount" in (bought.effect or {}):
                        shop_discount += bought.effect["shop_discount"]

        # --- Gacha pull ---
        if total_shards - (gold_spent // 100) >= SHARDS_PER_PULL:  # Don't double-count
            # Use actual shard balance
            available_shards = total_shards - sum(
                SHARDS_PER_PULL for g in run_result.gacha_results
            )
            if available_shards >= SHARDS_PER_PULL:
                pull_result = determine_rarity(
                    pulls_since_rare=pity_state["pulls_since_rare"],
                    pulls_since_very_rare=pity_state["pulls_since_very_rare"],
                    pulls_since_legendary=pity_state["pulls_since_legendary"],
                    floor_number=floor_num,
                )
                # Cycle through banners
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
                            "floor": floor_num,
                            "rarity": pull_result.rarity,
                            "item": item.name,
                            "banner": banner.name,
                            "was_pity": pull_result.was_pity,
                        })
                pity_state = update_pity_counters(pity_state, pull_result.rarity)

        # --- Long rest at end of floor ---
        apply_long_rest(party)

        # --- Sync party levels (all level together) ---
        max_level = max(c.level for c in party)
        for c in party:
            while c.level < max_level:
                c.level_up()

        run_result.floors.append(floor_result)

        if not floor_result.party_survived:
            run_result.tpk_count += 1
            floor_result.difficulty_notes.append(
                "TPK! Party wipes but revives at long rest for next floor."
            )

        if party[0].level >= 20:
            break

    # Final stats
    run_result.total_gold = total_gold
    run_result.total_shards = total_shards
    run_result.gold_spent = gold_spent
    run_result.final_level = party[0].level
    run_result.run_completed = party[0].level >= 20

    return run_result


# ══════════════════════════════════════════════════════════════════════════
# Report generation
# ══════════════════════════════════════════════════════════════════════════

def generate_report(result: RunResult) -> str:
    """Generate a detailed markdown report."""
    out = StringIO()
    def p(*args, **kwargs):
        print(*args, **kwargs, file=out)

    p("# Drifting Infinity — Full Run Simulation Report (v3)")
    p()
    p(f"**Final Level:** {result.final_level} | "
      f"**Floors Completed:** {len(result.floors)} | "
      f"**Run Completed:** {'YES' if result.run_completed else 'NO'}")
    p(f"**Total Gold:** {result.total_gold:,} | "
      f"**Gold Spent:** {result.gold_spent:,} | "
      f"**Total Shards:** {result.total_shards}")
    p(f"**Gacha Pulls:** {len(result.gacha_results)} | "
      f"**TPK Count:** {result.tpk_count}")
    p()

    # ── Summary table ─────────────────────────────────────────────────
    p("## Floor Summary")
    p()
    p("| Floor | Level | Tier | Arenas | Survived | Gold | XP/Char "
      "| PPC | HP% End | Deaths | Level Ups |")
    p("|-------|-------|------|--------|----------|------|---------"
      "|-----|---------|--------|-----------|")
    for f in result.floors:
        survived = "YES" if f.party_survived else "**TPK**"
        level_ups = ", ".join(f.level_ups) if f.level_ups else "-"
        p(f"| {f.floor_number:2d} | {f.party_level:2d} "
          f"| {f.tier} | {f.arenas_completed}/{f.total_arenas} "
          f"| {survived} | {f.gold_earned:,} "
          f"| {f.xp_earned_per_char:,} | {f.ppc:.2f} "
          f"| {f.hp_at_end:.0%} | {f.deaths_this_floor} "
          f"| {level_ups} |")

    # ── Detailed floor reports ────────────────────────────────────────
    p()
    p("---")
    p()
    p("## Detailed Floor Reports")

    for f in result.floors:
        p()
        p(f"### Floor {f.floor_number} (Party Level {f.party_level}, Tier {f.tier})")
        rest_sched = (
            " → ".join(f.recovery_schedule)
            if f.recovery_schedule else "N/A"
        )
        p(f"- **Rest Schedule:** {rest_sched} → Long Rest")
        if f.shop_purchases:
            p(f"- **Shop:** {', '.join(f.shop_purchases)}")
        p()
        if f.difficulty_notes:
            for note in f.difficulty_notes:
                p(f"> {note}")
            p()

        for i, enc in enumerate(f.encounters):
            combat = f.combat_results[i] if i < len(f.combat_results) else None
            boss_tag = " [BOSS]" if enc.get("is_boss") else ""
            danger = enc.get("danger_rating", "")
            danger_tag = f" [{danger}]" if danger else ""
            p(f"#### Arena {enc['arena']}: {enc['template']}"
              f"{boss_tag}{danger_tag} "
              f"({enc['phase']}, intensity {enc['intensity']:.2f})")
            p()
            p(f"- **Difficulty:** {enc['difficulty']} | "
              f"**Danger:** {danger or '?'} | "
              f"**XP Budget:** {enc['xp_budget']:,} | "
              f"**Raw XP:** {enc.get('raw_xp', '?'):,}")
            p(f"- **Environment:** {enc['environment']} "
              f"(Biome: {enc.get('biome', '?')})", end="")
            if enc.get("theme"):
                p(f" | **Theme:** {enc['theme']}", end="")
            if enc.get("objective"):
                p(f" | **Objective:** {enc['objective']}", end="")
            p()

            if enc.get("terrain"):
                p(f"- **Terrain:** {', '.join(enc['terrain'])}")

            p(f"- **Creatures ({enc['creature_count']}):**")
            for creature in enc["creatures"]:
                p(f"  - {creature['name']} "
                  f"(CR {creature['cr']}, "
                  f"HP {creature['hp']}, "
                  f"AC {creature['ac']}) "
                  f"x{creature['count']} "
                  f"[{creature['tactical_role']}] "
                  f"— {creature['xp']} XP each")

            if enc.get("warnings"):
                for w in enc["warnings"]:
                    p(f"  - **WARNING:** {w}")

            if combat:
                survived_txt = (
                    "Survived" if combat.party_survived
                    else "**PARTY WIPED**"
                )
                p(f"- **Combat:** {combat.rounds} rounds | "
                  f"{survived_txt} | "
                  f"Dmg dealt: {combat.damage_dealt_total:,} | "
                  f"Dmg taken: {combat.damage_taken_total:,}")
                if combat.weakness_exploits > 0:
                    p(f"  - Weakness Exploits: "
                      f"{combat.weakness_exploits} | "
                      f"Chain Bonuses: {combat.chain_bonuses}")
                if combat.characters_downed > 0:
                    p(f"  - Characters Downed: {combat.characters_downed} | "
                      f"Final Stand Deaths: {combat.final_stand_deaths}")
                if combat.armillary_events:
                    p("  - **Armillary Events:**")
                    for ae in combat.armillary_events:
                        p(f"    - R{ae['round']}: "
                          f"[{ae['category']}] {ae['name']} "
                          f"(severity {ae['severity']})")
            p()

    # ── Economy report ────────────────────────────────────────────────
    p("---")
    p()
    p("## Economy Report")
    p()
    p("| Metric | Value |")
    p("|--------|-------|")
    p(f"| Total Gold Earned | {result.total_gold:,} |")
    p(f"| Total Gold Spent | {result.gold_spent:,} |")
    p(f"| Gold Remaining | {result.total_gold - result.gold_spent:,} |")
    p(f"| Total Shards Earned | {result.total_shards} |")
    p(f"| Total Gacha Pulls | {len(result.gacha_results)} |")
    p()

    if result.gacha_results:
        p("### Gacha Pull History")
        p()
        p("| Floor | Banner | Rarity | Item | Pity? |")
        p("|-------|--------|--------|------|-------|")
        for g in result.gacha_results:
            pity = "YES" if g["was_pity"] else "no"
            p(f"| {g['floor']} | {g.get('banner', '?')} "
              f"| {g['rarity']} | {g['item']} | {pity} |")
        p()
        # Check for duplicates
        items = [g['item'] for g in result.gacha_results]
        dupes = [item for item in set(items) if items.count(item) > 1]
        if dupes:
            p(f"**Duplicate Items:** {', '.join(dupes)}")
        else:
            p("**No duplicate items!**")
        p()

    # ── Balance analysis ──────────────────────────────────────────────
    p("---")
    p()
    p("## Balance Analysis")
    p()

    # Leveling pace
    p("### Leveling Pace")
    p(f"- Floors to reach level 5 (Tier 2): {_floors_to_level(result, 5)}")
    p(f"- Floors to reach level 11 (Tier 3): {_floors_to_level(result, 11)}")
    p(f"- Floors to reach level 17 (Tier 4): {_floors_to_level(result, 17)}")
    p(f"- Floors to reach level 20: {_floors_to_level(result, 20)}")
    p()

    # Encounter stats
    total_encounters = sum(len(f.encounters) for f in result.floors)
    total_creatures = sum(enc["creature_count"] for f in result.floors for enc in f.encounters)
    templates_used = {}
    for f in result.floors:
        for enc in f.encounters:
            templates_used[enc["template"]] = templates_used.get(enc["template"], 0) + 1

    p("### Encounter Statistics")
    p(f"- Total encounters: {total_encounters}")
    p(f"- Total creatures faced: {total_creatures}")
    p(f"- Avg creatures per encounter: {total_creatures / max(1, total_encounters):.1f}")
    empty_encounters = sum(
        1 for f in result.floors
        for enc in f.encounters if enc["creature_count"] == 0
    )
    p(f"- Empty encounters: {empty_encounters}")
    p()
    p("**Template Distribution:**")
    for template, count in sorted(templates_used.items(), key=lambda x: -x[1]):
        p(f"- {template}: {count} ({count/max(1,total_encounters)*100:.0f}%)")
    p()

    # Danger rating distribution
    danger_counts: dict[str, int] = {}
    for f in result.floors:
        for enc in f.encounters:
            dr = enc.get("danger_rating", "Unknown")
            danger_counts[dr] = danger_counts.get(dr, 0) + 1
    if danger_counts:
        p("**Danger Rating Distribution:**")
        for rating in ["Challenging", "Dangerous", "Brutal", "Lethal"]:
            count = danger_counts.get(rating, 0)
            pct = count / max(1, total_encounters) * 100
            p(f"- {rating}: {count} ({pct:.0f}%)")
        p()

    # Biome distribution
    biome_counts: dict[str, int] = {}
    for f in result.floors:
        for enc in f.encounters:
            biome = enc.get("biome", "unknown")
            biome_counts[biome] = biome_counts.get(biome, 0) + 1
    if biome_counts:
        p("**Biome Distribution:**")
        for biome, count in sorted(biome_counts.items(), key=lambda x: -x[1]):
            p(f"- {biome}: {count} ({count/max(1,total_encounters)*100:.0f}%)")
        p()

    # Environment variety
    env_names = set()
    for f in result.floors:
        for enc in f.encounters:
            if enc.get("environment"):
                env_names.add(enc["environment"])
    p(f"**Unique environments used:** {len(env_names)}")
    p()

    # Gold economy analysis
    spend_ratio = result.gold_spent / max(1, result.total_gold) * 100
    p("### Gold Economy")
    p(f"- Total earned: {result.total_gold:,}")
    p(f"- Total spent: {result.gold_spent:,}")
    p(f"- Spend ratio: {spend_ratio:.1f}%")
    if spend_ratio < 20:
        p(f"  - **WARNING:** Low spend ratio ({spend_ratio:.1f}%) — players hoarding gold")
    elif spend_ratio > 80:
        p(f"  - **WARNING:** High spend ratio ({spend_ratio:.1f}%) — shop may be too enticing")
    else:
        p("  - Healthy spend ratio")
    p()

    # Combat stats
    total_exploits = sum(c.weakness_exploits for f in result.floors for c in f.combat_results)
    total_chains = sum(c.chain_bonuses for f in result.floors for c in f.combat_results)
    total_downings = sum(c.characters_downed for f in result.floors for c in f.combat_results)
    total_fs_deaths = sum(c.final_stand_deaths for f in result.floors for c in f.combat_results)
    total_armillary = sum(len(c.armillary_events) for f in result.floors for c in f.combat_results)

    p("### Combat Statistics")
    p(f"- Weakness exploits triggered: {total_exploits}")
    p(f"- Chain bonuses: {total_chains}")
    p(f"- Total character downings: {total_downings}")
    p(f"- Final Stand deaths: {total_fs_deaths}")
    p(f"- TPK count: {result.tpk_count}")
    p(f"- Armillary events fired: {total_armillary}")
    p()

    # PPC tracking
    p("### Difficulty Director (PPC Tracking)")
    p()
    ppc_values = [f.ppc for f in result.floors]
    p("- Starting PPC: 1.00")
    p(f"- Final PPC: {ppc_values[-1]:.2f}")
    p(f"- Min PPC: {min(ppc_values):.2f}")
    p(f"- Max PPC: {max(ppc_values):.2f}")
    p(f"- PPC trend: {' → '.join(f'{v:.2f}' for v in ppc_values)}")
    p()

    # Armillary category breakdown
    arm_categories = {"hostile": 0, "beneficial": 0, "environmental": 0, "wild": 0}
    for f in result.floors:
        for c in f.combat_results:
            for ae in c.armillary_events:
                cat = ae.get("category", "unknown")
                arm_categories[cat] = arm_categories.get(cat, 0) + 1
    if total_armillary > 0:
        p("### Armillary Event Breakdown")
        for cat, count in sorted(arm_categories.items(), key=lambda x: -x[1]):
            pct = count / max(1, total_armillary) * 100
            p(f"- {cat}: {count} ({pct:.0f}%)")
        p()

    # ── Issues & warnings ─────────────────────────────────────────────
    p("---")
    p()
    p("## Issues & Observations")
    p()

    issues = []
    for f in result.floors:
        for enc in f.encounters:
            if enc["creature_count"] == 0:
                issues.append(
                    f"Floor {f.floor_number} Arena {enc['arena']}: "
                    "No creatures generated"
                )
            for w in enc.get("warnings", []):
                issues.append(f"Floor {f.floor_number} Arena {enc['arena']}: {w}")
        for note in f.difficulty_notes:
            issues.append(f"Floor {f.floor_number}: {note}")

    # Balance checks
    ftl5 = _floors_to_level(result, 5)
    if ftl5 == "N/A":
        issues.append("BALANCE: Party never reached level 5")
    elif isinstance(ftl5, int) and ftl5 > 8:
        issues.append(f"BALANCE: Slow leveling — took {ftl5} floors to reach level 5")

    if result.tpk_count > 3:
        issues.append(
            f"BALANCE: High TPK rate "
            f"({result.tpk_count} TPKs in {len(result.floors)} floors)"
        )

    if total_exploits == 0:
        issues.append("BALANCE: No weakness exploits triggered — vulnerability data may be empty")

    # Gold economy check
    spend_ratio = result.gold_spent / max(1, result.total_gold) * 100
    if spend_ratio < 15:
        issues.append(
            f"BALANCE: Very low gold spend ratio "
            f"({spend_ratio:.1f}%) — shop items too cheap or too few"
        )

    # Danger rating distribution check
    danger_dist: dict[str, int] = {}
    for f in result.floors:
        for enc in f.encounters:
            dr = enc.get("danger_rating", "")
            if dr:
                danger_dist[dr] = danger_dist.get(dr, 0) + 1
    lethal_count = danger_dist.get("Lethal", 0)
    if total_encounters > 0 and lethal_count / total_encounters > 0.5:
        issues.append(
            f"BALANCE: Too many Lethal encounters ({lethal_count}/{total_encounters} = "
            f"{lethal_count/total_encounters:.0%})"
        )
    challenging_count = danger_dist.get("Challenging", 0)
    if total_encounters > 0 and challenging_count / total_encounters > 0.5:
        issues.append(
            f"BALANCE: Too many Challenging encounters ({challenging_count}/{total_encounters} = "
            f"{challenging_count/total_encounters:.0%}) — difficulty too low"
        )

    hostile_count = arm_categories.get("hostile", 0)
    if total_armillary > 0 and hostile_count / total_armillary > 0.6:
        hostile_pct = hostile_count / total_armillary
        issues.append(
            f"BALANCE: Armillary skews hostile "
            f"({hostile_count}/{total_armillary} = {hostile_pct:.0%})"
        )

    if empty_encounters > 0:
        issues.append(f"BUG: {empty_encounters} encounters generated with zero creatures")

    if issues:
        for issue in issues:
            p(f"- {issue}")
    else:
        p("No issues detected!")
    p()

    return out.getvalue()


def _floors_to_level(result: RunResult, target_level: int):
    """Find which floor the party first reached a given level."""
    for f in result.floors:
        for lu in f.level_ups:
            if f"→ {target_level}" in lu:
                return f.floor_number
    if result.final_level >= target_level:
        return len(result.floors)
    return "N/A"


# ══════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════

async def main():
    print("=" * 70)
    print("  DRIFTING INFINITY — FULL RUN SIMULATION v3")
    print("  Party: Fighter, Cleric, Rogue, Wizard (Level 1 → 20)")
    print("  v3: Kobold Press monsters, danger ratings, tier-scaled shop,")
    print("      prestige sinks, floor biome system, environment variety")
    print("=" * 70)
    print()

    result = await simulate_full_run(seed=42)
    report = generate_report(result)

    print(report)

    output_path = Path(__file__).parent / "simulation_report_v3.md"
    output_path.write_text(report)
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
