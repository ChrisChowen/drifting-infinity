"""Session export API endpoints.

Export runs and floors as structured JSON or printable Markdown for
use outside the app — sharing with players, printing reference sheets,
or archiving session data.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.arena import Arena, ArenaCreatureStatus
from app.models.campaign import Campaign
from app.models.character import Character
from app.models.floor import Floor
from app.models.monster import Monster
from app.models.run import Run

router = APIRouter(prefix="/export", tags=["export"])


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


async def _build_floor_export(
    db: AsyncSession, floor: Floor
) -> dict:
    """Build a full export dict for a single floor."""
    arenas_result = await db.execute(
        select(Arena)
        .where(Arena.floor_id == floor.id)
        .order_by(Arena.arena_number)
    )
    arenas = arenas_result.scalars().all()

    arena_exports = []
    for arena in arenas:
        creatures_result = await db.execute(
            select(ArenaCreatureStatus).where(
                ArenaCreatureStatus.arena_id == arena.id
            )
        )
        creatures = creatures_result.scalars().all()

        # Look up monster names
        monster_ids = list({c.monster_id for c in creatures})
        monster_names: dict[str, str] = {}
        if monster_ids:
            m_result = await db.execute(
                select(Monster.id, Monster.name).where(
                    Monster.id.in_(monster_ids)
                )
            )
            for mid, mname in m_result.all():
                monster_names[mid] = mname

        narrative = (arena.narrative_content or {})

        arena_exports.append(
            {
                "arena_number": arena.arena_number,
                "encounter_template": arena.encounter_template,
                "environment": arena.environment,
                "xp_budget": arena.xp_budget,
                "adjusted_xp": arena.adjusted_xp,
                "tactical_brief": arena.tactical_brief,
                "is_complete": arena.is_complete,
                "dm_notes": arena.dm_notes,
                "custom_read_aloud": arena.custom_read_aloud,
                "narrative": {
                    "read_aloud_text": narrative.get(
                        "read_aloud_text", ""
                    ),
                    "encounter_hook": narrative.get(
                        "encounter_hook", ""
                    ),
                    "dm_guidance_boxes": narrative.get(
                        "dm_guidance_boxes", []
                    ),
                    "creature_flavor": narrative.get(
                        "creature_flavor", []
                    ),
                    "weakness_tips": narrative.get(
                        "weakness_tips", []
                    ),
                    "roguelike_reference": narrative.get(
                        "roguelike_reference", {}
                    ),
                },
                "creatures": [
                    {
                        "instance_label": c.instance_label,
                        "monster_name": monster_names.get(
                            c.monster_id, "Unknown"
                        ),
                        "status": c.status,
                        "is_reinforcement": c.is_reinforcement,
                    }
                    for c in creatures
                ],
            }
        )

    return {
        "floor_number": floor.floor_number,
        "arena_count": floor.arena_count,
        "arenas_completed": floor.arenas_completed,
        "is_complete": floor.is_complete,
        "active_affixes": floor.active_affixes or [],
        "templates_used": floor.templates_used or [],
        "objectives_used": floor.objectives_used or [],
        "arenas": arena_exports,
    }


def _floor_to_markdown(floor_data: dict) -> str:
    """Convert a floor export dict to printable markdown."""
    lines: list[str] = []
    fn = floor_data["floor_number"]
    lines.append(f"# Floor {fn}")
    lines.append("")

    affixes = floor_data.get("active_affixes", [])
    if affixes:
        affix_str = ", ".join(
            a.replace("_", " ").title() for a in affixes
        )
        lines.append(f"**Affixes:** {affix_str}")
        lines.append("")

    for arena in floor_data.get("arenas", []):
        an = arena["arena_number"]
        lines.append(f"## Arena {an}")
        lines.append("")

        if arena.get("environment"):
            env = arena["environment"].replace("_", " ").title()
            lines.append(f"**Environment:** {env}")
        if arena.get("encounter_template"):
            tpl = arena["encounter_template"].replace("_", " ").title()
            lines.append(f"**Template:** {tpl}")
        if arena.get("xp_budget"):
            lines.append(f"**XP Budget:** {arena['xp_budget']}")
        lines.append("")

        # Read-aloud text
        read_aloud = (
            arena.get("custom_read_aloud")
            or arena.get("narrative", {}).get("read_aloud_text", "")
        )
        if read_aloud:
            lines.append("### Read Aloud")
            lines.append("")
            lines.append(f"> {read_aloud}")
            lines.append("")

        # Encounter hook
        hook = arena.get("narrative", {}).get("encounter_hook", "")
        if hook:
            lines.append(f"*{hook}*")
            lines.append("")

        # Creatures
        creatures = arena.get("creatures", [])
        if creatures:
            lines.append("### Creatures")
            lines.append("")
            for c in creatures:
                status = c.get("status", "alive")
                label = c.get("instance_label", "Unknown")
                name = c.get("monster_name", "")
                if name and name != label:
                    lines.append(f"- {label} ({name}) — {status}")
                else:
                    lines.append(f"- {label} — {status}")
            lines.append("")

        # Tactical brief
        if arena.get("tactical_brief"):
            lines.append("### Tactical Brief")
            lines.append("")
            lines.append(arena["tactical_brief"])
            lines.append("")

        # DM guidance boxes
        guidance = arena.get("narrative", {}).get(
            "dm_guidance_boxes", []
        )
        for box in guidance:
            title = box.get("title", "Guidance")
            content = box.get("content", "")
            lines.append(f"**{title}:** {content}")
            lines.append("")

        # Weakness tips
        tips = arena.get("narrative", {}).get("weakness_tips", [])
        if tips:
            lines.append("### Weakness Tips")
            lines.append("")
            for tip in tips:
                lines.append(f"- {tip}")
            lines.append("")

        # DM notes
        if arena.get("dm_notes"):
            lines.append("### DM Notes")
            lines.append("")
            lines.append(arena["dm_notes"])
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------


@router.get("/runs/{run_id}")
async def export_run(
    run_id: str,
    format: str = Query(default="json", pattern="^(json|markdown)$"),
    db: AsyncSession = Depends(get_db),
):
    """Export a full run as structured JSON or Markdown."""
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    campaign = await db.get(Campaign, run.campaign_id)

    # Get characters
    char_result = await db.execute(
        select(Character).where(
            Character.campaign_id == run.campaign_id
        )
    )
    chars = char_result.scalars().all()

    # Get all floors
    floors_result = await db.execute(
        select(Floor)
        .where(Floor.run_id == run_id)
        .order_by(Floor.floor_number)
    )
    floors = floors_result.scalars().all()

    floor_exports = []
    for floor in floors:
        floor_exports.append(await _build_floor_export(db, floor))

    export_data = {
        "title": "Drifting Infinity — Run Export",
        "campaign_name": campaign.name if campaign else "Unknown",
        "run_id": run.id,
        "started_at": (
            run.started_at.isoformat() if run.started_at else None
        ),
        "ended_at": (
            run.ended_at.isoformat() if run.ended_at else None
        ),
        "outcome": run.outcome,
        "starting_level": run.starting_level,
        "floor_count": run.floor_count,
        "floors_completed": run.floors_completed,
        "total_gold_earned": run.total_gold_earned,
        "total_shards_earned": run.total_shards_earned,
        "armillary_favour": run.armillary_favour,
        "lives_remaining": run.lives_remaining,
        "total_deaths": run.total_deaths,
        "seed": run.seed,
        "party": [
            {
                "name": c.name,
                "class_name": c.class_name,
                "level": c.level,
                "xp_total": c.xp_total,
            }
            for c in chars
        ],
        "floors": floor_exports,
    }

    if format == "markdown":
        md = _run_to_markdown(export_data)
        return PlainTextResponse(
            content=md,
            media_type="text/markdown",
        )

    return export_data


@router.get("/prep/floor/{floor_id}")
async def export_floor_prep(
    floor_id: str,
    format: str = Query(default="json", pattern="^(json|markdown)$"),
    db: AsyncSession = Depends(get_db),
):
    """Export a floor as a printable mini-module."""
    floor = await db.get(Floor, floor_id)
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    floor_data = await _build_floor_export(db, floor)

    if format == "markdown":
        md = _floor_to_markdown(floor_data)
        return PlainTextResponse(
            content=md,
            media_type="text/markdown",
        )

    return floor_data


def _run_to_markdown(data: dict) -> str:
    """Convert a full run export dict to markdown."""
    lines: list[str] = []
    lines.append("# Drifting Infinity — Run Export")
    lines.append("")

    outcome = data.get("outcome", "in progress")
    is_victory = outcome == "completed"
    result = "Victory" if is_victory else (
        "Defeat" if outcome == "failed" else "In Progress"
    )

    lines.append(
        f"**Campaign:** {data.get('campaign_name', 'Unknown')}"
    )
    lines.append(f"**Result:** {result}")
    lines.append(
        f"**Floors:** {data['floors_completed']} / "
        f"{data['floor_count']}"
    )
    lines.append(f"**Starting Level:** {data['starting_level']}")
    lines.append(f"**Seed:** {data.get('seed', 0)}")

    if data.get("started_at"):
        lines.append(f"**Started:** {data['started_at']}")
    if data.get("ended_at"):
        lines.append(f"**Ended:** {data['ended_at']}")

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"- Gold Earned: {data['total_gold_earned']:,}"
    )
    lines.append(
        f"- Shards Earned: {data['total_shards_earned']:,}"
    )
    lines.append(
        f"- Armillary Favour: {data['armillary_favour']}"
    )
    lines.append(
        f"- Deaths: {data['total_deaths']} "
        f"(Lives Remaining: {data['lives_remaining']})"
    )

    # Party
    party = data.get("party", [])
    if party:
        lines.append("")
        lines.append("## Party")
        lines.append("")
        for c in party:
            lines.append(
                f"- **{c['name']}** — Level {c['level']} "
                f"{c['class_name']}"
            )

    # Floors
    for floor_data in data.get("floors", []):
        lines.append("")
        lines.append(_floor_to_markdown(floor_data))

    lines.append("")
    lines.append("---")
    lines.append("*Generated by Drifting Infinity*")

    return "\n".join(lines)
