import type { TacticalRole } from "@/types";

export const TACTICAL_ROLE_CONFIG: Record<
  TacticalRole,
  { label: string; color: string; bgColor: string; description: string }
> = {
  brute: {
    label: "Brute",
    color: "text-brute",
    bgColor: "bg-brute",
    description: "High HP, high damage, charges forward",
  },
  soldier: {
    label: "Soldier",
    color: "text-soldier",
    bgColor: "bg-soldier",
    description: "Moderate HP/AC, holds position, protects allies",
  },
  artillery: {
    label: "Artillery",
    color: "text-artillery",
    bgColor: "bg-artillery",
    description: "Low HP, ranged attacks, stays at distance",
  },
  controller: {
    label: "Controller",
    color: "text-controller",
    bgColor: "bg-controller",
    description: "Area denial, conditions, terrain manipulation",
  },
  skirmisher: {
    label: "Skirmisher",
    color: "text-skirmisher",
    bgColor: "bg-skirmisher",
    description: "High mobility, hit-and-run, targets weak points",
  },
  lurker: {
    label: "Lurker",
    color: "text-lurker",
    bgColor: "bg-lurker",
    description: "Stealth, ambush, high burst damage from hiding",
  },
};
