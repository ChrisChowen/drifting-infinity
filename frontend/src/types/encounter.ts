import type { TacticalRole } from "./creature";
import type { ArmillaryEffect } from "./armillary";

export interface ObjectiveBonusRewards {
  gold_multiplier?: number;
  bonus_shard?: number;
}

export interface CreatureBuffs {
  hp_percent?: number;
  attack_bonus?: number;
  damage_bonus?: number;
  speed?: number;
  ac_bonus?: number;
  regen_hp?: number;
  save_advantage_condition?: string;
}

export interface AffixModifiedStats {
  creature_buffs?: CreatureBuffs;
}

export type EncounterTemplate =
  | "hold_and_flank"
  | "focus_fire"
  | "attrition"
  | "area_denial"
  | "ambush"
  | "boss"
  | "swarm_rush"
  | "elite_duel"
  | "siege"
  | "guerrilla"
  | "pincer_strike"
  | "dragons_court";

export interface EncounterProposal {
  creatures: EncounterCreature[];
  template: EncounterTemplate;
  xpBudget: number;
  adjustedXp: number;
  difficultyTier: string;
  tacticalBrief: string;
  warnings: EncounterWarning[];
  armillaryForecast: ArmillaryEffect[];
  mapPlacement: string;
  // Objective (Phase 7A)
  objectiveId: string;
  objectiveName: string;
  objectiveDescription: string;
  objectiveDmInstructions: string;
  objectiveWinConditions: string[];
  objectiveSpecialRules: string[];
  objectiveBonusRewards: ObjectiveBonusRewards;
  // Floor affixes (Phase 7B)
  activeAffixes: string[];
  affixModifiedStats: AffixModifiedStats;
  // Director AI notes (Phase 11B)
  difficultyNotes: string[];
  baseIntensity: number;
  adjustedIntensity: number;
  // Encounter theme (Phase 12I)
  themeId: string;
  themeName: string;
}

export interface EncounterCreature {
  monsterId: string;
  name: string;
  cr: number;
  hp: number;
  ac: number;
  tacticalRole: TacticalRole;
  count: number;
  xpEach: number;
}

export interface EncounterWarning {
  level: "warn" | "reject";
  message: string;
  creatureId: string;
}
