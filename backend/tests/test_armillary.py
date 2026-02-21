"""Tests for the Armillary system (roller, weight adjuster, budget, scaling)."""

from app.engine.armillary.budget_tracker import (
    BudgetState,
    can_afford_effect,
    compute_armillary_budget,
    downgrade_severity,
    get_budget_state,
)
from app.engine.armillary.roller import (
    DEFAULT_CATEGORY_WEIGHTS,
    ArmillaryRollResult,
    reroll_armillary_effect,
    roll_armillary_effect,
)
from app.engine.armillary.scaling import (
    apply_scaling_to_weights,
    get_armillary_scaling,
)
from app.engine.armillary.weight_adjuster import adjust_weights


class TestRollArmillaryEffect:
    def test_returns_roll_result(self):
        result = roll_armillary_effect(round_number=1)
        assert isinstance(result, ArmillaryRollResult)
        assert result.effect is not None
        assert result.was_rerolled is False

    def test_round_filtering(self):
        # Round 1 should only return effects with min_round <= 1
        for _ in range(20):
            result = roll_armillary_effect(round_number=1)
            assert result.effect.min_round <= 1

    def test_custom_weights(self):
        # Heavily weighted toward beneficial — statistical test
        weights = {"hostile": 1, "beneficial": 98, "environmental": 0, "wild": 1}
        categories = set()
        for _ in range(50):
            result = roll_armillary_effect(round_number=5, category_weights=weights)
            categories.add(result.effect.category)
        # With 98% beneficial, we should see it at least once
        assert "beneficial" in categories

    def test_recent_effects_reduces_repeat(self):
        # Get an initial roll, then mark it as recent
        first = roll_armillary_effect(round_number=5)
        key = first.effect.key
        # Roll many times with the key marked as recent
        different_count = 0
        for _ in range(30):
            result = roll_armillary_effect(round_number=5, recent_effect_keys=[key])
            if result.effect.key != key:
                different_count += 1
        # With 0.3x weight on the recent key, most should be different
        assert different_count > 0


class TestRerollArmillaryEffect:
    def test_reroll_marks_was_rerolled(self):
        first = roll_armillary_effect(round_number=3)
        result = reroll_armillary_effect(
            current_effect_key=first.effect.key, round_number=3
        )
        assert result.was_rerolled is True

    def test_reroll_excludes_current(self):
        first = roll_armillary_effect(round_number=3)
        different = False
        for _ in range(20):
            result = reroll_armillary_effect(
                current_effect_key=first.effect.key, round_number=3
            )
            if result.effect.key != first.effect.key:
                different = True
                break
        # It's possible but very unlikely to get the same effect 20 times
        # when its weight is reduced to 0.3x
        assert different


