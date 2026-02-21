import { describe, it, expect, vi, beforeEach } from "vitest";
import { useEconomyStore } from "../useEconomyStore";

vi.mock("@/api/economy", () => ({
  economyApi: {
    getBalance: vi.fn(),
  },
}));

import { economyApi } from "@/api/economy";

describe("useEconomyStore", () => {
  beforeEach(() => {
    useEconomyStore.setState({ goldBalance: 0, astralShardBalance: 0, loading: false });
    vi.restoreAllMocks();
  });

  it("has correct initial state", () => {
    const state = useEconomyStore.getState();
    expect(state.goldBalance).toBe(0);
    expect(state.astralShardBalance).toBe(0);
    expect(state.loading).toBe(false);
  });

  it("setBalance updates gold and shards", () => {
    useEconomyStore.getState().setBalance(500, 12);
    const state = useEconomyStore.getState();
    expect(state.goldBalance).toBe(500);
    expect(state.astralShardBalance).toBe(12);
  });

  it("fetchBalance loads from API and updates state", async () => {
    vi.mocked(economyApi.getBalance).mockResolvedValueOnce({
      gold_balance: 1200,
      astral_shard_balance: 7,
    });

    await useEconomyStore.getState().fetchBalance("campaign-1");

    const state = useEconomyStore.getState();
    expect(state.goldBalance).toBe(1200);
    expect(state.astralShardBalance).toBe(7);
    expect(state.loading).toBe(false);
    expect(economyApi.getBalance).toHaveBeenCalledWith("campaign-1");
  });
});
