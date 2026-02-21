"""Tests for meta-progression systems (talents, essence, achievements, lives, run reset)."""

import pytest

from app.engine.meta.achievements import (
    ACHIEVEMENTS,
    check_achievements,
    get_achievement,
)
from app.engine.meta.essence import compute_achievement_essence, compute_run_essence
from app.engine.meta.lives import (
    BASE_STARTING_LIVES,
    MAX_LIVES,
    add_life,
    can_resurrect,
    compute_starting_lives,
    process_character_death,
    process_tpk,
)
from app.engine.meta.run_reset import (
    compute_run_start_state,
    decay_ppc_between_runs,
    reset_character_for_new_run,
)
from app.engine.meta.talents import (
    TALENT_TREE,
    can_unlock,
    get_active_effects,
    get_branch,
    get_talent,
    unlock_talent,
)


# ---- Talent Tree ----

class TestTalentTree:
    def test_all_talents_present(self):
        assert len(TALENT_TREE) == 15  # 3 branches * 5 tiers

    def test_branches_have_5_tiers(self):
        for branch_name in ("resilience", "insight", "fortune"):
            branch = get_branch(branch_name)
            assert len(branch) == 5
            tiers = [t.tier for t in branch]
            assert tiers == [1, 2, 3, 4, 5]

    def test_get_talent_valid(self):
        t = get_talent("resilience_1")
        assert t is not None
        assert t.name == "Second Wind"
        assert t.branch == "resilience"
        assert t.tier == 1

    def test_get_talent_invalid(self):
        assert get_talent("nonexistent") is None

    def test_costs_increase_with_tier(self):
        for branch_name in ("resilience", "insight", "fortune"):
            branch = get_branch(branch_name)
            for i in range(1, len(branch)):
                assert branch[i].cost >= branch[i - 1].cost


class TestCanUnlock:
    def test_can_unlock_tier_1(self):
        assert can_unlock("resilience_1", [], essence=30) is True

    def test_cannot_unlock_insufficient_essence(self):
        assert can_unlock("resilience_1", [], essence=10) is False

    def test_cannot_unlock_already_unlocked(self):
        assert can_unlock("resilience_1", ["resilience_1"], essence=100) is False

    def test_cannot_skip_tiers(self):
        # Can't unlock tier 2 without tier 1
        assert can_unlock("resilience_2", [], essence=200) is False

    def test_can_unlock_tier_2_with_tier_1(self):
        assert can_unlock("resilience_2", ["resilience_1"], essence=60) is True

    def test_cannot_unlock_tier_3_without_tier_2(self):
        assert can_unlock("resilience_3", ["resilience_1"], essence=200) is False

    def test_cross_branch_no_dependency(self):
        # Unlocking insight_1 doesn't require resilience_1
        assert can_unlock("insight_1", [], essence=30) is True


class TestUnlockTalent:
    def test_unlock_returns_updated_state(self):
        unlocked, essence = unlock_talent("resilience_1", [], 100)
        assert "resilience_1" in unlocked
        assert essence == 70  # 100 - 30

    def test_unlock_preserves_existing(self):
        unlocked, essence = unlock_talent("resilience_2", ["resilience_1"], 100)
        assert "resilience_1" in unlocked
        assert "resilience_2" in unlocked
        assert essence == 40  # 100 - 60

    def test_unlock_raises_on_invalid(self):
        with pytest.raises(ValueError):
            unlock_talent("resilience_2", [], 200)  # Missing tier 1

    def test_unlock_raises_on_insufficient_essence(self):
        with pytest.raises(ValueError):
            unlock_talent("resilience_1", [], 5)


