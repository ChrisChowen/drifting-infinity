import { api } from "./client";
import type { MonsterStatblock } from "@/types/creature";
import type { ObjectiveBonusRewards, AffixModifiedStats } from "@/types/encounter";

export interface EncounterCreature {
  monster_id: string;
  name: string;
  cr: number;
  hp: number;
  ac: number;
  tactical_role: string;
  count: number;
  xp_each: number;
  statblock: MonsterStatblock;
}

export interface EncounterProposal {
  creatures: EncounterCreature[];
  template: string;
  xp_budget: number;
  adjusted_xp: number;
  difficulty_tier: string;
  tactical_brief: string;
  warnings: { level: string; message: string; creature_id: string }[];
  creature_count: number;
  environment: string;
  environment_name: string;
  terrain_features: string[];
  map_suggestions: string[];
  // Objective (Phase 7A)
  objective_id: string;
  objective_name: string;
  objective_description: string;
  objective_dm_instructions: string;
  objective_win_conditions: string[];
  objective_special_rules: string[];
  objective_bonus_rewards: ObjectiveBonusRewards;
  // Floor affixes (Phase 7B)
  active_affixes: string[];
  affix_details: { id: string; name: string; category: string; description: string; flavor_text: string }[];
  affix_modified_stats: AffixModifiedStats;
  // Danger rating (tiered label)
  danger_rating: string;
  // Director AI notes
  difficulty_notes: string[];
  base_intensity: number;
  adjusted_intensity: number;
  // Theme
  theme_id: string;
  theme_name: string;
  // Narrative content (Dynamic Sourcebook)
  read_aloud_text: string;
  encounter_hook: string;
  dm_guidance_boxes: { title: string; content: string; category: string }[];
  creature_flavor: { monster_id: string; name: string; personality: string; behavior: string; arena_reason: string }[];
  weakness_tips: string[];
  roguelike_reference: Record<string, string>;
}

export const encountersApi = {
  generate: (arenaId: string, params?: { difficulty?: string; template?: string; environment?: string; objective?: string }) => {
    const query = new URLSearchParams();
    if (params?.difficulty) query.set("difficulty", params.difficulty);
    if (params?.template) query.set("template", params.template);
    if (params?.environment) query.set("environment", params.environment);
    if (params?.objective) query.set("objective", params.objective);
    const qs = query.toString();
    return api.post<EncounterProposal>(`/arenas/${arenaId}/encounter/generate${qs ? `?${qs}` : ""}`);
  },
  approve: (arenaId: string, proposal: EncounterProposal) =>
    api.post(`/arenas/${arenaId}/encounter/approve`, proposal),
  updateObjectiveProgress: (arenaId: string, progress: Record<string, unknown>) =>
    api.post(`/arenas/${arenaId}/encounter/objective/progress`, { progress }),
};
