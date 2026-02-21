export type BalancePreset = "relaxed" | "standard" | "challenging" | "brutal";

export interface CampaignSettings {
  balance_preset: BalancePreset;
  leveling_speed: number;
  difficulty_multiplier: number;
  gold_multiplier: number;
  shard_multiplier: number;
  xp_budget_multiplier: number;
  early_game_scaling_factor: number;
  first_run_bonus_lives: number;
  armillary_aggression: number;
  shop_frequency: number;
  max_level: number;
  environment_preference: string | null;
}

export const DEFAULT_SETTINGS: CampaignSettings = {
  balance_preset: "standard",
  leveling_speed: 1.0,
  difficulty_multiplier: 1.0,
  gold_multiplier: 1.0,
  shard_multiplier: 1.0,
  xp_budget_multiplier: 1.0,
  early_game_scaling_factor: 0.85,
  first_run_bonus_lives: 1,
  armillary_aggression: 1.0,
  shop_frequency: 0.3,
  max_level: 20,
  environment_preference: null,
};

export interface SettingMeta {
  key: keyof CampaignSettings;
  label: string;
  description: string;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
  category: "balance" | "economy" | "other";
}

export const SETTING_META: SettingMeta[] = [
  // Balance category — core difficulty tuning
  {
    key: "difficulty_multiplier",
    label: "Difficulty",
    description: "Scales encounter XP budgets. Lower = easier encounters, higher = harder.",
    min: 0.5, max: 2.0, step: 0.1,
    format: (v) => `${v.toFixed(1)}x`,
    category: "balance",
  },
  {
    key: "xp_budget_multiplier",
    label: "XP Budget",
    description: "Additional multiplier on encounter XP budgets. Fine-tunes combat difficulty.",
    min: 0.5, max: 2.0, step: 0.05,
    format: (v) => `${v.toFixed(2)}x`,
    category: "balance",
  },
  {
    key: "early_game_scaling_factor",
    label: "Early Game Scaling",
    description: "Multiplier for floors 1-5 XP budgets. Below 1.0 = easier early game.",
    min: 0.5, max: 1.5, step: 0.05,
    format: (v) => `${v.toFixed(2)}x`,
    category: "balance",
  },
  {
    key: "armillary_aggression",
    label: "Armillary Aggression",
    description: "Controls how hostile the Armillary is. Below 1.0 = fewer hostile events.",
    min: 0.5, max: 2.0, step: 0.1,
    format: (v) => `${v.toFixed(1)}x`,
    category: "balance",
  },
  {
    key: "first_run_bonus_lives",
    label: "First Run Bonus Lives",
    description: "Extra lives granted on a campaign's first run to help new players.",
    min: 0, max: 3, step: 1,
    format: (v) => `+${v}`,
    category: "balance",
  },
  // Economy category
  {
    key: "leveling_speed",
    label: "Leveling Speed",
    description: "Multiplier for XP gained. Below 1.0 = slower, above 1.0 = faster.",
    min: 0.25, max: 4.0, step: 0.25,
    format: (v) => `${v}x`,
    category: "economy",
  },
  {
    key: "gold_multiplier",
    label: "Gold Rewards",
    description: "Scales gold rewards from encounters and arena completion.",
    min: 0.25, max: 4.0, step: 0.25,
    format: (v) => `${v}x`,
    category: "economy",
  },
  {
    key: "shard_multiplier",
    label: "Shard Rewards",
    description: "Scales Astral Shard rewards from encounters.",
    min: 0.25, max: 4.0, step: 0.25,
    format: (v) => `${v}x`,
    category: "economy",
  },
  // Other category
  {
    key: "shop_frequency",
    label: "Shop Frequency",
    description: "Chance of the wandering merchant appearing between arenas.",
    min: 0.0, max: 1.0, step: 0.05,
    format: (v) => `${Math.round(v * 100)}%`,
    category: "other",
  },
  {
    key: "max_level",
    label: "Max Character Level",
    description: "Level cap for characters in this campaign.",
    min: 1, max: 20, step: 1,
    format: (v) => `${v}`,
    category: "other",
  },
];

export const ENVIRONMENTS = [
  { key: "", label: "No Preference (Auto)" },
  { key: "forest", label: "Dense Forest" },
  { key: "grassland", label: "Open Grassland" },
  { key: "urban", label: "Urban Streets" },
  { key: "underdark", label: "Underdark Caverns" },
  { key: "mountain", label: "Mountain Pass" },
  { key: "swamp", label: "Murky Swamp" },
  { key: "coastal", label: "Rocky Coast" },
  { key: "desert", label: "Scorching Desert" },
  { key: "arctic", label: "Frozen Wastes" },
  { key: "hill", label: "Rolling Hills" },
  { key: "planar", label: "Planar Rift" },
  { key: "underwater", label: "Underwater Depths" },
];

export const PRESETS: { name: string; preset: BalancePreset; description: string; settings: Partial<CampaignSettings> }[] = [
  {
    name: "Relaxed",
    preset: "relaxed",
    description: "Easier encounters, faster leveling, more gold. Great for casual tables or new players.",
    settings: {
      balance_preset: "relaxed",
      leveling_speed: 1.2, difficulty_multiplier: 0.8, gold_multiplier: 1.3,
      xp_budget_multiplier: 0.85, early_game_scaling_factor: 0.75,
      first_run_bonus_lives: 2, armillary_aggression: 0.7,
    },
  },
  {
    name: "Standard",
    preset: "standard",
    description: "Balanced experience with a forgiving early game. Recommended for most groups.",
    settings: {
      balance_preset: "standard",
      leveling_speed: 1.0, difficulty_multiplier: 1.0, gold_multiplier: 1.0,
      xp_budget_multiplier: 1.0, early_game_scaling_factor: 0.85,
      first_run_bonus_lives: 1, armillary_aggression: 1.0,
    },
  },
  {
    name: "Challenging",
    preset: "challenging",
    description: "Harder encounters, tighter economy, no safety net. For experienced parties.",
    settings: {
      balance_preset: "challenging",
      leveling_speed: 0.9, difficulty_multiplier: 1.15, gold_multiplier: 0.9,
      xp_budget_multiplier: 1.1, early_game_scaling_factor: 0.95,
      first_run_bonus_lives: 0, armillary_aggression: 1.2,
    },
  },
  {
    name: "Brutal",
    preset: "brutal",
    description: "Punishing difficulty, scarce resources, hostile Armillary. Expect death.",
    settings: {
      balance_preset: "brutal",
      leveling_speed: 0.8, difficulty_multiplier: 1.3, gold_multiplier: 0.75,
      xp_budget_multiplier: 1.25, early_game_scaling_factor: 1.0,
      first_run_bonus_lives: 0, armillary_aggression: 1.5,
    },
  },
];
