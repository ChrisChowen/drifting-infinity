"""Death and Final Stand mechanics per GDD 2.6."""

from dataclasses import dataclass


@dataclass
class FinalStandCheck:
    """Result of a Final Stand CON save."""
    dc: int
    roll: int
    success: bool
    is_dead: bool  # True if failed the save


# Final Stand DC starts at 10 and increases by 2 each round on Final Stand
BASE_FINAL_STAND_DC = 10
DC_INCREMENT_PER_ROUND = 2


def compute_final_stand_dc(rounds_on_final_stand: int) -> int:
    """Compute the DC for a Final Stand CON save.

    DC starts at 10 and increases by 2 for each round spent on Final Stand.
    """
    return BASE_FINAL_STAND_DC + (rounds_on_final_stand * DC_INCREMENT_PER_ROUND)


def check_final_stand(
    con_save_roll: int,
    rounds_on_final_stand: int,
) -> FinalStandCheck:
    """Check if a creature survives their Final Stand CON save.

    Args:
        con_save_roll: The creature's CON save total (d20 + CON modifier)
        rounds_on_final_stand: How many rounds they've been on Final Stand

    Returns:
        FinalStandCheck with the result
    """
    dc = compute_final_stand_dc(rounds_on_final_stand)
    success = con_save_roll >= dc

    return FinalStandCheck(
        dc=dc,
        roll=con_save_roll,
        success=success,
        is_dead=not success,
    )
