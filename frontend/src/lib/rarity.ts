export type Rarity = "common" | "uncommon" | "rare" | "very_rare" | "legendary";

export interface RarityConfig {
  label: string;
  /** Tailwind text color class */
  text: string;
  /** Tailwind border color class */
  border: string;
  /** Tailwind background class */
  bg: string;
  /** Box-shadow glow string */
  glow: string;
  /** Badge color key (for the Badge component) */
  badge: "gray" | "emerald" | "blue" | "purple" | "gold";
  /** Hex color for particle effects */
  particleColor: string;
  /** CSS animation class for frame effect */
  frameAnimation: string;
}

const RARITY_CONFIGS: Record<Rarity, RarityConfig> = {
  common: {
    label: "Common",
    text: "text-gray-300",
    border: "border-gray-500/40",
    bg: "bg-gray-700/20",
    glow: "",
    badge: "gray",
    particleColor: "#9CA3AF",
    frameAnimation: "",
  },
  uncommon: {
    label: "Uncommon",
    text: "text-emerald-300",
    border: "border-emerald-500/40",
    bg: "bg-emerald-900/15",
    glow: "shadow-[0_0_16px_rgba(34,197,94,0.2)]",
    badge: "emerald",
    particleColor: "#22C55E",
    frameAnimation: "",
  },
  rare: {
    label: "Rare",
    text: "text-blue-300",
    border: "border-blue-500/40",
    bg: "bg-blue-900/15",
    glow: "shadow-[0_0_16px_rgba(59,130,246,0.25)]",
    badge: "blue",
    particleColor: "#3B82F6",
    frameAnimation: "rarity-glow-static",
  },
  very_rare: {
    label: "Very Rare",
    text: "text-purple-300",
    border: "border-purple-500/40",
    bg: "bg-purple-900/15",
    glow: "shadow-[0_0_20px_rgba(168,85,247,0.3)]",
    badge: "purple",
    particleColor: "#A855F7",
    frameAnimation: "rarity-glow-pulse",
  },
  legendary: {
    label: "Legendary",
    text: "text-amber-300",
    border: "border-amber-500/40",
    bg: "bg-amber-900/15",
    glow: "shadow-[0_0_24px_rgba(245,158,11,0.35)]",
    badge: "gold",
    particleColor: "#F59E0B",
    frameAnimation: "rarity-border-rotate",
  },
};

const DEFAULT_CONFIG: RarityConfig = RARITY_CONFIGS.common;

/** Normalize rarity strings from the backend (handles both "very_rare" and "very rare") */
function normalizeRarity(rarity: string): Rarity {
  const key = rarity.toLowerCase().replace(/\s+/g, "_") as Rarity;
  return key in RARITY_CONFIGS ? key : "common";
}

/** Get the full rarity configuration for a given rarity string */
export function getRarityConfig(rarity: string): RarityConfig {
  return RARITY_CONFIGS[normalizeRarity(rarity)] ?? DEFAULT_CONFIG;
}

/** Get just the label for display */
export function getRarityLabel(rarity: string): string {
  return getRarityConfig(rarity).label;
}

/** All rarity keys in ascending order */
export const RARITY_ORDER: Rarity[] = ["common", "uncommon", "rare", "very_rare", "legendary"];
