"""Dice rolling utilities. Parses NdM+B notation and rolls dice."""

import random
import re
from dataclasses import dataclass

DICE_PATTERN = re.compile(r"(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?")


@dataclass
class DiceResult:
    total: int
    rolls: list[int]
    bonus: int
    notation: str
    is_crit: bool = False

    @property
    def breakdown(self) -> str:
        roll_str = " + ".join(str(r) for r in self.rolls)
        if self.bonus > 0:
            return f"({roll_str}) + {self.bonus} = {self.total}"
        elif self.bonus < 0:
            return f"({roll_str}) - {abs(self.bonus)} = {self.total}"
        return f"({roll_str}) = {self.total}"


def parse_dice(notation: str) -> tuple[int, int, int]:
    """Parse dice notation like '2d8+3' into (count, sides, bonus)."""
    match = DICE_PATTERN.match(notation.strip())
    if not match:
        raise ValueError(f"Invalid dice notation: {notation}")

    count = int(match.group(1))
    sides = int(match.group(2))
    sign = match.group(3) or "+"
    bonus_val = int(match.group(4)) if match.group(4) else 0
    bonus = bonus_val if sign == "+" else -bonus_val

    return count, sides, bonus


def roll_dice(notation: str, crit: bool = False) -> DiceResult:
    """Roll dice from notation string. If crit, double the dice count."""
    count, sides, bonus = parse_dice(notation)

    if crit:
        count *= 2

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + bonus

    return DiceResult(
        total=max(0, total),
        rolls=rolls,
        bonus=bonus,
        notation=notation,
        is_crit=crit,
    )


def roll_d20(modifier: int = 0) -> tuple[int, int]:
    """Roll a d20 with modifier. Returns (total, natural_roll)."""
    natural = random.randint(1, 20)
    return natural + modifier, natural


def average_dice(notation: str) -> float:
    """Calculate the average result for a dice notation."""
    count, sides, bonus = parse_dice(notation)
    return count * (sides + 1) / 2 + bonus
