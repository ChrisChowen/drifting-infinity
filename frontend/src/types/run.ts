export type RunOutcome = "completed" | "failed" | "abandoned";

export interface Run {
  id: string;
  campaignId: string;
  startedAt: string;
  endedAt: string | null;
  startingLevel: number;
  floorCount: number;
  floorsCompleted: number;
  totalGoldEarned: number;
  totalShardsEarned: number;
  outcome: RunOutcome | null;
  difficultyCurve: DifficultyPoint[];
  armillaryFavour: number;
}

export interface Floor {
  id: string;
  runId: string;
  floorNumber: number;
  arenaCount: number;
  arenasCompleted: number;
  crMinimumOffset: number;
  isComplete: boolean;
  templatesUsed: string[];
}

export interface Arena {
  id: string;
  floorId: string;
  arenaNumber: number;
  encounterTemplate: string;
  difficultyTarget: number;
  xpBudget: number;
  adjustedXp: number;
  actualDifficulty: string | null;
  goldEarnedPerPlayer: number;
  tacticalBrief: string | null;
  mapId: string | null;
  environment: string | null;
  isActive: boolean;
  isComplete: boolean;
  momentumBonusEarned: boolean;
}

export interface DifficultyPoint {
  arenaIndex: number;
  planned: number;
  actual: number | null;
  partyHpAvg: number | null;
  resourceEst: number | null;
}

export type RunPhase =
  | "lobby"
  | "setup"
  | "encounter-brief"
  | "encounter-active"
  | "combat" // kept temporarily for backwards compat during migration
  | "post-arena"
  | "reward"
  | "shop"
  | "floor-transition"
  | "run-complete";

export interface HealthSnapshot {
  dmAssessment: "too_easy" | "just_right" | "too_hard" | "near_tpk";
  anyOnFinalStand: boolean;
  characterSnapshots: CharacterSnapshot[];
}

export interface CharacterSnapshot {
  characterId: string;
  hpCategory: "full" | "above_half" | "below_half" | "critical" | "down";
  conditions?: string[];
  spellSlots?: "full" | "most" | "half" | "few" | "empty";
}
