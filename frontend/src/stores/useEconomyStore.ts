import { create } from "zustand";
import { economyApi } from "@/api/economy";

interface EconomyState {
  goldBalance: number;
  astralShardBalance: number;
  loading: boolean;

  fetchBalance: (campaignId: string) => Promise<void>;
  setBalance: (gold: number, shards: number) => void;
}

export const useEconomyStore = create<EconomyState>()((set) => ({
  goldBalance: 0,
  astralShardBalance: 0,
  loading: false,

  fetchBalance: async (campaignId) => {
    set({ loading: true });
    const balance = await economyApi.getBalance(campaignId);
    set({
      goldBalance: balance.gold_balance,
      astralShardBalance: balance.astral_shard_balance,
      loading: false,
    });
  },

  setBalance: (gold, shards) => set({ goldBalance: gold, astralShardBalance: shards }),
}));
