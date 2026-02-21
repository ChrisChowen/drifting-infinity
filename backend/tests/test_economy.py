"""Tests for the gold economy engine."""

from app.engine.economy.gold import (
    LEVEL_MULTIPLIERS,
    MILESTONE_BONUSES,
    compute_arena_gold,
    compute_milestone_gold,
    compute_participation_gold,
    compute_run_completion_gold,
    compute_total_run_gold,
)


class TestLevelMultipliers:
    def test_tier_1_multiplier(self):
        for lvl in range(1, 5):
            assert LEVEL_MULTIPLIERS[lvl] == 1

    def test_tier_2_multiplier(self):
        for lvl in range(5, 11):
            assert LEVEL_MULTIPLIERS[lvl] == 2

    def test_tier_3_multiplier(self):
        for lvl in range(11, 17):
            assert LEVEL_MULTIPLIERS[lvl] == 4

    def test_tier_4_multiplier(self):
        for lvl in range(17, 21):
            assert LEVEL_MULTIPLIERS[lvl] == 8

    def test_all_levels_covered(self):
        for lvl in range(1, 21):
            assert lvl in LEVEL_MULTIPLIERS


class TestComputeArenaGold:
    def test_first_arena_level_1(self):
        gold = compute_arena_gold(1, 1)
        # base: 5*1=5, multiplier 1, bonus: 30*1=30 → 35
        assert gold == 35

    def test_scales_with_arena_number(self):
        gold_1 = compute_arena_gold(1, 1)
        gold_3 = compute_arena_gold(3, 1)
        assert gold_3 > gold_1

    def test_scales_with_party_level(self):
        gold_low = compute_arena_gold(1, 1)
        gold_high = compute_arena_gold(1, 5)
        assert gold_high > gold_low

    def test_high_difficulty_treasure_hoard(self):
        gold_mod = compute_arena_gold(3, 5, "moderate")
        gold_high = compute_arena_gold(3, 5, "high")
        assert gold_high > gold_mod
        assert gold_high == int(gold_mod * 1.5)

    def test_moderate_difficulty_default(self):
        gold = compute_arena_gold(1, 1)
        gold_explicit = compute_arena_gold(1, 1, "moderate")
        assert gold == gold_explicit

    def test_unknown_level_uses_default_multiplier(self):
        gold = compute_arena_gold(1, 25)
        assert gold > 0


class TestMilestoneGold:
    def test_floor_1_milestone(self):
        gold = compute_milestone_gold(1, 1)
        assert gold == 50

    def test_floor_20_milestone(self):
        gold = compute_milestone_gold(20, 1)
        assert gold == 8000

    def test_scales_with_level(self):
        gold_low = compute_milestone_gold(5, 1)
        gold_high = compute_milestone_gold(5, 5)
        assert gold_high == gold_low * 2  # tier2 multiplier is 2x

    def test_all_floors_have_milestones(self):
        for floor in range(1, 21):
            assert floor in MILESTONE_BONUSES

    def test_milestones_increase(self):
        prev = 0
        for floor in range(1, 21):
            bonus = MILESTONE_BONUSES[floor]
            assert bonus > prev, f"Floor {floor} bonus {bonus} <= {prev}"
            prev = bonus

    def test_unknown_floor_returns_zero(self):
        assert compute_milestone_gold(25, 1) == 0


class TestParticipationGold:
    def test_basic_participation(self):
        gold = compute_participation_gold(5, 1)
        assert gold == 250  # 5 * 50 * 1

    def test_scales_with_level(self):
        gold_low = compute_participation_gold(5, 1)
        gold_high = compute_participation_gold(5, 5)
        assert gold_high == gold_low * 2


class TestRunCompletionGold:
    def test_basic_completion(self):
        gold = compute_run_completion_gold(1)
        assert gold == 150

    def test_scales_with_level(self):
        gold_low = compute_run_completion_gold(1)
        gold_high = compute_run_completion_gold(17)
        assert gold_high == gold_low * 8


class TestTotalRunGold:
    def test_includes_arena_gold(self):
        total = compute_total_run_gold(
            arenas_cleared_per_floor=[3],
            floors_completed=[1],
            party_level=1,
            run_completed=False,
        )
        assert total > 0

    def test_completion_bonus_adds(self):
        total_incomplete = compute_total_run_gold(
            arenas_cleared_per_floor=[3],
            floors_completed=[1],
            party_level=1,
            run_completed=False,
        )
        total_complete = compute_total_run_gold(
            arenas_cleared_per_floor=[3],
            floors_completed=[1],
            party_level=1,
            run_completed=True,
        )
        assert total_complete > total_incomplete

    def test_uses_higher_of_arena_or_participation(self):
        # With very few arenas, participation floor should be used
        total = compute_total_run_gold(
            arenas_cleared_per_floor=[1],
            floors_completed=[],
            party_level=1,
            run_completed=False,
        )
        assert total > 0
