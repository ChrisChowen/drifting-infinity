"""Talent tree: Armillary Attunement.

Three branches of 5 tiers each. Nodes unlock in order within a branch.
Effects expand options and resilience — never raw combat power — so early
content stays challenging regardless of how many talents are unlocked.
"""

from dataclasses import dataclass


@dataclass
class TalentDef:
    id: str
    name: str
    branch: str          # "resilience", "insight", "fortune"
    tier: int            # 1-5
    cost: int            # Essence cost
    effect_key: str      # Machine-readable effect identifier
    description: str     # Player-facing description


# ---------------------------------------------------------------------------
# Talent catalogue
# ---------------------------------------------------------------------------

TALENT_TREE: list[TalentDef] = [
    # === RESILIENCE ===
    TalentDef(
        id="resilience_1",
        name="Second Wind",
        branch="resilience",
        tier=1,
        cost=30,
        effect_key="extra_starting_life",
        description="+1 starting life per run (4 total).",
    ),
    TalentDef(
        id="resilience_2",
        name="Death's Door",
        branch="resilience",
        tier=2,
        cost=60,
        effect_key="auto_stabilize",
        description="Characters at 0 HP stabilize automatically once per floor.",
    ),
    TalentDef(
        id="resilience_3",
        name="Armillary's Mercy",
        branch="resilience",
        tier=3,
        cost=100,
        effect_key="improved_revive_hp",
        description="Dead characters resurrect at 50% HP instead of 1 HP on floor clear.",
    ),
    TalentDef(
        id="resilience_4",
        name="Undying Will",
        branch="resilience",
        tier=4,
        cost=150,
        effect_key="final_stand_saves",
        description="Final Stand grants one more round of death saves instead of instant death.",
    ),
    TalentDef(
        id="resilience_5",
        name="Phoenix Protocol",
        branch="resilience",
        tier=5,
        cost=250,
        effect_key="tpk_save",
        description="Once per run, a TPK instead reduces to 1 life and resurrects the party at 1 HP.",
    ),
    # === INSIGHT ===
    TalentDef(
        id="insight_1",
        name="Arena Mapping",
        branch="insight",
        tier=1,
        cost=30,
        effect_key="preview_difficulty",
        description="See encounter difficulty tier before entering.",
    ),
    TalentDef(
        id="insight_2",
        name="Creature Lore",
        branch="insight",
        tier=2,
        cost=60,
        effect_key="preview_vulnerability",
        description="See one vulnerability per creature in the encounter preview.",
    ),
    TalentDef(
        id="insight_3",
        name="Arbiter's Whisper",
        branch="insight",
        tier=3,
        cost=100,
        effect_key="preview_armillary_effect",
        description="Once per floor, preview the Armillary's next effect before it triggers.",
    ),
    TalentDef(
        id="insight_4",
        name="Tactical Foresight",
        branch="insight",
        tier=4,
        cost=150,
        effect_key="choose_template",
        description="Once per floor, choose between 2 encounter templates instead of random.",
    ),
    TalentDef(
        id="insight_5",
        name="Armillary Interference",
        branch="insight",
        tier=5,
        cost=250,
        effect_key="cancel_hostile_effect",
        description="Once per run, cancel an Armillary hostile effect entirely.",
    ),
    # === FORTUNE ===
    TalentDef(
        id="fortune_1",
        name="Prospector",
        branch="fortune",
        tier=1,
        cost=30,
        effect_key="gold_bonus",
        description="+15% gold from all sources.",
    ),
    TalentDef(
        id="fortune_2",
        name="Shard Resonance",
        branch="fortune",
        tier=2,
        cost=60,
        effect_key="bonus_shards",
        description="+1 Astral Shard per floor clear.",
    ),
    TalentDef(
        id="fortune_3",
        name="Merchant's Friend",
        branch="fortune",
        tier=3,
        cost=100,
        effect_key="shop_discount",
        description="Shop prices reduced 10% permanently.",
    ),
    TalentDef(
        id="fortune_4",
        name="Lucky Find",
        branch="fortune",
        tier=4,
        cost=150,
        effect_key="bonus_consumable_chance",
        description="10% chance per arena for bonus consumable drop.",
    ),
    TalentDef(
        id="fortune_5",
        name="Vault Attunement",
        branch="fortune",
        tier=5,
        cost=250,
        effect_key="pity_head_start",
        description="Gacha pity counter starts at 5 instead of 0.",
    ),
]


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

