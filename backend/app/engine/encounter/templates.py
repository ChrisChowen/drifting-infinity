"""Encounter templates per GDD 4.2 - define role compositions for different tactical scenarios."""

from dataclasses import dataclass


@dataclass
class EncounterTemplate:
    name: str
    description: str
    role_weights: dict[str, float]  # role -> weight (higher = more likely to be selected)
    min_creatures: int
    max_creatures: int
    preferred_cr_spread: str  # "mixed", "uniform", "boss_plus_minions"
    tactical_brief_template: str


TEMPLATES: dict[str, EncounterTemplate] = {
    "hold_and_flank": EncounterTemplate(
        name="Hold & Flank",
        description="Soldiers hold the front while skirmishers flank around",
        role_weights={
            "soldier": 3.0,
            "skirmisher": 2.5,
            "brute": 1.5,
            "artillery": 0.5,
            "controller": 0.5,
            "lurker": 1.0,
        },
        min_creatures=3,
        max_creatures=7,
        preferred_cr_spread="mixed",
        tactical_brief_template=(
            "Soldiers engage the front line while skirmishers move to flank. "
            "Key threat: being surrounded. Prioritize controlling the flankers."
        ),
    ),
    "focus_fire": EncounterTemplate(
        name="Focus Fire",
        description="Ranged attackers concentrate fire while tanks shield them",
        role_weights={
            "artillery": 3.0,
            "soldier": 2.0,
            "brute": 1.5,
            "controller": 1.0,
            "skirmisher": 0.5,
            "lurker": 0.5,
        },
        min_creatures=3,
        max_creatures=6,
        preferred_cr_spread="mixed",
        tactical_brief_template=(
            "Artillery creatures focus fire from range while frontliners screen. "
            "Key threat: concentrated ranged damage. Close the gap fast."
        ),
    ),
    "attrition": EncounterTemplate(
        name="Attrition",
        description="Durable enemies wear the party down over a long fight",
        role_weights={
            "brute": 3.0,
            "soldier": 2.5,
            "controller": 1.5,
            "artillery": 0.5,
            "skirmisher": 0.5,
            "lurker": 0.5,
        },
        min_creatures=2,
        max_creatures=5,
        preferred_cr_spread="uniform",
        tactical_brief_template=(
            "High-HP creatures designed to outlast the party. "
            "Key threat: resource drain. Focus fire to eliminate threats one at a time."
        ),
    ),
    "area_denial": EncounterTemplate(
        name="Area Denial",
        description="Controllers lock down zones while others punish positioning",
        role_weights={
            "controller": 3.0,
            "artillery": 2.0,
            "soldier": 1.5,
            "lurker": 1.5,
            "brute": 0.5,
            "skirmisher": 0.5,
        },
        min_creatures=3,
        max_creatures=6,
        preferred_cr_spread="mixed",
        tactical_brief_template=(
            "Controllers create hazardous zones while allies punish bad positioning. "
            "Key threat: movement restriction. Dispel or push through control effects."
        ),
    ),
    "ambush": EncounterTemplate(
        name="Ambush",
        description="Hidden attackers strike from unexpected positions",
        role_weights={
            "lurker": 3.0,
            "skirmisher": 2.5,
            "artillery": 1.5,
            "controller": 1.0,
            "brute": 0.5,
            "soldier": 0.5,
        },
        min_creatures=3,
        max_creatures=6,
        preferred_cr_spread="mixed",
        tactical_brief_template=(
            "Hidden creatures strike from stealth and unexpected angles. "
            "Key threat: surprise damage. Perception checks and AoE to reveal attackers."
        ),
    ),
    "boss": EncounterTemplate(
        name="Boss",
        description="A single powerful creature with optional supporting minions",
        role_weights={
            "brute": 2.5,
            "controller": 2.5,
            "soldier": 2.0,
            "artillery": 1.5,
            "lurker": 1.0,
            "skirmisher": 1.0,
        },
        min_creatures=1,
        max_creatures=4,
        preferred_cr_spread="boss_plus_minions",
        tactical_brief_template=(
            "A powerful boss creature dominates the encounter, supported by minions. "
            "Key threat: the boss's signature abilities. Manage minions while focusing the boss."
        ),
    ),
    "swarm_rush": EncounterTemplate(
        name="Swarm Rush",
        description="Many weak creatures overwhelm with numbers",
        role_weights={
            "skirmisher": 3.0,
            "brute": 2.0,
            "soldier": 1.5,
            "lurker": 0.5,
            "artillery": 0.5,
            "controller": 0.5,
        },
        min_creatures=5,
        max_creatures=10,
        preferred_cr_spread="uniform",
        tactical_brief_template=(
            "A horde of weak creatures floods the battlefield. "
            "Key threat: action economy. Use AoE effects and bottleneck terrain."
        ),
    ),
    "elite_duel": EncounterTemplate(
        name="Elite Duel",
        description="Few powerful creatures demand focused tactics",
        role_weights={
            "brute": 3.0,
            "controller": 2.0,
            "soldier": 2.0,
            "artillery": 1.0,
            "skirmisher": 0.5,
            "lurker": 0.5,
        },
        min_creatures=1,
        max_creatures=3,
        preferred_cr_spread="uniform",
        tactical_brief_template=(
            "A small number of elite threats with high HP and damage. "
            "Key threat: sustained damage output. Focus fire and manage resources carefully."
        ),
    ),
    "siege": EncounterTemplate(
        name="Siege",
        description="Ranged bombardment with terrain control",
        role_weights={
            "artillery": 3.0,
            "controller": 2.5,
            "soldier": 1.5,
            "brute": 1.0,
            "lurker": 0.5,
            "skirmisher": 0.5,
        },
        min_creatures=4,
        max_creatures=8,
        preferred_cr_spread="mixed",
        tactical_brief_template=(
            "Ranged attackers rain fire from fortified positions while controllers restrict approach. "
            "Key threat: ranged saturation. Use cover and close distance quickly."
        ),
    ),
    "guerrilla": EncounterTemplate(
        name="Guerrilla",
        description="Hit-and-run with ranged support",
        role_weights={
            "lurker": 3.0,
            "artillery": 2.0,
            "skirmisher": 2.0,
            "controller": 0.5,
            "brute": 0.5,
            "soldier": 0.5,
        },
        min_creatures=3,
        max_creatures=6,
        preferred_cr_spread="mixed",
        tactical_brief_template=(
            "Enemies strike from hiding, deal damage, then retreat or reposition. "
            "Key threat: inability to pin down threats. Ready actions and area control."
        ),
    ),
    "pincer_strike": EncounterTemplate(
        name="Pincer Strike",
        description="Two-front flanking assault",
        role_weights={
            "skirmisher": 3.0,
            "lurker": 2.5,
            "soldier": 1.5,
            "brute": 1.0,
            "artillery": 0.5,
            "controller": 0.5,
        },
        min_creatures=4,
        max_creatures=7,
        preferred_cr_spread="mixed",
        tactical_brief_template=(
            "Enemies attack from multiple directions simultaneously. "
            "Key threat: divided attention. Maintain formation and cover rear."
        ),
    ),
    "dragons_court": EncounterTemplate(
        name="Dragon's Court",
        description="Boss plus themed retinue",
        role_weights={
            "brute": 3.5,
            "soldier": 2.0,
            "artillery": 1.5,
            "controller": 1.0,
            "lurker": 0.5,
            "skirmisher": 0.5,
        },
        min_creatures=2,
        max_creatures=5,
        preferred_cr_spread="boss_plus_minions",
        tactical_brief_template=(
            "A powerful boss commands a themed retinue of servants. "
            "Key threat: the boss's legendary actions. Neutralize servants first or burst the boss."
        ),
    ),
}


def get_template(name: str) -> EncounterTemplate:
    return TEMPLATES[name]


def get_all_template_names() -> list[str]:
    return list(TEMPLATES.keys())
