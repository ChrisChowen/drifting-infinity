"""Lives system: death processing, scar generation, TPK handling.

Each run starts with a base number of lives (3 + meta-talent bonuses).
Character deaths cost lives; when lives run out, further deaths are
permanent for the run.  TPK = all living characters die = run over.
"""

import random
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_STARTING_LIVES = 3
MAX_LIVES = 5

SCAR_DESCRIPTIONS: list[str] = [
    "A jagged scar across the left cheek — a memento from the Armillary's cruelty.",
    "A faint arcane burn on the forearm that never fully healed.",
    "One eye clouded with a milky film — the Armillary's mark.",
    "A slight limp from a shattered knee, knit back together by desperate magic.",
    "Phantom pain in the chest where a blade once found its mark.",
    "White-streaked hair at the temples — aged by the shock of death.",
    "A tremor in the sword hand that surfaces under stress.",
    "A hollow whisper in the ears — echoes of the death that almost stuck.",
    "Skin cold to the touch along the spine — where the Armillary's essence seeped in.",
    "A crescent-shaped burn on the palm from gripping a weapon past the point of death.",
    "An inability to dream — sleep is just darkness since the Armillary brought them back.",
    "A faint shimmer around the edges, as if reality isn't quite sure they should still exist.",
]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class DeathResult:
    life_spent: bool
    lives_remaining: int
    permanently_dead: bool
    scar: str | None
    notes: list[str]


@dataclass
class TPKResult:
    run_over: bool
    saved_by_phoenix: bool
    lives_remaining: int
    notes: list[str]


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def compute_starting_lives(
    meta_talents: list[str],
    first_run_bonus: int = 0,
) -> int:
    """Compute starting lives for a new run based on meta-talents.

    Args:
        meta_talents: Unlocked talent IDs.
        first_run_bonus: Extra lives for the campaign's first run (from settings).
    """
    lives = BASE_STARTING_LIVES
    if "resilience_1" in meta_talents:
        lives += 1
    lives += first_run_bonus
    return min(MAX_LIVES, lives)


def process_character_death(
    lives_remaining: int,
    character_death_count: int,
) -> DeathResult:
    """Process a character death within a run.

    Returns a DeathResult describing what happened.
    """
    notes: list[str] = []
    scar = None
    permanently_dead = False

    if lives_remaining > 0:
        lives_remaining -= 1
        notes.append(f"Life spent. {lives_remaining} lives remaining.")
        scar = random.choice(SCAR_DESCRIPTIONS)
        notes.append(f"Scar acquired: {scar}")
    else:
        permanently_dead = True
        notes.append("No lives remaining — character is permanently dead for this run.")

    return DeathResult(
        life_spent=not permanently_dead,
        lives_remaining=lives_remaining,
        permanently_dead=permanently_dead,
        scar=scar,
        notes=notes,
    )


def process_tpk(
    lives_remaining: int,
    meta_talents: list[str],
    phoenix_used_this_run: bool = False,
) -> TPKResult:
    """Process a Total Party Kill.

    If Phoenix Protocol is available and unused, the TPK is converted to a
    near-death experience instead of ending the run.
    """
    notes: list[str] = []

    has_phoenix = "resilience_5" in meta_talents
    can_save = has_phoenix and not phoenix_used_this_run

    if can_save:
        notes.append("Phoenix Protocol activates! The party is pulled back from oblivion.")
        notes.append("All characters resurrect at 1 HP. 1 life remains.")
        return TPKResult(
            run_over=False,
            saved_by_phoenix=True,
            lives_remaining=1,
            notes=notes,
        )

    notes.append("Total Party Kill. The run is over.")
    notes.append("The Armillary claims its due. Return to the Nexus.")
    return TPKResult(
        run_over=True,
        saved_by_phoenix=False,
        lives_remaining=0,
        notes=notes,
    )


def can_resurrect(lives_remaining: int) -> bool:
    """Check if a dead character can be resurrected at floor clear."""
    return lives_remaining > 0


def add_life(current_lives: int) -> int:
    """Add a life (from shop purchase, achievement, or armillary effect)."""
    return min(MAX_LIVES, current_lives + 1)
