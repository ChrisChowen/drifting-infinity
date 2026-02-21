export const DAMAGE_TYPES = [
  "acid",
  "bludgeoning",
  "cold",
  "fire",
  "force",
  "lightning",
  "necrotic",
  "piercing",
  "poison",
  "psychic",
  "radiant",
  "slashing",
  "thunder",
] as const;

export type DamageType = (typeof DAMAGE_TYPES)[number];

export const DAMAGE_TYPE_COLORS: Record<DamageType, string> = {
  acid: "text-lime-400",
  bludgeoning: "text-stone-400",
  cold: "text-cyan-400",
  fire: "text-orange-400",
  force: "text-indigo-400",
  lightning: "text-blue-400",
  necrotic: "text-purple-400",
  piercing: "text-gray-400",
  poison: "text-green-400",
  psychic: "text-pink-400",
  radiant: "text-yellow-300",
  slashing: "text-red-400",
  thunder: "text-sky-400",
};
