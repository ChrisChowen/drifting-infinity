export const D5E_CLASSES = [
  "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
  "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard",
] as const;

export type D5eClass = (typeof D5E_CLASSES)[number];

interface ClassProfile {
  baseAc: number;
  baseHp: number;
  hpPerLevel: number;
  speed: number;
  proficientSaves: string[];
  commonDamageTypes: string[];
  icon: string; // lucide icon name hint for display
}

export const CLASS_DEFAULTS: Record<D5eClass, ClassProfile> = {
  Barbarian: {
    baseAc: 14, baseHp: 12, hpPerLevel: 7, speed: 30,
    proficientSaves: ["str", "con"],
    commonDamageTypes: ["slashing", "bludgeoning"],
    icon: "axe",
  },
  Bard: {
    baseAc: 13, baseHp: 8, hpPerLevel: 5, speed: 30,
    proficientSaves: ["dex", "cha"],
    commonDamageTypes: ["psychic", "thunder"],
    icon: "music",
  },
  Cleric: {
    baseAc: 16, baseHp: 8, hpPerLevel: 5, speed: 30,
    proficientSaves: ["wis", "cha"],
    commonDamageTypes: ["radiant", "bludgeoning"],
    icon: "shield",
  },
  Druid: {
    baseAc: 13, baseHp: 8, hpPerLevel: 5, speed: 30,
    proficientSaves: ["int", "wis"],
    commonDamageTypes: ["fire", "cold", "lightning"],
    icon: "leaf",
  },
  Fighter: {
    baseAc: 16, baseHp: 10, hpPerLevel: 6, speed: 30,
    proficientSaves: ["str", "con"],
    commonDamageTypes: ["slashing", "piercing"],
    icon: "sword",
  },
  Monk: {
    baseAc: 15, baseHp: 8, hpPerLevel: 5, speed: 30,
    proficientSaves: ["str", "dex"],
    commonDamageTypes: ["bludgeoning"],
    icon: "wind",
  },
  Paladin: {
    baseAc: 18, baseHp: 10, hpPerLevel: 6, speed: 30,
    proficientSaves: ["wis", "cha"],
    commonDamageTypes: ["radiant", "slashing"],
    icon: "sun",
  },
  Ranger: {
    baseAc: 15, baseHp: 10, hpPerLevel: 6, speed: 30,
    proficientSaves: ["str", "dex"],
    commonDamageTypes: ["piercing", "slashing"],
    icon: "target",
  },
  Rogue: {
    baseAc: 14, baseHp: 8, hpPerLevel: 5, speed: 30,
    proficientSaves: ["dex", "int"],
    commonDamageTypes: ["piercing"],
    icon: "eye",
  },
  Sorcerer: {
    baseAc: 12, baseHp: 6, hpPerLevel: 4, speed: 30,
    proficientSaves: ["con", "cha"],
    commonDamageTypes: ["fire", "lightning", "cold"],
    icon: "flame",
  },
  Warlock: {
    baseAc: 13, baseHp: 8, hpPerLevel: 5, speed: 30,
    proficientSaves: ["wis", "cha"],
    commonDamageTypes: ["force", "necrotic", "fire"],
    icon: "moon",
  },
  Wizard: {
    baseAc: 12, baseHp: 6, hpPerLevel: 4, speed: 30,
    proficientSaves: ["int", "wis"],
    commonDamageTypes: ["fire", "cold", "lightning", "force"],
    icon: "wand",
  },
};

const ABILITY_KEYS = ["str", "dex", "con", "int", "wis", "cha"] as const;

export function computeDefaults(className: D5eClass, level: number) {
  const profile = CLASS_DEFAULTS[className];
  const hp = profile.baseHp + profile.hpPerLevel * (level - 1);

  // Rough save computation: proficient saves get +2 + proficiency bonus
  const profBonus = Math.floor((level - 1) / 4) + 2;
  const saves: Record<string, number> = {};
  for (const ab of ABILITY_KEYS) {
    saves[ab] = profile.proficientSaves.includes(ab) ? profBonus : 0;
  }

  return {
    ac: profile.baseAc,
    max_hp: hp,
    speed: profile.speed,
    saves,
    damage_types: [...profile.commonDamageTypes],
  };
}

export const ALL_DAMAGE_TYPES = [
  "slashing", "piercing", "bludgeoning",
  "fire", "cold", "lightning", "thunder",
  "acid", "poison", "necrotic", "radiant",
  "force", "psychic",
];
