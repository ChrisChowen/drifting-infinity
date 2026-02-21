import { create } from "zustand";
import { arenasApi, type ArenaCreatureStatus } from "@/api/runs";
import { armillaryApi } from "@/api/combat";

interface ArmillaryEffect {
  id: string;
  round_number: number;
  category: string;
  effect_key: string;
  effect_description: string;
  xp_cost: number;
  was_rerolled: boolean;
}

interface ArenaState {
  creatures: ArenaCreatureStatus[];
  armillaryEffects: ArmillaryEffect[];
  armillaryRound: number;
  loading: boolean;

  loadCreatures: (floorId: string, arenaId: string) => Promise<void>;
  updateCreatureStatus: (
    floorId: string,
    arenaId: string,
    creatureId: string,
    status: "alive" | "bloodied" | "defeated",
  ) => Promise<void>;
  loadArmillaryEffects: (arenaId: string) => Promise<void>;
  rollArmillaryEffect: (arenaId: string) => Promise<ArmillaryEffect | null>;
  rerollArmillaryEffect: (arenaId: string, effectId: string) => Promise<ArmillaryEffect | null>;
  reset: () => void;
}

export const useArenaStore = create<ArenaState>()((set, get) => ({
  creatures: [],
  armillaryEffects: [],
  armillaryRound: 1,
  loading: false,

  loadCreatures: async (floorId, arenaId) => {
    set({ loading: true });
    const creatures = await arenasApi.listCreatures(floorId, arenaId);
    set({ creatures, loading: false });
  },

  updateCreatureStatus: async (floorId, arenaId, creatureId, status) => {
    const updated = await arenasApi.updateCreatureStatus(floorId, arenaId, creatureId, status);
    set({
      creatures: get().creatures.map((c) => (c.id === creatureId ? updated : c)),
    });
  },

  loadArmillaryEffects: async (arenaId) => {
    const effects = (await armillaryApi.list(arenaId)) as ArmillaryEffect[];
    const maxRound = effects.reduce((max, e) => Math.max(max, e.round_number), 0);
    set({ armillaryEffects: effects, armillaryRound: maxRound + 1 });
  },

  rollArmillaryEffect: async (arenaId) => {
    const { armillaryRound } = get();
    const effect = (await armillaryApi.roll(arenaId, armillaryRound)) as ArmillaryEffect;
    set({
      armillaryEffects: [...get().armillaryEffects, effect],
      armillaryRound: armillaryRound + 1,
    });
    return effect;
  },

  rerollArmillaryEffect: async (arenaId, effectId) => {
    const effect = (await armillaryApi.reroll(arenaId, effectId)) as ArmillaryEffect;
    set({
      armillaryEffects: get().armillaryEffects.map((e) => (e.id === effectId ? effect : e)),
    });
    return effect;
  },

  reset: () =>
    set({ creatures: [], armillaryEffects: [], armillaryRound: 1, loading: false }),
}));
