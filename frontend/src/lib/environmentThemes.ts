import type { ParticlePresetKey } from "@/components/effects/particlePresets";

export interface EnvironmentTheme {
  /** Background gradient CSS for the layout */
  gradient: string;
  /** Particle preset to use */
  particles: ParticlePresetKey;
  /** Accent color override (CSS color) */
  accent: string;
  /** Label for display */
  label: string;
}

/**
 * Map environment keys → biome, then biome → visual theme.
 * Environments not explicitly mapped fall back to the "default" theme.
 */
const ENVIRONMENT_TO_BIOME: Record<string, string> = {
  // arctic
  arctic: "arctic",
  frozen_lake: "arctic",
  // forest
  forest: "forest",
  fungal_forest: "forest",
  feywild_glade: "feywild",
  // underground
  underdark: "underdark",
  crystal_caverns: "underdark",
  lava_tubes: "volcanic",
  sewer_catacomb: "underdark",
  // water
  coastal: "water",
  underwater: "water",
  swamp: "swamp",
  // mountain
  mountain: "mountain",
  volcanic_caldera: "volcanic",
  // urban
  urban: "urban",
  haunted_ruins: "haunted",
  temple_interior: "urban",
  ship_deck: "water",
  // desert
  desert: "desert",
  // plains
  grassland: "plains",
  hill: "plains",
  // planar
  planar: "planar",
  elemental_nexus: "planar",
  shadowfell_wastes: "shadowfell",
  cloud_palace: "celestial",
};

const BIOME_THEMES: Record<string, EnvironmentTheme> = {
  arctic: {
    gradient: "radial-gradient(ellipse at top, rgba(56, 189, 248, 0.06) 0%, transparent 50%)",
    particles: "frost_motes",
    accent: "#7DD3FC",
    label: "Frozen Wastes",
  },
  forest: {
    gradient: "radial-gradient(ellipse at top, rgba(34, 197, 94, 0.05) 0%, transparent 50%)",
    particles: "forest_motes",
    accent: "#86EFAC",
    label: "Dense Wilds",
  },
  feywild: {
    gradient: "radial-gradient(ellipse at top, rgba(168, 85, 247, 0.06) 0%, rgba(34, 197, 94, 0.03) 30%, transparent 60%)",
    particles: "fey_sparkle",
    accent: "#C084FC",
    label: "Feywild",
  },
  underdark: {
    gradient: "radial-gradient(ellipse at top, rgba(139, 92, 246, 0.06) 0%, transparent 50%)",
    particles: "arcane_dust",
    accent: "#A78BFA",
    label: "Underdark",
  },
  volcanic: {
    gradient: "radial-gradient(ellipse at top, rgba(239, 68, 68, 0.06) 0%, rgba(249, 115, 22, 0.03) 30%, transparent 60%)",
    particles: "combat_embers",
    accent: "#F97316",
    label: "Volcanic",
  },
  water: {
    gradient: "radial-gradient(ellipse at top, rgba(56, 189, 248, 0.05) 0%, rgba(6, 182, 212, 0.03) 30%, transparent 60%)",
    particles: "aquatic_bubbles",
    accent: "#22D3EE",
    label: "Aquatic",
  },
  swamp: {
    gradient: "radial-gradient(ellipse at top, rgba(34, 197, 94, 0.04) 0%, rgba(107, 114, 128, 0.04) 30%, transparent 60%)",
    particles: "swamp_haze",
    accent: "#6EE7B7",
    label: "Murky Swamp",
  },
  mountain: {
    gradient: "radial-gradient(ellipse at top, rgba(148, 163, 184, 0.06) 0%, transparent 50%)",
    particles: "mountain_dust",
    accent: "#94A3B8",
    label: "Mountain",
  },
  urban: {
    gradient: "radial-gradient(ellipse at top, rgba(99, 102, 241, 0.05) 0%, transparent 50%)",
    particles: "arcane_dust",
    accent: "#A5B4FC",
    label: "Urban",
  },
  haunted: {
    gradient: "radial-gradient(ellipse at top, rgba(107, 114, 128, 0.06) 0%, rgba(139, 92, 246, 0.03) 30%, transparent 60%)",
    particles: "shadow_wisps",
    accent: "#9CA3AF",
    label: "Haunted",
  },
  desert: {
    gradient: "radial-gradient(ellipse at top, rgba(245, 158, 11, 0.05) 0%, transparent 50%)",
    particles: "sand_drift",
    accent: "#FCD34D",
    label: "Desert",
  },
  plains: {
    gradient: "radial-gradient(ellipse at top, rgba(34, 197, 94, 0.04) 0%, transparent 50%)",
    particles: "forest_motes",
    accent: "#86EFAC",
    label: "Open Plains",
  },
  planar: {
    gradient: "radial-gradient(ellipse at top, rgba(168, 85, 247, 0.07) 0%, rgba(236, 72, 153, 0.03) 30%, transparent 60%)",
    particles: "planar_rift",
    accent: "#C084FC",
    label: "Planar Rift",
  },
  shadowfell: {
    gradient: "radial-gradient(ellipse at top, rgba(107, 114, 128, 0.06) 0%, rgba(0, 0, 0, 0.04) 30%, transparent 60%)",
    particles: "shadow_wisps",
    accent: "#6B7280",
    label: "Shadowfell",
  },
  celestial: {
    gradient: "radial-gradient(ellipse at top, rgba(253, 224, 71, 0.05) 0%, rgba(147, 197, 253, 0.03) 30%, transparent 60%)",
    particles: "celestial_glow",
    accent: "#FDE68A",
    label: "Celestial",
  },
};

const DEFAULT_THEME: EnvironmentTheme = {
  gradient: "radial-gradient(ellipse at top, rgba(99, 102, 241, 0.04) 0%, transparent 50%)",
  particles: "arcane_dust",
  accent: "#C4A962",
  label: "The Nexus",
};

/**
 * Get the visual theme for a given environment key.
 * Falls back to default if the environment isn't mapped.
 */
export function getEnvironmentTheme(environmentKey: string | null | undefined): EnvironmentTheme {
  if (!environmentKey) return DEFAULT_THEME;
  const biome = ENVIRONMENT_TO_BIOME[environmentKey];
  if (!biome) return DEFAULT_THEME;
  return BIOME_THEMES[biome] ?? DEFAULT_THEME;
}