_TALENT_INDEX: dict[str, TalentDef] = {t.id: t for t in TALENT_TREE}
_BRANCH_TALENTS: dict[str, list[TalentDef]] = {}
for _t in TALENT_TREE:
    _BRANCH_TALENTS.setdefault(_t.branch, []).append(_t)
for _branch in _BRANCH_TALENTS:
    _BRANCH_TALENTS[_branch].sort(key=lambda t: t.tier)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_talent(talent_id: str) -> TalentDef | None:
    """Return a talent definition by id."""
    return _TALENT_INDEX.get(talent_id)


def get_branch(branch: str) -> list[TalentDef]:
    """Return all talents in a branch, sorted by tier."""
    return list(_BRANCH_TALENTS.get(branch, []))


def can_unlock(talent_id: str, unlocked: list[str], essence: int) -> bool:
    """Check whether a talent can be unlocked.

    Requirements:
    - Talent exists and is not already unlocked
    - All lower tiers in the same branch are unlocked
    - Player has enough essence
    """
    talent = _TALENT_INDEX.get(talent_id)
    if not talent or talent_id in unlocked:
        return False
    if talent.cost > essence:
        return False
    # Check prerequisites: all lower tiers in the branch must be unlocked
    for t in _BRANCH_TALENTS.get(talent.branch, []):
        if t.tier < talent.tier and t.id not in unlocked:
            return False
    return True


def unlock_talent(
    talent_id: str,
    unlocked: list[str],
    essence: int,
) -> tuple[list[str], int]:
    """Unlock a talent, returning updated unlocked list and remaining essence.

    Raises ValueError if prerequisites or cost are not met.
    """
    if not can_unlock(talent_id, unlocked, essence):
        raise ValueError(f"Cannot unlock {talent_id}: prerequisites or cost not met")
    talent = _TALENT_INDEX[talent_id]
    return unlocked + [talent_id], essence - talent.cost


def get_active_effects(unlocked: list[str]) -> dict:
    """Compute the aggregate effect dict from all unlocked talents.

    Returns a dict mapping effect_key → value.  Numeric bonuses are summed;
    boolean flags are True if any talent enables them.
    """
    effects: dict = {
        # Resilience
        "extra_starting_lives": 0,
        "auto_stabilize": False,
        "improved_revive_hp": False,
        "final_stand_saves": False,
        "tpk_save": False,
        # Insight
        "preview_difficulty": False,
        "preview_vulnerability": False,
        "preview_armillary_effect": False,
        "choose_template": False,
        "cancel_hostile_effect": False,
        # Fortune
        "gold_bonus_pct": 0,
        "bonus_shards_per_floor": 0,
        "shop_discount_pct": 0,
        "bonus_consumable_chance": 0.0,
        "pity_head_start": 0,
    }

    for tid in unlocked:
        talent = _TALENT_INDEX.get(tid)
        if not talent:
            continue
        match talent.effect_key:
            # Resilience
            case "extra_starting_life":
                effects["extra_starting_lives"] += 1
            case "auto_stabilize":
                effects["auto_stabilize"] = True
            case "improved_revive_hp":
                effects["improved_revive_hp"] = True
            case "final_stand_saves":
                effects["final_stand_saves"] = True
            case "tpk_save":
                effects["tpk_save"] = True
            # Insight
            case "preview_difficulty":
                effects["preview_difficulty"] = True
            case "preview_vulnerability":
                effects["preview_vulnerability"] = True
            case "preview_armillary_effect":
                effects["preview_armillary_effect"] = True
            case "choose_template":
                effects["choose_template"] = True
            case "cancel_hostile_effect":
                effects["cancel_hostile_effect"] = True
            # Fortune
            case "gold_bonus":
                effects["gold_bonus_pct"] += 15
            case "bonus_shards":
                effects["bonus_shards_per_floor"] += 1
            case "shop_discount":
                effects["shop_discount_pct"] += 10
            case "bonus_consumable_chance":
                effects["bonus_consumable_chance"] += 0.10
            case "pity_head_start":
                effects["pity_head_start"] += 5

    return effects
