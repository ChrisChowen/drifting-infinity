"""Tests for the leveling engine."""

from app.engine.leveling import (
    XP_TO_LEVEL,
    check_level_up,
    compute_arena_xp_award,
    compute_power_xp_bonus,
    compute_xp_progress,
    xp_to_next_level,
)


class TestXpToNextLevel:
    def test_level_1_threshold(self):
        assert xp_to_next_level(1) == 75

    def test_level_5_threshold(self):
        assert xp_to_next_level(5) == 1800

    def test_level_20_max(self):
        assert xp_to_next_level(20) == 0

    def test_all_levels_have_thresholds(self):
        for level in range(1, 21):
            assert level in XP_TO_LEVEL

    def test_thresholds_increase_monotonically(self):
        prev = 0
        for level in range(1, 20):
            threshold = xp_to_next_level(level)
            assert threshold > prev, f"Level {level} threshold {threshold} <= {prev}"
            prev = threshold

    def test_unknown_level_returns_zero(self):
        assert xp_to_next_level(25) == 0


class TestCheckLevelUp:
    def test_can_level_up(self):
        assert check_level_up(1, 75) is True

    def test_cannot_level_up_insufficient_xp(self):
        assert check_level_up(1, 50) is False

    def test_max_level_cannot_level(self):
        assert check_level_up(20, 999999) is False

    def test_exact_threshold(self):
        assert check_level_up(3, 350) is True

    def test_one_below_threshold(self):
        assert check_level_up(3, 349) is False


class TestComputeArenaXpAward:
    def test_basic_award(self):
        result = compute_arena_xp_award(400, 4)
        assert result == 100  # 400 / 4

    def test_zero_party_size(self):
        assert compute_arena_xp_award(400, 0) == 0

    def test_minimum_one_xp(self):
        result = compute_arena_xp_award(1, 4)
        assert result >= 1

    def test_leveling_speed_multiplier(self):
        base = compute_arena_xp_award(400, 4, leveling_speed=1.0)
        fast = compute_arena_xp_award(400, 4, leveling_speed=1.5)
        assert fast > base

    def test_slow_leveling_speed(self):
        base = compute_arena_xp_award(400, 4, leveling_speed=1.0)
        slow = compute_arena_xp_award(400, 4, leveling_speed=0.7)
        assert slow < base


class TestComputePowerXpBonus:
    def test_base_bonus(self):
        assert compute_power_xp_bonus() == 1.0

    def test_gacha_items_bonus(self):
        result = compute_power_xp_bonus(gacha_items_owned=5)
        assert result == 1.25  # 1.0 + 5 * 0.05

    def test_floor_bonus(self):
        result = compute_power_xp_bonus(floors_completed=10)
        assert result == 1.2  # 1.0 + 10 * 0.02

    def test_cap_at_1_5(self):
        result = compute_power_xp_bonus(gacha_items_owned=20, floors_completed=50)
        assert result == 1.5


class TestComputeXpProgress:
    def test_no_xp(self):
        progress = compute_xp_progress(1, 0)
        assert progress["percentage"] == 0.0
        assert progress["can_level_up"] is False

    def test_halfway(self):
        # Level 1 requires 75 XP; 37 XP is about halfway
        progress = compute_xp_progress(1, 37)
        assert progress["percentage"] == 49.3

    def test_max_level(self):
        progress = compute_xp_progress(20, 100000)
        assert progress["percentage"] == 100.0
        assert progress["can_level_up"] is False

    def test_ready_to_level(self):
        progress = compute_xp_progress(1, 75)
        assert progress["can_level_up"] is True
