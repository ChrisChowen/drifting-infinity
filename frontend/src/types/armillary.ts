export type ArmillaryCategory = "hostile" | "neutral" | "beneficial" | "chaos";

export interface ArmillaryEffect {
  id: string;
  roundNumber: number;
  category: ArmillaryCategory;
  effectKey: string;
  effectDescription: string;
  xpCost: number;
  wasOverridden: boolean;
  wasRerolled: boolean;
}

export interface ArmillaryWeights {
  hostile: number;
  neutral: number;
  beneficial: number;
  chaos: number;
}

export interface ArmillaryBudget {
  total: number;
  spent: number;
  remaining: number;
}
