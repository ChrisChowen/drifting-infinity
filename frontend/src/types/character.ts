export interface Character {
  id: string;
  campaignId: string;
  name: string;
  characterClass: string;
  subclass: string | null;
  level: number;
  ac: number;
  maxHp: number;
  saves: Record<AbilityScore, number>;
  damageTypes: string[];
  capabilities: PartyCapabilities;
  speed: number;
  variantId: string | null;
  identityId: string | null;
  weaponId: string | null;
}

export type AbilityScore = "str" | "dex" | "con" | "int" | "wis" | "cha";

export interface PartyCapabilities {
  rangedDamage: boolean;
  flight: boolean;
  conditionRemoval: boolean;
  deathWard: boolean;
  revivify: boolean;
  magicalWeapons: boolean;
  aoeAvailable: boolean;
  teleportation: boolean;
  darkvisionCount: number;
  stealthCapable: boolean;
  damageTypesAvailable: string[];
}

export interface CharacterCombatState {
  characterId: string;
  currentHp: number;
  maxHp: number;
  conditions: Condition[];
  isOnFinalStand: boolean;
  isDead: boolean;
  deathSaves: { successes: number; failures: number };
}

export type Condition =
  | "blinded"
  | "charmed"
  | "deafened"
  | "frightened"
  | "grappled"
  | "incapacitated"
  | "invisible"
  | "paralyzed"
  | "petrified"
  | "poisoned"
  | "prone"
  | "restrained"
  | "stunned"
  | "unconscious"
  | "exhaustion"
  | "final_stand";