class TestGetActiveEffects:
    def test_no_talents(self):
        effects = get_active_effects([])
        assert effects["extra_starting_lives"] == 0
        assert effects["auto_stabilize"] is False
        assert effects["gold_bonus_pct"] == 0
        assert effects["pity_head_start"] == 0

    def test_resilience_1_adds_life(self):
        effects = get_active_effects(["resilience_1"])
        assert effects["extra_starting_lives"] == 1

    def test_fortune_branch_effects(self):
        effects = get_active_effects([
            "fortune_1", "fortune_2", "fortune_3", "fortune_4", "fortune_5",
        ])
        assert effects["gold_bonus_pct"] == 15
        assert effects["bonus_shards_per_floor"] == 1
        assert effects["shop_discount_pct"] == 10
        assert effects["bonus_consumable_chance"] == pytest.approx(0.10)
        assert effects["pity_head_start"] == 5

    def test_insight_branch_booleans(self):
        effects = get_active_effects(["insight_1", "insight_2"])
        assert effects["preview_difficulty"] is True
        assert effects["preview_vulnerability"] is True
        assert effects["preview_armillary_effect"] is False

    def test_mixed_branches(self):
        effects = get_active_effects(["resilience_1", "insight_1", "fortune_1"])
        assert effects["extra_starting_lives"] == 1
        assert effects["preview_difficulty"] is True
        assert effects["gold_bonus_pct"] == 15

    def test_unknown_talent_ignored(self):
        effects = get_active_effects(["nonexistent_talent"])
        assert effects["extra_starting_lives"] == 0


# ---- Essence ----

class TestComputeRunEssence:
    def test_floor_essence(self):
        assert compute_run_essence(floors_completed=5) == 50

    def test_boss_kills(self):
        assert compute_run_essence(boss_kills=2) == 50

    def test_achievements(self):
        assert compute_run_essence(achievements_earned=3) == 45

    def test_win_bonus(self):
        assert compute_run_essence(run_won=True) == 100

    def test_full_run(self):
        total = compute_run_essence(
            floors_completed=20, boss_kills=4, achievements_earned=2, run_won=True,
        )
        # 200 + 100 + 30 + 100 = 430
        assert total == 430

    def test_failed_run_no_win_bonus(self):
        total = compute_run_essence(floors_completed=5, run_won=False)
        assert total == 50

    def test_empty_run(self):
        assert compute_run_essence() == 0


class TestComputeAchievementEssence:
    def test_known_milestone(self):
        assert compute_achievement_essence("first_blood") == 10
        assert compute_achievement_essence("deathless_run") == 75

    def test_unknown_returns_zero(self):
        assert compute_achievement_essence("nonexistent") == 0


# ---- Achievements ----

class TestCheckAchievements:
    def test_first_blood(self):
        earned = check_achievements({"floors_completed": 1}, [])
        assert "first_blood" in earned

    def test_does_not_re_earn(self):
        earned = check_achievements({"floors_completed": 1}, ["first_blood"])
        assert "first_blood" not in earned

    def test_deathless_run(self):
        earned = check_achievements(
            {"run_won": True, "total_deaths": 0}, [],
        )
        assert "deathless_run" in earned

    def test_deathless_run_requires_win(self):
        earned = check_achievements(
            {"run_won": False, "total_deaths": 0}, [],
        )
        assert "deathless_run" not in earned

    def test_the_long_descent(self):
        earned = check_achievements({"floors_completed": 10}, [])
        assert "the_long_descent" in earned

    def test_armillarys_equal(self):
        earned = check_achievements({"run_won": True}, [])
        assert "armillarys_equal" in earned

    def test_tpk_survivor(self):
        earned = check_achievements({"tpk_saved": True}, [])
        assert "tpk_survivor" in earned

    def test_big_spender(self):
        earned = check_achievements({"gold_spent": 10000}, [])
        assert "big_spender" in earned

    def test_veteran(self):
        earned = check_achievements({"total_runs_completed": 5}, [])
        assert "veteran" in earned

    def test_multiple_achievements_at_once(self):
        earned = check_achievements(
            {"floors_completed": 20, "run_won": True, "total_deaths": 0}, [],
        )
        assert "first_blood" in earned
        assert "the_long_descent" in earned
        assert "armillarys_equal" in earned
        assert "deathless_run" in earned

    def test_all_achievements_have_definitions(self):
        for a in ACHIEVEMENTS:
            assert get_achievement(a.id) is not None
            assert a.essence_reward > 0


# ---- Lives System ----

class TestComputeStartingLives:
    def test_base_lives(self):
        assert compute_starting_lives([]) == BASE_STARTING_LIVES

    def test_resilience_1_adds_life(self):
        assert compute_starting_lives(["resilience_1"]) == 4

    def test_capped_at_max(self):
        # Even with extra talents, shouldn't exceed MAX_LIVES
        result = compute_starting_lives(["resilience_1"])
        assert result <= MAX_LIVES


