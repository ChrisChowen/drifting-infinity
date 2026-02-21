export interface Enhancement {
  id: string;
  name: string;
  tier: 1 | 2 | 3;
  baseCost: number;
  effect: EnhancementEffect;
  powerRating: number;
  description: string;
  stackingRules: {
    maxPerCharacter: number;
    stacksWith: string[];
  };
}

export interface EnhancementEffect {
  type: string;
  [key: string]: unknown;
}

export interface RewardEffect {
  // Gold rewards
  gold?: number;
  // Healing / consumable
  heal?: string;
  temp_hp?: number;
  // Spell effects
  spell?: string;
  spell_effect?: string;
  damage?: string;
  damage_type?: string;
  dc?: number;
  // Defensive effects
  resistance?: string;
  condition?: string;
  duration?: string;
  flying_speed?: number;
  remove?: string[];
  advantage?: string;
  // Ability score overrides
  set_ability?: { ability: string; value: number };
  // Resource recovery
  hit_dice?: number;
  inspiration?: boolean;
  spell_slot?: number;
  // Feat rewards
  feat_type?: string;
  min_party_level?: number;
}

export interface Reward {
  id: string;
  name: string;
  category: "consumable" | "buff" | "equipment" | "favour" | "gold" | "intel";
  rarity: Rarity;
  description: string;
  effect: RewardEffect;
}

export interface ShopItem extends Reward {
  price: number;
}

export type Rarity = "common" | "uncommon" | "rare" | "very_rare" | "legendary";
