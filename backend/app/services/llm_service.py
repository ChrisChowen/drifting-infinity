"""LLM service with Anthropic API integration and mock fallback.

Provides AI-enhanced text generation for:
- Tactical briefs (encounter descriptions)
- Armillary voice lines (the entity speaking)
- Lore generation (world-building fragments)
- Post-arena narration (combat aftermath)

When `llm_enabled` is False or no API key is set, returns curated mock responses.
When True, calls the Anthropic API with feature-specific prompts.
Gracefully falls back to mock responses if the API call fails.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from app.config import settings

logger = logging.getLogger(__name__)


class LlmFeature(str, Enum):
    TACTICAL_BRIEF = "tactical_brief"
    ARMILLARY_VOICE = "armillary_voice"
    LORE_FRAGMENT = "lore_fragment"
    POST_ARENA_NARRATION = "post_arena_narration"


@dataclass
class LlmResponse:
    text: str
    feature: LlmFeature
    is_mock: bool


# ── Mock response pools ─────────────────────────────────────────────

MOCK_TACTICAL_BRIEFS = [
    "The creatures have taken defensive positions near the chamber's "
    "pillars — flanking will be difficult but rewarding.",
    "Watch for the pack tactics. They'll focus fire on whoever "
    "breaks formation first.",
    "The terrain favors ranged attackers. Melee fighters should "
    "close distance quickly before they're picked apart.",
    "This group fights with surprising coordination. Expect "
    "readied actions and opportunity attacks.",
    "The environment itself is a hazard here. Use it against them "
    "before they use it against you.",
]

MOCK_ARMILLARY_VOICE = [
    "The Armillary turns, and fate bends with it.",
    "Your struggle amuses me. Continue.",
    "The spheres align. Something stirs in the cosmic lattice.",
    "Even the strongest chains have a weakest link. I wonder "
    "which of you that is.",
    "The Armillary remembers. The Armillary always remembers.",
    "Do you feel it? The weight of destiny pressing down upon you.",
    "Another turn of the great wheel. Another test.",
]

MOCK_LORE_FRAGMENTS = [
    "The Armillary was not built — it grew, like a crystal in the "
    "void between worlds.",
    "Those who enter the Armillary's domain rarely return "
    "unchanged. Most do not return at all.",
    "The Arbiter claims to serve the Armillary, but some whisper "
    "that the relationship is far more complex.",
    "Each floor descends deeper into the Armillary's psyche. "
    "The creatures you face are its thoughts given form.",
    "Aethon speaks of freedom, but the Armillary's grip extends "
    "far beyond these walls.",
]

MOCK_POST_ARENA_NARRATION = [
    "The dust settles. The silence after combat feels heavier "
    "than the fighting itself.",
    "Victory, but at what cost? The Armillary notes your "
    "performance with cold interest.",
    "The fallen creatures dissolve into motes of light, "
    "absorbed back into the Armillary's essence.",
    "A moment to breathe. The next challenge awaits below.",
    "The arena dims as the last echo of steel fades. "
    "The descent beckons.",
]

MOCK_POOLS: dict[LlmFeature, list[str]] = {
    LlmFeature.TACTICAL_BRIEF: MOCK_TACTICAL_BRIEFS,
    LlmFeature.ARMILLARY_VOICE: MOCK_ARMILLARY_VOICE,
    LlmFeature.LORE_FRAGMENT: MOCK_LORE_FRAGMENTS,
    LlmFeature.POST_ARENA_NARRATION: MOCK_POST_ARENA_NARRATION,
}


# ── Prompt templates ────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a narrative engine for Drifting Infinity, a D&D 5e roguelike "
    "combat arena. The setting features the Armillary — a shifting "
    "extradimensional structure that spawns combat encounters. Aethon, "
    "also known as The Architect, is a cosmic scientist entity who built "
    "the Armillary and watches the party from above. Your tone should be "
    "atmospheric, dark fantasy with cosmic horror undertones. Keep "
    "responses concise and evocative. Do not use markdown formatting."
)


def _build_tactical_brief_prompt(context: dict) -> str:
    creatures = context.get("creatures", [])
    environment = context.get("environment", "unknown arena")
    objective = context.get("objective", "extermination")
    danger = context.get("danger_rating", "challenging")
    template = context.get("template", "standard")

    creature_list = ", ".join(
        f"{c.get('count', 1)}x {c.get('name', 'creature')} "
        f"({c.get('tactical_role', 'unknown')})"
        for c in creatures
    ) if creatures else "various creatures"

    return (
        f"Write a 2-3 paragraph tactical brief for a DM about to run "
        f"this encounter.\n\n"
        f"Environment: {environment}\n"
        f"Encounter composition: {creature_list}\n"
        f"Objective: {objective}\n"
        f"Danger rating: {danger}\n"
        f"Encounter template: {template}\n\n"
        f"Focus on: tactical positioning, creature behavior, key threats, "
        f"and how the environment affects the fight. Write for a DM who "
        f"knows 5e rules but needs actionable combat guidance. Do not "
        f"include stat blocks."
    )


def _build_armillary_voice_prompt(context: dict) -> str:
    effect = context.get("effect_name", "unknown effect")
    category = context.get("category", "neutral")
    floor_number = context.get("floor_number", 1)
    party_state = context.get("party_state", "healthy")

    return (
        f"Write a 1-2 sentence voice line from Aethon (The Architect), "
        f"the cosmic entity who controls the Armillary.\n\n"
        f"The Armillary just triggered: {effect} ({category} effect)\n"
        f"Floor depth: {floor_number}\n"
        f"Party condition: {party_state}\n\n"
        f"Aethon speaks with detached curiosity, cosmic menace, and "
        f"occasional dry humor. They view the party as fascinating "
        f"specimens. Keep it to 1-2 sentences maximum."
    )


def _build_lore_fragment_prompt(context: dict) -> str:
    topic = context.get("topic", "the Armillary")
    floor_number = context.get("floor_number", 1)
    category = context.get("category", "history")

    return (
        f"Write a single short lore fragment (2-3 sentences) about "
        f"the Armillary setting.\n\n"
        f"Topic: {topic}\n"
        f"Category: {category}\n"
        f"Floor depth: {floor_number}\n\n"
        f"The fragment should feel like a recovered text, an overheard "
        f"whisper, or a half-remembered vision. It should hint at deeper "
        f"mysteries without fully explaining them. Dark fantasy tone "
        f"with cosmic horror undertones."
    )


def _build_post_arena_prompt(context: dict) -> str:
    outcome = context.get("outcome", "victory")
    deaths = context.get("deaths", 0)
    creatures_defeated = context.get("creatures_defeated", [])
    environment = context.get("environment", "arena")
    exploits_used = context.get("exploits_used", 0)

    creature_names = ", ".join(
        c.get("name", "creature") for c in creatures_defeated
    ) if creatures_defeated else "the creatures"

    return (
        f"Write a 1-2 paragraph post-combat narration for the DM to "
        f"read aloud.\n\n"
        f"Outcome: {outcome}\n"
        f"Character deaths: {deaths}\n"
        f"Creatures defeated: {creature_names}\n"
        f"Environment: {environment}\n"
        f"Weakness exploits triggered: {exploits_used}\n\n"
        f"The narration should capture the aftermath — the settling "
        f"dust, the cost of the fight, and the Armillary's reaction. "
        f"If there were deaths, acknowledge the loss. If exploits were "
        f"triggered, reference the party's tactical brilliance. Keep it "
        f"atmospheric and brief."
    )


PROMPT_BUILDERS: dict[LlmFeature, Callable[[dict], str]] = {
    LlmFeature.TACTICAL_BRIEF: _build_tactical_brief_prompt,
    LlmFeature.ARMILLARY_VOICE: _build_armillary_voice_prompt,
    LlmFeature.LORE_FRAGMENT: _build_lore_fragment_prompt,
    LlmFeature.POST_ARENA_NARRATION: _build_post_arena_prompt,
}

# Max tokens per feature to control response length and cost
MAX_TOKENS: dict[LlmFeature, int] = {
    LlmFeature.TACTICAL_BRIEF: 400,
    LlmFeature.ARMILLARY_VOICE: 100,
    LlmFeature.LORE_FRAGMENT: 150,
    LlmFeature.POST_ARENA_NARRATION: 300,
}


# ── Anthropic API client ────────────────────────────────────────────

_client = None


def _get_client():
    """Lazy-initialize the Anthropic async client."""
    global _client
    if _client is None:
        import anthropic

        _client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=10.0,
        )
    return _client


async def _call_anthropic(feature: LlmFeature, context: dict) -> str:
    """Call the Anthropic API with a feature-specific prompt."""
    client = _get_client()
    prompt_builder = PROMPT_BUILDERS.get(feature)
    if not prompt_builder:
        raise ValueError(f"No prompt builder for feature: {feature}")

    user_prompt = prompt_builder(context)
    max_tokens = MAX_TOKENS.get(feature, 300)

    message = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text


# ── Service ──────────────────────────────────────────────────────────

async def generate(
    feature: LlmFeature,
    context: dict | None = None,
) -> LlmResponse:
    """Generate text for a given feature.

    If LLM is enabled and an API key is configured, calls the
    Anthropic API. Otherwise, returns a curated mock response.
    Falls back to mock responses if the API call fails.

    Args:
        feature: Which type of text to generate.
        context: Optional dict of contextual data (creature names,
                 environment, difficulty, etc.) for prompt construction.
    """
    if settings.llm_enabled and settings.anthropic_api_key:
        try:
            text = await _call_anthropic(feature, context or {})
            return LlmResponse(text=text, feature=feature, is_mock=False)
        except Exception as e:
            logger.warning(
                "LLM API call failed for %s, falling back to mock: %s",
                feature.value, e,
            )

    pool = MOCK_POOLS.get(feature, MOCK_TACTICAL_BRIEFS)
    text = random.choice(pool)

    return LlmResponse(
        text=text,
        feature=feature,
        is_mock=True,
    )


async def is_available() -> bool:
    """Check if the LLM service is configured and available."""
    return bool(settings.llm_enabled and settings.anthropic_api_key)
