"""Achievement definitions and checking.

Achievements track notable milestones across runs.  Each achievement can
only be earned once per campaign.  They award essence and unlock lore.
"""

from dataclasses import dataclass


@dataclass
class AchievementDef:
    id: str
    name: str
    description: str
    category: str       # "combat", "exploration", "economy", "meta"
    essence_reward: int
    lore_fragment_id: str | None = None


# ---------------------------------------------------------------------------
# Achievement catalogue
# ---------------------------------------------------------------------------

ACHIEVEMENTS: list[AchievementDef] = [
    # Combat
    AchievementDef(
        id="first_blood",
        name="First Blood",
        description="Complete Floor 1 for the first time.",
        category="combat",
        essence_reward=10,
    ),
    AchievementDef(
        id="deathless_floor",
        name="Deathless Floor",
        description="Clear an entire floor with no character deaths.",
        category="combat",
        essence_reward=15,
    ),
    AchievementDef(
        id="deathless_run",
        name="Deathless Run",
        description="Complete an entire run with no character deaths.",
        category="combat",
        essence_reward=75,
        lore_fragment_id="frag_deathless",
    ),
    AchievementDef(
        id="the_long_descent",
        name="The Long Descent",
        description="Reach Floor 10 for the first time.",
        category="combat",
        essence_reward=25,
        lore_fragment_id="frag_long_descent",
    ),
    AchievementDef(
        id="armillarys_equal",
        name="Armillary's Equal",
        description="Complete a full 20-floor run.",
        category="combat",
        essence_reward=50,
        lore_fragment_id="frag_victory",
    ),
    AchievementDef(
        id="tpk_survivor",
        name="TPK Survivor",
        description="Survive a TPK via Phoenix Protocol.",
        category="combat",
        essence_reward=20,
    ),
    # Exploration
    AchievementDef(
        id="secret_finder",
        name="Secret Finder",
        description="Discover a secret floor for the first time.",
        category="exploration",
        essence_reward=40,
        lore_fragment_id="frag_secret_discovered",
    ),
    AchievementDef(
        id="collector_slayer",
        name="Collector Slayer",
        description="Kill The Collector before it escapes.",
        category="exploration",
        essence_reward=20,
    ),
    AchievementDef(
        id="social_butterfly",
        name="Social Butterfly",
        description="Successfully resolve 5 social encounters across all runs.",
        category="exploration",
        essence_reward=30,
    ),
    # Economy
    AchievementDef(
        id="big_spender",
        name="Big Spender",
        description="Spend 10,000 gold in a single run.",
        category="economy",
        essence_reward=20,
    ),
    AchievementDef(
        id="hoarder",
        name="Hoarder",
        description="Accumulate 50 Astral Shards across all runs.",
        category="economy",
        essence_reward=25,
    ),
    # Meta
    AchievementDef(
        id="completionist",
        name="Completionist",
        description="Use all 12 encounter templates in a single run.",
        category="meta",
        essence_reward=30,
    ),
    AchievementDef(
        id="veteran",
        name="Veteran",
        description="Complete 5 runs (any outcome).",
        category="meta",
        essence_reward=35,
    ),
    AchievementDef(
        id="lore_master",
        name="Lore Master",
        description="Collect 20 lore fragments.",
        category="meta",
        essence_reward=40,
        lore_fragment_id="frag_lore_master",
    ),
    AchievementDef(
        id="aethon_defied",
        name="Aethon Defied",
        description="Defeat Aethon in the final encounter on Floor 20.",
        category="meta",
        essence_reward=100,
        lore_fragment_id="frag_aethon_truth",
    ),
]


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

_ACHIEVEMENT_INDEX: dict[str, AchievementDef] = {a.id: a for a in ACHIEVEMENTS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_achievement(achievement_id: str) -> AchievementDef | None:
    """Return an achievement definition by id."""
    return _ACHIEVEMENT_INDEX.get(achievement_id)


def check_achievements(
    run_stats: dict,
    campaign_meta_achievements: list[str],
) -> list[str]:
    """Check which achievements were newly earned during a run.

    Args:
        run_stats: Dict with keys like:
            - floors_completed: int
            - total_deaths: int
            - run_won: bool
            - templates_used: list[str]
            - gold_spent: int
            - secret_events: list[str]
            - collector_killed: bool
            - social_successes: int
            - total_runs_completed: int
            - total_shards_lifetime: int
            - total_lore_fragments: int
            - tpk_saved: bool
            - aethon_defeated: bool
        campaign_meta_achievements: Already-earned achievement IDs.

    Returns:
        List of newly earned achievement IDs.
    """
    earned = campaign_meta_achievements or []
    newly_earned: list[str] = []

    def _check(aid: str, condition: bool) -> None:
        if aid not in earned and condition:
            newly_earned.append(aid)

    _check("first_blood", run_stats.get("floors_completed", 0) >= 1)
    _check("deathless_floor", run_stats.get("had_deathless_floor", False))
    _check("deathless_run", run_stats.get("run_won", False) and run_stats.get("total_deaths", 0) == 0)
    _check("the_long_descent", run_stats.get("floors_completed", 0) >= 10)
    _check("armillarys_equal", run_stats.get("run_won", False))
    _check("tpk_survivor", run_stats.get("tpk_saved", False))
    _check("secret_finder", len(run_stats.get("secret_events", [])) > 0)
    _check("collector_slayer", run_stats.get("collector_killed", False))
    _check("social_butterfly", run_stats.get("total_social_successes", 0) >= 5)
    _check("big_spender", run_stats.get("gold_spent", 0) >= 10000)
    _check("hoarder", run_stats.get("total_shards_lifetime", 0) >= 50)
    _check("completionist", len(set(run_stats.get("templates_used", []))) >= 12)
    _check("veteran", run_stats.get("total_runs_completed", 0) >= 5)
    _check("lore_master", run_stats.get("total_lore_fragments", 0) >= 20)
    _check("aethon_defied", run_stats.get("aethon_defeated", False))

    return newly_earned