class TestAdjustWeights:
    def test_neutral_hp_no_adjustment(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        # 0.7 HP is in the neutral band (not < 0.5, not > 0.8)
        result = adjust_weights(base, average_hp_percentage=0.7)
        # Floor 1, arena 1, neutral HP: no HP-based adjustments
        assert result["hostile"] == base["hostile"]
        assert result["beneficial"] == base["beneficial"]

    def test_critical_hp_favors_beneficial(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(base, average_hp_percentage=0.2)
        assert result["hostile"] < base["hostile"]
        assert result["beneficial"] > base["beneficial"]

    def test_low_hp_slight_beneficial(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(base, average_hp_percentage=0.4)
        assert result["hostile"] < base["hostile"]
        assert result["beneficial"] > base["beneficial"]

    def test_high_hp_increases_hostile(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(base, average_hp_percentage=0.9)
        assert result["hostile"] > base["hostile"]

    def test_death_eases_up(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(base, any_dead=True)
        assert result["hostile"] < base["hostile"]
        assert result["beneficial"] > base["beneficial"]

    def test_high_stress_reduces_hostile(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(base, cumulative_stress=0.8)
        assert result["hostile"] < base["hostile"]

    def test_deeper_floors_more_hostile(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        r1 = adjust_weights(base, floor_number=1)
        r10 = adjust_weights(base, floor_number=10)
        assert r10["hostile"] > r1["hostile"]

    def test_later_arenas_more_hostile(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        r1 = adjust_weights(base, arena_number=1)
        r5 = adjust_weights(base, arena_number=5)
        assert r5["hostile"] > r1["hostile"]

    def test_weak_ppc_reduces_hostile(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(base, party_power_coefficient=0.7)
        assert result["hostile"] < base["hostile"]

    def test_strong_ppc_increases_hostile(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(base, party_power_coefficient=1.3)
        assert result["hostile"] > base["hostile"]

    def test_weights_never_below_minimum(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        result = adjust_weights(
            base,
            average_hp_percentage=0.1,
            any_dead=True,
            cumulative_stress=1.0,
            party_power_coefficient=0.5,
        )
        for key in result:
            assert result[key] >= 5

    def test_does_not_mutate_input(self):
        base = dict(DEFAULT_CATEGORY_WEIGHTS)
        original = dict(base)
        adjust_weights(base, average_hp_percentage=0.2, any_dead=True)
        assert base == original


class TestBudgetTracker:
    def test_compute_budget(self):
        assert compute_armillary_budget(1000) == 200
        assert compute_armillary_budget(500) == 100
        assert compute_armillary_budget(0) == 0

    def test_budget_state_fresh(self):
        state = get_budget_state(200, [])
        assert state.total_budget == 200
        assert state.spent == 0
        assert state.remaining == 200
        assert state.is_exhausted is False
        assert state.can_use_hostile is True

    def test_budget_state_partially_spent(self):
        effects = [{"xp_cost": 50}, {"xp_cost": 30}]
        state = get_budget_state(200, effects)
        assert state.spent == 80
        assert state.remaining == 120
        assert state.is_exhausted is False

    def test_budget_state_exhausted(self):
        effects = [{"xp_cost": 100}, {"xp_cost": 100}]
        state = get_budget_state(200, effects)
        assert state.spent == 200
        assert state.remaining == 0
        assert state.is_exhausted is True
        assert state.can_use_hostile is False

    def test_overridden_effects_not_counted(self):
        effects = [
            {"xp_cost": 100, "was_overridden": True},
            {"xp_cost": 50},
        ]
        state = get_budget_state(200, effects)
        assert state.spent == 50

    def test_can_afford_free_effect(self):
        state = BudgetState(
            total_budget=200, spent=200, remaining=0,
            is_exhausted=True, can_use_hostile=False,
        )
        assert can_afford_effect(state, 0) is True

    def test_can_afford_with_budget(self):
        state = BudgetState(
            total_budget=200, spent=100, remaining=100,
            is_exhausted=False, can_use_hostile=True,
        )
        assert can_afford_effect(state, 50) is True
        assert can_afford_effect(state, 100) is True
        assert can_afford_effect(state, 101) is False

    def test_downgrade_severity_exhausted(self):
        assert downgrade_severity(3, 0) == 1

    def test_downgrade_severity_low_budget(self):
        assert downgrade_severity(3, 20) == 2
        assert downgrade_severity(2, 20) == 1

    def test_downgrade_severity_sufficient_budget(self):
        assert downgrade_severity(3, 100) == 3
        assert downgrade_severity(1, 100) == 1


class TestArmillaryScaling:
    def test_floor_1_base(self):
        s = get_armillary_scaling(1)
        assert s.hostile_weight_bonus == 0
        assert s.max_severity == 2
        assert s.wild_weight_bonus == 0
        assert s.favour_earned_on_clear == 1

    def test_floor_3_unlocks_severity_3(self):
        s = get_armillary_scaling(3)
        assert s.max_severity == 3
        assert s.favour_earned_on_clear == 2

    def test_floor_4_adds_wild_bonus(self):
        s = get_armillary_scaling(4)
        assert s.wild_weight_bonus == 5
        assert s.hostile_weight_bonus == 15

    def test_hostile_bonus_capped_at_15(self):
        s = get_armillary_scaling(10)
        assert s.hostile_weight_bonus == 15

    def test_apply_scaling_to_weights(self):
        base = {"hostile": 40, "beneficial": 20, "environmental": 25, "wild": 15}
        scaling = get_armillary_scaling(4)
        result = apply_scaling_to_weights(base, scaling)
        assert result["hostile"] == 40 + 15
        assert result["wild"] == 15 + 5
        # Unchanged categories
        assert result["beneficial"] == 20
        assert result["environmental"] == 25
