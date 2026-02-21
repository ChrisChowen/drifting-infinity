export interface InitiativeEntry {
  id: string;
  entityType: "character" | "creature" | "armillary";
  entityId: string | null;
  entityName: string;
  initiativeRoll: number;
  sortOrder: number;
  isCurrentTurn: boolean;
}

export interface DamageRollResult {
  total: number;
  rolls: number[];
  bonus: number;
  notation: string;
  damageType: string;
  isCrit: boolean;
  breakdown: string;
}

export interface WeaknessExploitEntry {
  round: number;
  attackerName: string;
  targetName: string;
  exploitType: "vulnerability" | "weak_save";
  grantedReactionTo: string;
}

export interface CreatureAction {
  name: string;
  description: string;
  attackBonus: number | null;
  saveDC: number | null;
  saveAbility: string | null;
  damageNotation: string | null;
  damageType: string | null;
  range: string | null;
  isRecharge: boolean;
  rechargeOn: number | null;
}
