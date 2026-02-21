import { api } from "./client";

export interface SkillCheckSetup {
  skill: string;
  dc: number;
  success_text: string;
  failure_text: string;
}

export interface SocialEncounterSetup {
  encounter_id: string;
  name: string;
  description: string;
  dm_prompt: string;
  skill_checks: SkillCheckSetup[];
  lore_fragment_id: string | null;
}

export interface CheckResultInput {
  skill: string;
  roll: number;
  modifier: number;
}

export interface SkillCheckOutcome {
  skill: string;
  dc: number;
  roll: number;
  modifier: number;
  total: number;
  success: boolean;
  result_text: string;
}

export interface SocialEncounterResult {
  encounter_id: string;
  encounter_name: string;
  checks: SkillCheckOutcome[];
  successes: number;
  total_checks: number;
  overall_success: boolean;
  rewards: Record<string, string | number | boolean>;
  consequences: Record<string, string | number | boolean>;
  lore_fragment_id: string | null;
}

export const socialApi = {
  generate: (arenaId: string) =>
    api.post<SocialEncounterSetup | null>(`/arenas/${arenaId}/social/generate`),
  resolve: (arenaId: string, checkResults: CheckResultInput[]) =>
    api.post<SocialEncounterResult>(`/arenas/${arenaId}/social/resolve`, {
      check_results: checkResults,
    }),
};
