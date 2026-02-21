import type { Condition } from "@/types";

export const CONDITIONS: Record<Condition, { label: string; icon: string; color: string; description: string }> = {
  blinded: { label: "Blinded", icon: "eye-off", color: "text-gray-500", description: "Can't see. Attack rolls against have advantage. Own attack rolls have disadvantage." },
  charmed: { label: "Charmed", icon: "heart", color: "text-pink-400", description: "Can't attack charmer or target them with harmful abilities. Charmer has advantage on social checks." },
  deafened: { label: "Deafened", icon: "volume-x", color: "text-gray-500", description: "Can't hear. Automatically fails any check that requires hearing." },
  frightened: { label: "Frightened", icon: "skull", color: "text-yellow-400", description: "Disadvantage on ability checks and attack rolls while source of fear is in line of sight. Can't willingly move closer to the source." },
  grappled: { label: "Grappled", icon: "grip-horizontal", color: "text-orange-400", description: "Speed becomes 0. Ends if grappler is incapacitated or moved out of reach." },
  incapacitated: { label: "Incapacitated", icon: "circle-slash", color: "text-red-400", description: "Can't take actions or reactions." },
  invisible: { label: "Invisible", icon: "ghost", color: "text-blue-300", description: "Impossible to see without magic or special sense. Attack rolls against have disadvantage. Own attack rolls have advantage." },
  paralyzed: { label: "Paralyzed", icon: "zap-off", color: "text-yellow-600", description: "Incapacitated, can't move or speak. Auto-fails STR and DEX saves. Attacks have advantage. Hits within 5 ft are critical." },
  petrified: { label: "Petrified", icon: "mountain", color: "text-stone-400", description: "Transformed to stone. Weight x10. Incapacitated, can't move or speak. Resistance to all damage. Immune to poison and disease." },
  poisoned: { label: "Poisoned", icon: "flask-round", color: "text-green-400", description: "Disadvantage on attack rolls and ability checks." },
  prone: { label: "Prone", icon: "arrow-down", color: "text-amber-400", description: "Disadvantage on attack rolls. Attacks within 5 ft have advantage, ranged attacks have disadvantage. Must spend half movement to stand." },
  restrained: { label: "Restrained", icon: "link", color: "text-orange-500", description: "Speed becomes 0. Attack rolls against have advantage. Own attack rolls have disadvantage. Disadvantage on DEX saves." },
  stunned: { label: "Stunned", icon: "star", color: "text-yellow-300", description: "Incapacitated, can't move, can only speak falteringly. Auto-fails STR and DEX saves. Attacks against have advantage." },
  unconscious: { label: "Unconscious", icon: "moon", color: "text-indigo-400", description: "Incapacitated, can't move or speak, unaware. Drops held items, falls prone. Auto-fails STR and DEX saves. Attacks have advantage. Hits within 5 ft are critical." },
  exhaustion: { label: "Exhaustion", icon: "battery-low", color: "text-red-500", description: "Cumulative levels. Affects ability checks, speed, attack rolls, saving throws, HP max. 6 levels = death." },
  final_stand: { label: "Final Stand", icon: "flame", color: "text-red-600", description: "Creature fights with desperate fury. At 0 HP, makes one last attack or action before falling." },
};
