export interface ParticlePreset {
  /** Max number of particles alive at once */
  count: number;
  /** Particle colors (randomly picked) */
  colors: string[];
  /** Min/max size in px */
  sizeRange: [number, number];
  /** Min/max speed in px/s (positive = up, negative = down) */
  speedYRange: [number, number];
  /** Min/max horizontal drift in px/s */
  speedXRange: [number, number];
  /** Min/max opacity */
  opacityRange: [number, number];
  /** Min/max lifetime in seconds */
  lifetimeRange: [number, number];
  /** Spawn rate — new particles per second */
  spawnRate: number;
}

export const PARTICLE_PRESETS: Record<string, ParticlePreset> = {
  arcane_dust: {
    count: 30,
    colors: ["#C4A962", "#A78BFA", "#D4AF37", "#9F7AEA"],
    sizeRange: [1.5, 3],
    speedYRange: [-18, -8],
    speedXRange: [-4, 4],
    opacityRange: [0.15, 0.5],
    lifetimeRange: [4, 8],
    spawnRate: 4,
  },

  combat_embers: {
    count: 40,
    colors: ["#EF4444", "#F97316", "#FBBF24", "#DC2626"],
    sizeRange: [1, 2.5],
    speedYRange: [-30, -12],
    speedXRange: [-8, 8],
    opacityRange: [0.3, 0.7],
    lifetimeRange: [2, 5],
    spawnRate: 8,
  },

  vault_shimmer: {
    count: 25,
    colors: ["#E0E7FF", "#C7D2FE", "#A5B4FC", "#D4AF37"],
    sizeRange: [1, 2],
    speedYRange: [-10, -4],
    speedXRange: [-3, 3],
    opacityRange: [0.2, 0.55],
    lifetimeRange: [3, 7],
    spawnRate: 4,
  },

  descent_fog: {
    count: 20,
    colors: ["#6B7280", "#9CA3AF", "#4B5563"],
    sizeRange: [3, 6],
    speedYRange: [6, 16],
    speedXRange: [-6, 6],
    opacityRange: [0.06, 0.18],
    lifetimeRange: [5, 10],
    spawnRate: 2,
  },

  // Environment-specific presets
  frost_motes: {
    count: 25,
    colors: ["#BAE6FD", "#E0F2FE", "#7DD3FC", "#FFFFFF"],
    sizeRange: [1, 2.5],
    speedYRange: [4, 12],
    speedXRange: [-6, 6],
    opacityRange: [0.2, 0.6],
    lifetimeRange: [4, 9],
    spawnRate: 3,
  },

  forest_motes: {
    count: 20,
    colors: ["#86EFAC", "#4ADE80", "#BBF7D0", "#D9F99D"],
    sizeRange: [1, 2],
    speedYRange: [-6, -2],
    speedXRange: [-5, 5],
    opacityRange: [0.15, 0.4],
    lifetimeRange: [5, 10],
    spawnRate: 3,
  },

  fey_sparkle: {
    count: 35,
    colors: ["#C084FC", "#F0ABFC", "#86EFAC", "#FDE68A", "#E9D5FF"],
    sizeRange: [1, 2.5],
    speedYRange: [-14, -4],
    speedXRange: [-6, 6],
    opacityRange: [0.25, 0.7],
    lifetimeRange: [3, 6],
    spawnRate: 6,
  },

  shadow_wisps: {
    count: 15,
    colors: ["#374151", "#4B5563", "#1F2937", "#6B7280"],
    sizeRange: [2, 5],
    speedYRange: [-8, -2],
    speedXRange: [-3, 3],
    opacityRange: [0.08, 0.2],
    lifetimeRange: [6, 12],
    spawnRate: 2,
  },

  swamp_haze: {
    count: 18,
    colors: ["#6EE7B7", "#34D399", "#6B7280", "#A7F3D0"],
    sizeRange: [3, 6],
    speedYRange: [-4, 4],
    speedXRange: [-5, 5],
    opacityRange: [0.06, 0.15],
    lifetimeRange: [6, 12],
    spawnRate: 2,
  },

  sand_drift: {
    count: 30,
    colors: ["#FCD34D", "#FDE68A", "#D4AF37", "#B45309"],
    sizeRange: [1, 2],
    speedYRange: [-6, 6],
    speedXRange: [4, 16],
    opacityRange: [0.15, 0.35],
    lifetimeRange: [3, 6],
    spawnRate: 5,
  },

  aquatic_bubbles: {
    count: 20,
    colors: ["#22D3EE", "#67E8F9", "#A5F3FC", "#CFFAFE"],
    sizeRange: [1.5, 3],
    speedYRange: [-12, -4],
    speedXRange: [-3, 3],
    opacityRange: [0.15, 0.45],
    lifetimeRange: [4, 8],
    spawnRate: 3,
  },

  planar_rift: {
    count: 30,
    colors: ["#C084FC", "#F472B6", "#A78BFA", "#818CF8", "#E879F9"],
    sizeRange: [1, 3],
    speedYRange: [-20, -6],
    speedXRange: [-8, 8],
    opacityRange: [0.2, 0.55],
    lifetimeRange: [3, 7],
    spawnRate: 5,
  },

  celestial_glow: {
    count: 25,
    colors: ["#FDE68A", "#FEF9C3", "#93C5FD", "#BFDBFE", "#FFFBEB"],
    sizeRange: [1, 2.5],
    speedYRange: [-8, -2],
    speedXRange: [-2, 2],
    opacityRange: [0.2, 0.6],
    lifetimeRange: [5, 10],
    spawnRate: 3,
  },

  mountain_dust: {
    count: 15,
    colors: ["#94A3B8", "#CBD5E1", "#64748B", "#E2E8F0"],
    sizeRange: [2, 4],
    speedYRange: [-4, 8],
    speedXRange: [-8, 8],
    opacityRange: [0.08, 0.2],
    lifetimeRange: [5, 10],
    spawnRate: 2,
  },
};

export type ParticlePresetKey = keyof typeof PARTICLE_PRESETS;
