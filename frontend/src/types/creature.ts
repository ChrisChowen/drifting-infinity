export type TacticalRole = "brute" | "soldier" | "artillery" | "controller" | "skirmisher" | "lurker";

export type DangerRating = "trivial" | "standard" | "dangerous" | "lethal" | "banned";

export interface ThreatFlags {
  save_or_die: boolean;
  save_or_incapacitate: boolean;
  permanent_drain: boolean;
  action_denial: boolean;
  healing_prevention: boolean;
  forced_movement: boolean;
  summon_or_split: boolean;
  aoe_damage: boolean;
  aoe_control: boolean;
  stealth_ambush: boolean;
  flight_only: boolean;
  counterspell_or_dispel: boolean;
  charm_or_dominate: boolean;
  swarm_scaling: boolean;
  equipment_destruction: boolean;
  pack_tactics: boolean;
  grapple_capable: boolean;
  creates_darkness: boolean;
  has_blindsight_or_devilsight: boolean;
  high_single_hit_damage: boolean;
  imposes_restrained: boolean;
  imposes_frightened: boolean;
}

export interface DangerByTier {
  tier1: DangerRating;
  tier2: DangerRating;
  tier3: DangerRating;
  tier4: DangerRating;
}

export interface StatblockAction {
  name: string;
  desc: string;
}

export interface MonsterStatblock {
  name: string;
  size: string;
  type: string;
  alignment: string;
  armor_class: number;
  hit_points: number;
  hit_dice: string;
  speed: Record<string, string>;
  challenge_rating: string;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  strength_save?: number | null;
  dexterity_save?: number | null;
  constitution_save?: number | null;
  intelligence_save?: number | null;
  wisdom_save?: number | null;
  charisma_save?: number | null;
  senses: string;
  languages: string;
  damage_vulnerabilities: string;
  damage_resistances: string;
  damage_immunities: string;
  condition_immunities: string;
  skills: Record<string, number>;
  actions: StatblockAction[];
  bonus_actions: StatblockAction[];
  special_abilities: StatblockAction[];
  legendary_actions: StatblockAction[];
  legendary_desc: string;
  reactions: StatblockAction[];
}

export interface Monster {
  id: string;
  slug: string;
  name: string;
  source: string;
  cr: number;
  xp: number;
  hp: number;
  hitDice: string;
  ac: number;
  size: string;
  creatureType: string;
  tacticalRole: TacticalRole;
  secondaryRole: TacticalRole | null;
  intelligenceTier: "mindless" | "instinctual" | "cunning" | "mastermind";
  mechanicalSignature: MechanicalSignature;
  behaviourProfile: BehaviourProfile;
  vulnerabilities: string[];
  weakSaves: WeakSave[];
  environments: string[];
  statblock: MonsterStatblock;
}

export interface WeakSave {
  ability: string;
  modifier: number;
}

export interface MechanicalSignature {
  damageOutput: {
    perRoundAverage: number;
    perRoundMax: number;
    spikePotential: number;
    damageTypes: string[];
    requiresRecharge: boolean;
  };
  effectiveHp: number;
  saveDifficulty: {
    strongSaves: string[];
    weakSaves: string[];
    conditionImmunities: string[];
    magicResistance: boolean;
  };
  threatFlags: ThreatFlags;
  dangerByTier: DangerByTier;
  partyWarnings: {
    dangerousIfNo: string[];
    trivialisedBy: string[];
    hardCounters: string[];
  };
  exploitProfile: {
    vulnerabilities: string[];
    weakSaves: WeakSave[];
    resistanceGaps: string[];
  };
}

export interface BehaviourProfile {
  role: TacticalRole;
  positioning: "frontline" | "backline" | "flanking" | "mobile" | "hidden";
  targetPriority: string;
  retreatThreshold: number;
  abilityPriority: string[];
  groupTactics: string | null;
}

export interface CreatureCombatState {
  id: string;
  monsterId: string;
  instanceLabel: string;
  currentHp: number;
  maxHp: number;
  conditions: string[];
  isAlive: boolean;
  isReinforcement: boolean;
  monster: Monster;
}
