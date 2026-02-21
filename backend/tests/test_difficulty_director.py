"""Tests for the difficulty director (intensity curve + target computation)."""

from app.engine.difficulty.intensity_curve import (
    FLOOR_DIFFICULTY,
    IntensityPhase,
    compute_intensity_curve,
)
from app.engine.difficulty.target_computer import (
    DifficultyTarget,
    compute_difficulty_target,
)


class TestFloorDifficulty:
    def test_floor_1_is_easiest(self):
        assert FLOOR_DIFFICULTY[1] < FLOOR_DIFFICULTY[20]

    def test_floor_20_is_max(self):
        assert FLOOR_DIFFICULTY[20] == 1.0

    def test_all_floors_present(self):
        for floor in range(1, 21):
            assert floor in FLOOR_DIFFICULTY

    def test_tier_resets_exist(self):
        # Floor 11 resets slightly from floor 10 (tier 2→3 transition)
        assert FLOOR_DIFFICULTY[11] < FLOOR_DIFFICULTY[10]
        # Floor 17 resets slightly from floor 16 (tier 3→4 transition)
        assert FLOOR_DIFFICULTY[17] < FLOOR_DIFFICULTY[16]


class TestIntensityCurve:
    def test_basic_curve(self):
        result = compute_intensity_curve(
            arena_number=1, total_arenas=3,
            floor_number=1, party_power_coefficient=1.0,
        )
        assert result.intensity > 0
        assert result.intensity <= 1.0
        assert isinstance(result.phase, IntensityPhase)

    def test_intensity_increases_with_arena(self):
        i1 = compute_intensity_curve(
            arena_number=1, total_arenas=4,
            floor_number=5, party_power_coefficient=1.0,
        )
        i4 = compute_intensity_curve(
            arena_number=4, total_arenas=4,
            floor_number=5, party_power_coefficient=1.0,
        )
        # The last arena should have higher perceived intensity
        # (even if raw budget is adjusted for attrition)
        assert i4.intensity >= i1.intensity

    def test_intensity_increases_with_floor(self):
        i_early = compute_intensity_curve(
            arena_number=1, total_arenas=3,
            floor_number=1, party_power_coefficient=1.0,
        )
        i_late = compute_intensity_curve(
            arena_number=1, total_arenas=3,
            floor_number=10, party_power_coefficient=1.0,
        )
        assert i_late.intensity > i_early.intensity

    def test_ppc_affects_intensity(self):
        i_normal = compute_intensity_curve(
            arena_number=2, total_arenas=4,
            floor_number=5, party_power_coefficient=1.0,
        )
        i_strong = compute_intensity_curve(
            arena_number=2, total_arenas=4,
            floor_number=5, party_power_coefficient=1.3,
        )
        # Strong PPC should increase intensity
        assert i_strong.intensity >= i_normal.intensity

    def test_phase_assignment(self):
        # First arena of 4 should be warmup or escalation
        result = compute_intensity_curve(
            arena_number=1, total_arenas=4,
            floor_number=5, party_power_coefficient=1.0,
        )
        assert result.phase in (IntensityPhase.WARMUP, IntensityPhase.ESCALATION)


class TestDifficultyTarget:
    def test_base_intensity_only(self):
        target = compute_difficulty_target(base_intensity=0.7)
        assert isinstance(target, DifficultyTarget)
        assert target.base_intensity == 0.7
        assert target.adjusted_intensity > 0
        assert target.difficulty in ("moderate", "high")
        assert target.xp_multiplier > 0

    def test_tpk_reduces_difficulty(self):
        base = compute_difficulty_target(base_intensity=0.8)
        tpk = compute_difficulty_target(
            base_intensity=0.8, previous_floor_tpk=True,
        )
        assert tpk.adjusted_intensity < base.adjusted_intensity

    def test_low_hp_reduces_difficulty(self):
        base = compute_difficulty_target(base_intensity=0.8)
        hurt = compute_difficulty_target(
            base_intensity=0.8, previous_floor_avg_hp=0.20,
        )
        assert hurt.adjusted_intensity < base.adjusted_intensity

    def test_healthy_party_slight_increase(self):
        base = compute_difficulty_target(base_intensity=0.7)
        healthy = compute_difficulty_target(
            base_intensity=0.7, previous_floor_avg_hp=0.95,
        )
        assert healthy.adjusted_intensity >= base.adjusted_intensity

    def test_deaths_reduce_difficulty(self):
        base = compute_difficulty_target(base_intensity=0.8)
        deaths = compute_difficulty_target(
            base_intensity=0.8, previous_floor_deaths=2,
        )
        assert deaths.adjusted_intensity < base.adjusted_intensity

    def test_strong_ppc_increases_difficulty(self):
        base = compute_difficulty_target(base_intensity=0.7)
        strong = compute_difficulty_target(
            base_intensity=0.7, party_power_coefficient=1.3,
        )
        assert strong.adjusted_intensity > base.adjusted_intensity

    def test_weak_ppc_reduces_difficulty(self):
        base = compute_difficulty_target(base_intensity=0.8)
        weak = compute_difficulty_target(
            base_intensity=0.8, party_power_coefficient=0.6,
        )
        assert weak.adjusted_intensity < base.adjusted_intensity

    def test_dm_assessment_dire_reduces(self):
        base = compute_difficulty_target(base_intensity=0.8)
        dire = compute_difficulty_target(
            base_intensity=0.8, dm_assessment="dire",
        )
        assert dire.adjusted_intensity < base.adjusted_intensity

    def test_intensity_clamped(self):
        # Even with all reductions, shouldn't go below 0.35
        target = compute_difficulty_target(
            base_intensity=0.5,
            previous_floor_tpk=True,
            previous_floor_deaths=3,
            dm_assessment="dire",
            party_power_coefficient=0.5,
        )
        assert target.adjusted_intensity >= 0.35

    def test_notes_populated(self):
        target = compute_difficulty_target(
            base_intensity=0.8,
            previous_floor_deaths=2,
            dm_assessment="critical",
        )
        assert len(target.notes) > 0

    def test_xp_multiplier_capped(self):
        target = compute_difficulty_target(
            base_intensity=1.0,
            party_power_coefficient=1.5,
            previous_floor_avg_hp=1.0,
        )
        assert target.xp_multiplier <= 1.15