class TestProcessCharacterDeath:
    def test_life_spent(self):
        result = process_character_death(lives_remaining=3, character_death_count=0)
        assert result.life_spent is True
        assert result.lives_remaining == 2
        assert result.permanently_dead is False
        assert result.scar is not None

    def test_last_life(self):
        result = process_character_death(lives_remaining=1, character_death_count=0)
        assert result.life_spent is True
        assert result.lives_remaining == 0
        assert result.permanently_dead is False

    def test_no_lives_permanent_death(self):
        result = process_character_death(lives_remaining=0, character_death_count=0)
        assert result.life_spent is False
        assert result.lives_remaining == 0
        assert result.permanently_dead is True
        assert result.scar is None


class TestProcessTPK:
    def test_tpk_ends_run(self):
        result = process_tpk(lives_remaining=2, meta_talents=[])
        assert result.run_over is True
        assert result.saved_by_phoenix is False
        assert result.lives_remaining == 0

    def test_phoenix_protocol_saves(self):
        result = process_tpk(
            lives_remaining=2, meta_talents=["resilience_5"],
        )
        assert result.run_over is False
        assert result.saved_by_phoenix is True
        assert result.lives_remaining == 1

    def test_phoenix_only_once(self):
        result = process_tpk(
            lives_remaining=1,
            meta_talents=["resilience_5"],
            phoenix_used_this_run=True,
        )
        assert result.run_over is True
        assert result.saved_by_phoenix is False

    def test_no_phoenix_without_talent(self):
        result = process_tpk(lives_remaining=3, meta_talents=["resilience_1"])
        assert result.run_over is True
        assert result.saved_by_phoenix is False


class TestCanResurrect:
    def test_can_resurrect_with_lives(self):
        assert can_resurrect(1) is True
        assert can_resurrect(3) is True

    def test_cannot_resurrect_no_lives(self):
        assert can_resurrect(0) is False


class TestAddLife:
    def test_adds_life(self):
        assert add_life(2) == 3

    def test_capped_at_max(self):
        assert add_life(MAX_LIVES) == MAX_LIVES
        assert add_life(MAX_LIVES - 1) == MAX_LIVES


# ---- Run Reset ----

class TestDecayPPC:
    def test_strong_ppc_decays_toward_one(self):
        result = decay_ppc_between_runs(1.3)
        assert result == pytest.approx(1.21, abs=0.001)

    def test_weak_ppc_decays_toward_one(self):
        result = decay_ppc_between_runs(0.7)
        assert result == pytest.approx(0.79, abs=0.001)

    def test_neutral_ppc_unchanged(self):
        assert decay_ppc_between_runs(1.0) == 1.0

    def test_extreme_strong_ppc(self):
        result = decay_ppc_between_runs(1.5)
        assert 1.0 < result < 1.5

    def test_extreme_weak_ppc(self):
        result = decay_ppc_between_runs(0.5)
        assert 0.5 < result < 1.0


class TestComputeRunStartState:
    def test_base_state(self):
        state = compute_run_start_state([])
        assert state["starting_lives"] == BASE_STARTING_LIVES
        assert state["effects"]["extra_starting_lives"] == 0
        assert state["talents_snapshot"] == []

    def test_with_talents(self):
        state = compute_run_start_state(["resilience_1", "fortune_1"])
        assert state["starting_lives"] == 4
        assert state["effects"]["extra_starting_lives"] == 1
        assert state["effects"]["gold_bonus_pct"] == 15
        assert "resilience_1" in state["talents_snapshot"]
        assert "fortune_1" in state["talents_snapshot"]


class TestResetCharacterForNewRun:
    def test_resets_run_fields(self):
        char = {
            "name": "Thorn",
            "class": "Fighter",
            "level": 12,
            "xp_total": 5000,
            "is_dead": True,
            "run_deaths": 3,
            "scars": ["A jagged scar"],
        }
        result = reset_character_for_new_run(char)
        assert result["level"] == 1
        assert result["xp_total"] == 0
        assert result["is_dead"] is False
        assert result["run_deaths"] == 0

    def test_preserves_identity(self):
        char = {
            "name": "Thorn",
            "class": "Fighter",
            "scars": ["A jagged scar"],
            "level": 10,
            "xp_total": 3000,
            "is_dead": False,
            "run_deaths": 0,
        }
        result = reset_character_for_new_run(char)
        assert result["name"] == "Thorn"
        assert result["class"] == "Fighter"
        assert result["scars"] == ["A jagged scar"]
