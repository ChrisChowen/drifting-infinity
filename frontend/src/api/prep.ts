import { api } from "./client";
import type { NarrativeContent } from "./runs";

export interface PrepArenaSummary {
  arena_id: string;
  arena_number: number;
  template: string;
  difficulty_tier: string;
  danger_rating: string;
  environment: string;
  environment_name: string;
  creature_count: number;
  xp_budget: number;
  objective_name: string;
  read_aloud_text: string;
  encounter_hook: string;
  creatures: { name: string; count: number; cr: number; tactical_role: string }[];
}

export interface PrepFloorGenerateResponse {
  floor_id: string;
  floor_number: number;
  arena_count: number;
  arenas: PrepArenaSummary[];
}

export interface PrepArenaDetail {
  arena: {
    id: string;
    floor_id: string;
    arena_number: number;
    encounter_template: string | null;
    xp_budget: number | null;
    adjusted_xp: number | null;
    tactical_brief: string | null;
    environment: string | null;
    is_active: boolean;
    is_complete: boolean;
    dm_notes: string | null;
    custom_read_aloud: string | null;
    narrative_content: NarrativeContent | null;
    [key: string]: unknown;
  };
  creatures: {
    id: string;
    monster_id: string;
    instance_label: string;
    status: string;
    is_reinforcement: boolean;
  }[];
}

export interface PrepFloorResponse {
  floor_id: string;
  floor_number: number;
  arena_count: number;
  arenas_completed: number;
  is_complete: boolean;
  active_affixes: string[];
  templates_used: string[];
  objectives_used: string[];
  arenas: PrepArenaDetail[];
}

export const prepApi = {
  generateFloor: (floorId: string) =>
    api.post<PrepFloorGenerateResponse>(`/prep/floor/${floorId}/generate`),

  getFloor: (floorId: string) =>
    api.get<PrepFloorResponse>(`/prep/floor/${floorId}`),

  regenerateArena: (
    floorId: string,
    arenaNumber: number,
    params?: { difficulty?: string; template?: string; environment?: string },
  ) => {
    const query = new URLSearchParams();
    if (params?.difficulty) query.set("difficulty", params.difficulty);
    if (params?.template) query.set("template", params.template);
    if (params?.environment) query.set("environment", params.environment);
    const qs = query.toString();
    return api.post<PrepArenaSummary>(
      `/prep/floor/${floorId}/regenerate/${arenaNumber}${qs ? `?${qs}` : ""}`,
    );
  },

  updateNotes: (floorId: string, arenaId: string, data: { dm_notes?: string; custom_read_aloud?: string }) =>
    api.patch(`/prep/floor/${floorId}/arenas/${arenaId}/notes`, data),
};
