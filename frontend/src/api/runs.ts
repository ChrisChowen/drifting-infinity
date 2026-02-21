import { api } from "./client";

export interface NarrativeContent {
  read_aloud_text: string;
  encounter_hook: string;
  dm_guidance_boxes: { title: string; content: string; category: string }[];
  creature_flavor: { monster_id: string; name: string; personality: string; behavior: string; arena_reason: string }[];
  weakness_tips: string[];
  roguelike_reference: Record<string, string>;
}

export interface RunResponse {
  id: string;
  campaign_id: string;
  started_at: string;
  ended_at: string | null;
  starting_level: number;
  floor_count: number;
  seed: number;
  floors_completed: number;
  total_gold_earned: number;
  total_shards_earned: number;
  outcome: string | null;
  difficulty_curve: unknown[];
  armillary_favour: number;
  affix_history: string[];
  lives_remaining: number;
  total_deaths: number;
  death_log: { character_id: string; character_name: string; death_number: number; lives_remaining: number; timestamp: string }[];
}

export interface FloorResponse {
  id: string;
  run_id: string;
  floor_number: number;
  arena_count: number;
  arenas_completed: number;
  cr_minimum_offset: number;
  is_complete: boolean;
  templates_used: string[];
  objectives_used: string[];
  active_affixes: string[];
}

export interface ArenaResponse {
  id: string;
  floor_id: string;
  arena_number: number;
  encounter_template: string | null;
  difficulty_target: number | null;
  xp_budget: number | null;
  adjusted_xp: number | null;
  actual_difficulty: string | null;
  gold_earned_per_player: number;
  tactical_brief: string | null;
  map_id: string | null;
  environment: string | null;
  is_active: boolean;
  is_complete: boolean;
  momentum_bonus_earned: boolean;
  objective: string | null;
  objective_progress: Record<string, string | number | boolean> | null;
  dm_notes: string | null;
  custom_read_aloud: string | null;
  narrative_content: NarrativeContent | null;
}

export interface ArenaCreatureStatus {
  id: string;
  arena_id: string;
  monster_id: string;
  instance_label: string;
  status: "alive" | "bloodied" | "defeated";
  is_reinforcement: boolean;
}

export interface IntensityCurvePoint {
  floor: number;
  arena: number;
  phase: "warmup" | "escalation" | "climax";
  planned_intensity: number;
  planned_difficulty: string;
  actual_difficulty: string | null;
  difficulty_target: number | null;
  is_complete: boolean;
}

export interface IntensityCurveResponse {
  run_id: string;
  floor_count: number;
  curve: IntensityCurvePoint[];
}

export const runsApi = {
  list: (campaignId: string) =>
    api.get<RunResponse[]>(`/campaigns/${campaignId}/runs`),
  start: (campaignId: string, data: { starting_level?: number; floor_count?: number }) =>
    api.post<RunResponse>(`/campaigns/${campaignId}/runs`, data),
  getActive: (campaignId: string) =>
    api.get<RunResponse | null>(`/campaigns/${campaignId}/runs/active`),
  get: (campaignId: string, runId: string) =>
    api.get<RunResponse>(`/campaigns/${campaignId}/runs/${runId}`),
  end: (campaignId: string, runId: string, outcome?: string) =>
    api.post(`/campaigns/${campaignId}/runs/${runId}/end?outcome=${outcome || "completed"}`),
  getLives: (campaignId: string, runId: string) =>
    api.get<{ lives_remaining: number; total_deaths: number; death_log: unknown[]; max_lives: number }>(
      `/campaigns/${campaignId}/runs/${runId}/lives`,
    ),
  getIntensityCurve: (campaignId: string, runId: string) =>
    api.get<IntensityCurveResponse>(
      `/campaigns/${campaignId}/runs/${runId}/intensity-curve`,
    ),
};

export const floorsApi = {
  list: (runId: string) =>
    api.get<FloorResponse[]>(`/runs/${runId}/floors`),
  start: (runId: string, data?: { arena_count?: number }) =>
    api.post<FloorResponse>(`/runs/${runId}/floors`, data || {}),
  getActive: (runId: string) =>
    api.get<FloorResponse | null>(`/runs/${runId}/floors/active`),
  complete: (runId: string, floorId: string) =>
    api.post(`/runs/${runId}/floors/${floorId}/complete`),
};

export const arenasApi = {
  list: (floorId: string) =>
    api.get<ArenaResponse[]>(`/floors/${floorId}/arenas`),
  start: (floorId: string) =>
    api.post<ArenaResponse>(`/floors/${floorId}/arenas`),
  getActive: (floorId: string) =>
    api.get<ArenaResponse | null>(`/floors/${floorId}/arenas/active`),
  complete: (floorId: string, arenaId: string) =>
    api.post<{
      message: string;
      gold_per_player: number;
      xp_award: number;
      leveled_characters: { character_id: string; name: string; new_level: number }[];
    }>(`/floors/${floorId}/arenas/${arenaId}/complete`),
  listCreatures: (floorId: string, arenaId: string) =>
    api.get<ArenaCreatureStatus[]>(`/floors/${floorId}/arenas/${arenaId}/creatures`),
  updateCreatureStatus: (floorId: string, arenaId: string, creatureId: string, status: string) =>
    api.patch<ArenaCreatureStatus>(
      `/floors/${floorId}/arenas/${arenaId}/creatures/${creatureId}/status`,
      { status },
    ),
};
