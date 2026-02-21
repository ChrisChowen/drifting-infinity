import type { Rarity } from "./economy";

export type GachaBanner = "the_armory" | "the_reliquary" | "echoes_of_power";

export interface GachaBannerState {
  banner: GachaBanner;
  totalPulls: number;
  pullsSinceRare: number;
  pullsSinceVeryRare: number;
  pullsSinceLegendary: number;
}

export interface GachaPull {
  id: string;
  banner: GachaBanner;
  rarity: Rarity;
  pullNumber: number;
  resultType: "variant" | "weapon" | "identity";
  resultId: string;
  wasPity: boolean;
  wasDuplicate: boolean;
}

export interface GachaItemEffect {
  ac?: number;
  saving_throws?: number;
  stealth_advantage?: boolean;
  str_set?: number;
  con_set?: number;
  wis_set?: number;
  displacement?: boolean;
  fly_speed?: number;
  spell_attack?: number;
  spell_dc?: number;
  magic_save_advantage?: boolean;
  speed_double?: boolean;
  spell?: string;
  uses_per_day?: number;
  at_will?: boolean;
  charges?: number;
  truesight?: number;
  telepathy_range?: number;
}

export interface GachaVariant {
  id: string;
  baseCharacterId: string;
  name: string;
  rarity: Rarity;
  origin: string;
  subclassVariant: string;
  inherentItem: GachaItemEffect;
  preAppliedEnhancements: string[];
  description: string;
}

export interface GachaWeapon {
  id: string;
  name: string;
  rarity: Rarity;
  baseWeaponType: string;
  bonus: number;
  damageType: string | null;
  properties: string[];
  riderEffect: { trigger: string; effect: string; usesPer: string } | null;
  description: string;
}

export interface GachaIdentity {
  id: string;
  name: string;
  epithet: string;
  rarity: Rarity;
  passiveAbility: { name: string; description: string };
  activatedAbility: { name: string; description: string; usesPer: string };
  description: string;
}
