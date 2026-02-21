import { api } from "./client";
import type { CampaignSettings } from "@/constants/campaignSettings";

export interface CampaignResponse {
  id: string;
  name: string;
  party_power_coefficient: number;
  total_runs: number;
  gold_balance: number;
  astral_shard_balance: number;
  settings: CampaignSettings;
}

export interface CharacterResponse {
  id: string;
  campaign_id: string;
  name: string;
  character_class: string;
  subclass: string | null;
  level: number;
  ac: number;
  max_hp: number;
  speed: number;
  saves: Record<string, number>;
  damage_types: string[];
  capabilities: Record<string, boolean>;
  xp_total: number;
  xp_to_next_level: number;
  variant_id: string | null;
  identity_id: string | null;
  weapon_id: string | null;
  is_dead: boolean;
  death_count: number;
  is_replacement: boolean;
  original_character_id: string | null;
  replaced_by_id: string | null;
}

export interface CharacterCreatePayload {
  name: string;
  character_class: string;
  subclass: string | null;
  level: number;
  ac: number;
  max_hp: number;
  speed: number;
  saves: Record<string, number>;
  damage_types: string[];
  capabilities: Record<string, boolean>;
}

export const campaignsApi = {
  list: () => api.get<CampaignResponse[]>("/campaigns"),
  create: (name: string) => api.post<CampaignResponse>("/campaigns", { name }),
  get: (id: string) => api.get<CampaignResponse>(`/campaigns/${id}`),
  update: (id: string, data: Partial<{ name: string; settings: CampaignSettings }>) =>
    api.patch<CampaignResponse>(`/campaigns/${id}`, data),
  delete: (id: string) => api.delete(`/campaigns/${id}`),

  // Characters
  listCharacters: (campaignId: string) =>
    api.get<CharacterResponse[]>(`/campaigns/${campaignId}/characters`),
  createCharacter: (campaignId: string, data: CharacterCreatePayload) =>
    api.post<CharacterResponse>(`/campaigns/${campaignId}/characters`, data),
  updateCharacter: (campaignId: string, charId: string, data: Partial<CharacterResponse>) =>
    api.patch<CharacterResponse>(`/campaigns/${campaignId}/characters/${charId}`, data),
  deleteCharacter: (campaignId: string, charId: string) =>
    api.delete(`/campaigns/${campaignId}/characters/${charId}`),

  // XP & Leveling
  awardXp: (campaignId: string, charId: string, amount: number) =>
    api.post<CharacterResponse>(`/campaigns/${campaignId}/characters/${charId}/award-xp`, { amount }),
  levelUp: (campaignId: string, charId: string, data: { new_max_hp: number; new_ac: number; new_saves?: Record<string, number>; new_capabilities?: Record<string, boolean> }) =>
    api.post<CharacterResponse>(`/campaigns/${campaignId}/characters/${charId}/level-up`, data),

  // Death & Respawn
  recordDeath: (campaignId: string, charId: string, runId: string) =>
    api.post<{ character_name: string; death_count: number; lives_remaining: number; total_deaths: number; can_respawn: boolean }>(
      `/campaigns/${campaignId}/characters/${charId}/death?run_id=${runId}`,
    ),
  respawnCharacter: (campaignId: string, charId: string, data: CharacterCreatePayload) =>
    api.post<CharacterResponse>(`/campaigns/${campaignId}/characters/${charId}/respawn`, data),
};
