import { api } from "./client";

// ── Response Types ──────────────────────────────────────────────────────────

export interface MetaResponse {
  essence_balance: number;
  essence_lifetime: number;
  unlocked_talents: string[];
  achievements: string[];
  total_runs_completed: number;
  total_runs_won: number;
  highest_floor_reached: number;
  total_floors_cleared: number;
  total_deaths_all_runs: number;
  secret_floors_discovered: string[];
  lore_fragments_found: string[];
  antagonist_encounters: number;
}

export interface TalentResponse {
  id: string;
  name: string;
  branch: string;
  tier: number;
  cost: number;
  effect_key: string;
  description: string;
  is_unlocked: boolean;
  can_afford: boolean;
  prerequisite_met: boolean;
}

export interface TalentTreeResponse {
  talents: TalentResponse[];
  essence_balance: number;
}

export interface AchievementResponse {
  id: string;
  name: string;
  description: string;
  category: string;
  essence_reward: number;
  is_earned: boolean;
}

export interface LoreFragmentResponse {
  id: string;
  title: string;
  text: string;
  category: string;
  source: string;
  is_discovered: boolean;
}

export interface LoreBeatResponse {
  id: string;
  floor: number;
  act: number;
  trigger: string;
  arbiter_text: string;
  aethon_text: string;
  dm_stage_direction: string;
  lore_fragment_id: string | null;
}

export interface RunEndMetaResponse {
  essence_earned: number;
  new_achievements: AchievementResponse[];
  lore_fragments_discovered: LoreFragmentResponse[];
  total_essence: number;
  talents_affordable: number;
}

// ── API Client ──────────────────────────────────────────────────────────────

export const metaApi = {
  /** Get campaign meta-progression overview (auto-creates if missing) */
  get: (campaignId: string) =>
    api.get<MetaResponse>(`/campaigns/${campaignId}/meta`),

  /** Get the full talent tree with unlock/affordability status */
  getTalents: (campaignId: string) =>
    api.get<TalentTreeResponse>(`/campaigns/${campaignId}/meta/talents`),

  /** Spend essence to unlock a talent */
  unlockTalent: (campaignId: string, talentId: string) =>
    api.post<TalentTreeResponse>(
      `/campaigns/${campaignId}/meta/talents/${talentId}/unlock`,
    ),

  /** Get all achievements with earned/unearned status */
  getAchievements: (campaignId: string) =>
    api.get<AchievementResponse[]>(`/campaigns/${campaignId}/meta/achievements`),

  /** Get all lore fragments with discovered/undiscovered status */
  getLore: (campaignId: string) =>
    api.get<LoreFragmentResponse[]>(`/campaigns/${campaignId}/meta/lore`),

  /** Get lore beats for a specific floor and trigger */
  getLoreBeats: (campaignId: string, floorNumber: number, trigger = "floor_end") =>
    api.get<LoreBeatResponse[]>(
      `/campaigns/${campaignId}/meta/lore-beats/${floorNumber}?trigger=${trigger}`,
    ),

  /** Complete a run and compute meta-progression rewards */
  completeRunMeta: (campaignId: string, runId: string) =>
    api.post<RunEndMetaResponse>(
      `/campaigns/${campaignId}/runs/${runId}/complete-meta`,
    ),
};
