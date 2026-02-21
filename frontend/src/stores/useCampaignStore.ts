import { create } from "zustand";
import { persist } from "zustand/middleware";
import { campaignsApi, type CampaignResponse, type CharacterResponse, type CharacterCreatePayload } from "@/api/campaigns";

interface CampaignState {
  campaigns: CampaignResponse[];
  activeCampaignId: string | null;
  characters: CharacterResponse[];
  loading: boolean;
  error: string | null;

  fetchCampaigns: () => Promise<void>;
  createCampaign: (name: string) => Promise<CampaignResponse>;
  setActiveCampaign: (id: string) => Promise<void>;
  fetchCharacters: () => Promise<void>;
  addCharacter: (data: CharacterCreatePayload) => Promise<void>;
  removeCharacter: (charId: string) => Promise<void>;

  get activeCampaign(): CampaignResponse | undefined;
}

export const useCampaignStore = create<CampaignState>()(
  persist(
    (set, get) => ({
      campaigns: [],
      activeCampaignId: null,
      characters: [],
      loading: false,
      error: null,

      get activeCampaign() {
        return get().campaigns.find((c) => c.id === get().activeCampaignId);
      },

      fetchCampaigns: async () => {
        set({ loading: true, error: null });
        try {
          const campaigns = await campaignsApi.list();
          set({ campaigns, loading: false });
        } catch (e) {
          set({ error: String(e), loading: false });
        }
      },

      createCampaign: async (name) => {
        const campaign = await campaignsApi.create(name);
        set((s) => ({ campaigns: [campaign, ...s.campaigns] }));
        return campaign;
      },

      setActiveCampaign: async (id) => {
        set({ activeCampaignId: id });
        const chars = await campaignsApi.listCharacters(id);
        set({ characters: chars });
      },

      fetchCharacters: async () => {
        const { activeCampaignId } = get();
        if (!activeCampaignId) return;
        const chars = await campaignsApi.listCharacters(activeCampaignId);
        set({ characters: chars });
      },

      addCharacter: async (data) => {
        const { activeCampaignId } = get();
        if (!activeCampaignId) return;
        const char = await campaignsApi.createCharacter(activeCampaignId, data);
        set((s) => ({ characters: [...s.characters, char] }));
      },

      removeCharacter: async (charId) => {
        const { activeCampaignId } = get();
        if (!activeCampaignId) return;
        await campaignsApi.deleteCharacter(activeCampaignId, charId);
        set((s) => ({ characters: s.characters.filter((c) => c.id !== charId) }));
      },
    }),
    {
      name: "drifting-infinity-campaign",
      version: 1,
      partialize: (state) => ({
        activeCampaignId: state.activeCampaignId,
      }),
      migrate: (persisted, version) => {
        if (version === 0) {
          return { activeCampaignId: (persisted as { activeCampaignId?: string })?.activeCampaignId ?? null };
        }
        return persisted as { activeCampaignId: string | null };
      },
      onRehydrateStorage: () => {
        // After store rehydrates from localStorage, auto-fetch campaigns & characters
        return (state) => {
          if (state?.activeCampaignId) {
            // Fetch campaigns list so sidebar/selectors have data
            state.fetchCampaigns().then(() => {
              // Fetch characters for the active campaign
              if (state.activeCampaignId) {
                state.fetchCharacters();
              }
            }).catch(() => {
              // Silently fail — backend might not be running yet
            });
          }
        };
      },
    }
  )
);
