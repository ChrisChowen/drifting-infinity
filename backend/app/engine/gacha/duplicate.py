"""Duplicate protection for gacha per GDD 7.3."""

from dataclasses import dataclass


@dataclass
class DuplicateResult:
    is_duplicate: bool
    refund_shards: int
    refund_gold: int
    enhancement_materials: int


# Duplicate refund rates by rarity
DUPLICATE_REFUNDS: dict[str, dict[str, int]] = {
    "common": {"shards": 1, "gold": 25, "materials": 0},
    "uncommon": {"shards": 1, "gold": 50, "materials": 1},
    "rare": {"shards": 2, "gold": 100, "materials": 2},
    "very_rare": {"shards": 3, "gold": 200, "materials": 3},
    "legendary": {"shards": 3, "gold": 500, "materials": 5},
}


def check_duplicate(
    item_id: str,
    owned_item_ids: set[str],
) -> bool:
    """Check if the pulled item is a duplicate."""
    return item_id in owned_item_ids


def compute_duplicate_refund(rarity: str) -> DuplicateResult:
    """Compute refund for a duplicate pull."""
    refund = DUPLICATE_REFUNDS.get(rarity, DUPLICATE_REFUNDS["common"])
    return DuplicateResult(
        is_duplicate=True,
        refund_shards=refund["shards"],
        refund_gold=refund["gold"],
        enhancement_materials=refund["materials"],
    )
