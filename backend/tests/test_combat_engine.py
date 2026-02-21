"""Tests for the combat engine subsystems."""

from app.engine.combat.weakness_exploit import (
    CHAIN_BONUS_DAMAGE,
    CHAIN_THRESHOLD,
    WeaknessExploitState,
    check_vulnerability_exploit,
    check_weak_save_exploit,
    new_round,
    trigger_exploit,
)


class TestCheckVulnerabilityExploit:
    def test_matching_vulnerability(self):
        assert check_vulnerability_exploit("fire", ["fire", "cold"]) is True

    def test_no_matching_vulnerability(self):
        assert check_vulnerability_exploit("thunder", ["fire", "cold"]) is False

    def test_case_insensitive(self):
        assert check_vulnerability_exploit("Fire", ["fire"]) is True

    def test_empty_vulnerabilities(self):
        assert check_vulnerability_exploit("fire", []) is False


class TestCheckWeakSaveExploit:
    def test_matching_weak_save(self):
        assert check_weak_save_exploit("DEX", ["DEX", "CHA"]) is True

    def test_no_matching_save(self):
        assert check_weak_save_exploit("CON", ["DEX", "CHA"]) is False

    def test_case_insensitive(self):
        assert check_weak_save_exploit("dex", ["DEX"]) is True


class TestTriggerExploit:
    def test_successful_exploit(self):
        state = WeaknessExploitState()
        state, trigger = trigger_exploit(
            state, "Fighter", "goblin_1", "vulnerability", "fire"
        )
        assert trigger is not None
        assert trigger.character_name == "Fighter"
        assert state.exploits_this_round == 1

    def test_exploit_cap_per_round(self):
        state = WeaknessExploitState()
        # First two should succeed
        state, t1 = trigger_exploit(state, "A", "g1", "vulnerability", "fire")
        state, t2 = trigger_exploit(state, "B", "g2", "vulnerability", "cold")
        assert t1 is not None
        assert t2 is not None
        # Third should fail (cap is 2)
        state, t3 = trigger_exploit(state, "C", "g3", "vulnerability", "thunder")
        assert t3 is None
        assert state.exploits_this_round == 2

    def test_chain_bonus_activates(self):
        state = WeaknessExploitState()
        for i in range(CHAIN_THRESHOLD):
            state.exploits_this_round = 0  # Reset per-round cap
            state, _ = trigger_exploit(state, f"P{i}", f"c{i}", "vulnerability", "fire")
        assert state.chain_bonus_active is True
        assert state.chain_bonus_damage == CHAIN_BONUS_DAMAGE

    def test_chain_bonus_requires_threshold(self):
        state = WeaknessExploitState()
        state, _ = trigger_exploit(state, "A", "c1", "vulnerability", "fire")
        assert state.chain_bonus_active is False

    def test_trigger_tracks_chain_position(self):
        state = WeaknessExploitState()
        state, t1 = trigger_exploit(state, "A", "c1", "vulnerability", "fire")
        assert t1.chain_position == 1
        state.exploits_this_round = 0
        state, t2 = trigger_exploit(state, "B", "c2", "vulnerability", "cold")
        assert t2.chain_position == 2


class TestNewRound:
    def test_resets_per_round_counter(self):
        state = WeaknessExploitState(exploits_this_round=2)
        state = new_round(state)
        assert state.exploits_this_round == 0

    def test_preserves_chain_count(self):
        state = WeaknessExploitState(chain_count=3)
        state = new_round(state)
        assert state.chain_count == 3
