import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  metaApi,
  type MetaResponse,
  type TalentResponse,
  type AchievementResponse,
  type LoreFragmentResponse,
  type LoreBeatResponse,
  type RunEndMetaResponse,
} from "@/api/meta";

interface MetaState {
  // Data
  meta: MetaResponse | null;
  talents: TalentResponse[];
  talentEssence: number;
  achievements: AchievementResponse[];
  lore: LoreFragmentResponse[];
  loreBeats: LoreBeatResponse[];
  lastRunMeta: RunEndMetaResponse | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchMeta: (campaignId: string) => Promise<void>;
  fetchTalents: (campaignId: string) => Promise<void>;
  unlockTalent: (campaignId: string, talentId: string) => Promise<void>;
  fetchAchievements: (campaignId: string) => Promise<void>;
  fetchLore: (campaignId: string) => Promise<void>;
  fetchLoreBeats: (campaignId: string, floorNumber: number, trigger?: string) => Promise<void>;
  completeRunMeta: (campaignId: string, runId: string) => Promise<RunEndMetaResponse>;
  clearLastRunMeta: () => void;
}

export const useMetaStore = create<MetaState>()(
  persist(
    (set, _get) => ({
      meta: null,
      talents: [],
      talentEssence: 0,
      achievements: [],
      lore: [],
      loreBeats: [],
      lastRunMeta: null,
      loading: false,
      error: null,

      fetchMeta: async (campaignId) => {
        set({ loading: true, error: null });
        try {
          const meta = await metaApi.get(campaignId);
          set({ meta, loading: false });
        } catch (e) {
          set({ error: String(e), loading: false });
        }
      },

      fetchTalents: async (campaignId) => {
        set({ loading: true, error: null });
        try {
          const result = await metaApi.getTalents(campaignId);
          set({ talents: result.talents, talentEssence: result.essence_balance, loading: false });
        } catch (e) {
          set({ error: String(e), loading: false });
        }
      },

      unlockTalent: async (campaignId, talentId) => {
        set({ loading: true, error: null });
        try {
          const result = await metaApi.unlockTalent(campaignId, talentId);
          set({ talents: result.talents, talentEssence: result.essence_balance, loading: false });
          // Also refresh meta to keep essence_balance in sync
          const meta = await metaApi.get(campaignId);
          set({ meta });
        } catch (e) {
          set({ error: String(e), loading: false });
        }
      },

      fetchAchievements: async (campaignId) => {
        set({ loading: true, error: null });
        try {
          const achievements = await metaApi.getAchievements(campaignId);
          set({ achievements, loading: false });
        } catch (e) {
          set({ error: String(e), loading: false });
        }
      },

      fetchLore: async (campaignId) => {
        set({ loading: true, error: null });
        try {
          const lore = await metaApi.getLore(campaignId);
          set({ lore, loading: false });
        } catch (e) {
          set({ error: String(e), loading: false });
        }
      },

      fetchLoreBeats: async (campaignId, floorNumber, trigger) => {
        try {
          const beats = await metaApi.getLoreBeats(campaignId, floorNumber, trigger);
          set({ loreBeats: beats });
        } catch (e) {
          console.error("[MetaStore] Failed to fetch lore beats:", e);
        }
      },

      completeRunMeta: async (campaignId, runId) => {
        set({ loading: true, error: null });
        try {
          const result = await metaApi.completeRunMeta(campaignId, runId);
          set({ lastRunMeta: result, loading: false });
          // Refresh meta
          const meta = await metaApi.get(campaignId);
          set({ meta });
          return result;
        } catch (e) {
          set({ error: String(e), loading: false });
          throw e;
        }
      },

      clearLastRunMeta: () => set({ lastRunMeta: null }),
    }),
    {
      name: "drifting-infinity-meta",
      version: 1,
      partialize: (state) => ({
        meta: state.meta,
        lastRunMeta: state.lastRunMeta,
      }),
      migrate: (persisted, version) => {
        if (version === 0) {
          return { meta: null, lastRunMeta: null };
        }
        return persisted as { meta: MetaResponse | null; lastRunMeta: RunEndMetaResponse | null };
      },
    },
  ),
);
