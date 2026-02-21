import { create } from "zustand";
import { runsApi, floorsApi, arenasApi, type RunResponse, type FloorResponse, type ArenaResponse } from "@/api/runs";
import { encountersApi, type EncounterProposal } from "@/api/encounters";
import { campaignsApi } from "@/api/campaigns";
import type { RunPhase } from "@/types/run";

interface RunState {
  phase: RunPhase;
  run: RunResponse | null;
  floor: FloorResponse | null;
  arena: ArenaResponse | null;
  encounter: EncounterProposal | null;
  loading: boolean;
  livesRemaining: number;
  totalDeaths: number;

  startRun: (campaignId: string, level?: number, floors?: number) => Promise<void>;
  startFloor: (arenaCount?: number) => Promise<void>;
  startArena: () => Promise<void>;
  generateEncounter: (opts?: { difficulty?: string; template?: string; environment?: string }) => Promise<void>;
  approveEncounter: () => Promise<void>;
  completeArena: () => Promise<void>;
  completeFloor: () => Promise<void>;
  endRun: (campaignId: string, outcome?: string) => Promise<void>;
  setPhase: (phase: RunPhase) => void;
  loadActiveRun: (campaignId: string) => Promise<void>;
  recordDeath: (campaignId: string, characterId: string) => Promise<{ can_respawn: boolean; lives_remaining: number }>;
  reset: () => void;
}

export const useRunStore = create<RunState>()((set, get) => ({
  phase: "lobby",
  run: null,
  floor: null,
  arena: null,
  encounter: null,
  loading: false,
  livesRemaining: 3,
  totalDeaths: 0,

  startRun: async (campaignId, level, floors = 20) => {
    set({ loading: true });
    const run = await runsApi.start(campaignId, { starting_level: level, floor_count: floors });
    set({ run, phase: "setup", loading: false, livesRemaining: run.lives_remaining, totalDeaths: run.total_deaths });
  },

  loadActiveRun: async (campaignId) => {
    const run = await runsApi.getActive(campaignId);
    if (run) {
      set({ run, livesRemaining: run.lives_remaining, totalDeaths: run.total_deaths });
      // Try to load active floor/arena
      const floor = await floorsApi.getActive(run.id);
      if (floor) {
        set({ floor });
        const arena = await arenasApi.getActive(floor.id);
        if (arena) {
          set({ arena, phase: arena.is_active ? "encounter-active" : "encounter-brief" });
        } else {
          set({ phase: "encounter-brief" });
        }
      } else {
        set({ phase: "setup" });
      }
    }
  },

  startFloor: async (arenaCount = 4) => {
    const { run } = get();
    if (!run) return;
    set({ loading: true });
    const floor = await floorsApi.start(run.id, { arena_count: arenaCount });
    set({ floor, loading: false });
  },

  startArena: async () => {
    const { floor } = get();
    if (!floor) return;
    set({ loading: true });
    const arena = await arenasApi.start(floor.id);
    set({ arena, encounter: null, phase: "encounter-brief", loading: false });
  },

  generateEncounter: async (opts) => {
    const { arena } = get();
    if (!arena) return;
    set({ loading: true });
    try {
      const proposal = await encountersApi.generate(arena.id, opts);
      set({ encounter: proposal, loading: false });
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  approveEncounter: async () => {
    const { arena, encounter } = get();
    if (!arena || !encounter) return;
    await encountersApi.approve(arena.id, encounter);
    set({ phase: "encounter-active" });
  },

  completeArena: async () => {
    const { floor, arena } = get();
    if (!floor || !arena) return;
    const result = await arenasApi.complete(floor.id, arena.id);
    set({
      arena: { ...arena, gold_earned_per_player: result.gold_per_player },
      phase: "post-arena",
    });
  },

  completeFloor: async () => {
    const { run, floor } = get();
    if (!run || !floor) return;
    await floorsApi.complete(run.id, floor.id);
    set({ floor: null, arena: null, encounter: null, phase: "floor-transition" });
  },

  endRun: async (campaignId, outcome = "completed") => {
    const { run } = get();
    if (!run) return;
    await runsApi.end(campaignId, run.id, outcome);
    set({ phase: "run-complete" });
  },

  recordDeath: async (campaignId, characterId) => {
    const { run } = get();
    if (!run) throw new Error("No active run");
    const result = await campaignsApi.recordDeath(campaignId, characterId, run.id);
    set({ livesRemaining: result.lives_remaining, totalDeaths: result.total_deaths });
    return result;
  },

  setPhase: (phase) => set({ phase }),
  reset: () => set({ phase: "lobby", run: null, floor: null, arena: null, encounter: null, livesRemaining: 3, totalDeaths: 0 }),
}));
