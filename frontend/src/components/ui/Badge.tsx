import { clsx } from "clsx";
import { type ReactNode } from "react";

const colorMap = {
  default: "bg-surface-3 text-gray-300",
  gold: "bg-amber-900/40 text-amber-300",
  arcane: "bg-indigo-900/40 text-indigo-300",
  success: "bg-emerald-900/40 text-emerald-300",
  danger: "bg-red-900/40 text-red-300",
  warning: "bg-yellow-900/40 text-yellow-300",
  // Rarity
  common: "bg-gray-700/40 text-gray-300",
  uncommon: "bg-emerald-900/40 text-emerald-300",
  rare: "bg-blue-900/40 text-blue-300",
  "very-rare": "bg-purple-900/40 text-purple-300",
  legendary: "bg-amber-900/40 text-amber-300",
  // Semantic extras
  emerald: "bg-emerald-900/40 text-emerald-300",
  blue: "bg-blue-900/40 text-blue-300",
  purple: "bg-purple-900/40 text-purple-300",
  red: "bg-red-900/40 text-red-300",
  indigo: "bg-indigo-900/40 text-indigo-300",
  gray: "bg-gray-700/40 text-gray-400",
  // Tactical roles
  brute: "bg-red-900/40 text-red-300",
  soldier: "bg-orange-900/40 text-orange-300",
  artillery: "bg-blue-900/40 text-blue-300",
  controller: "bg-purple-900/40 text-purple-300",
  skirmisher: "bg-green-900/40 text-green-300",
  lurker: "bg-gray-700/40 text-gray-400",
};

interface BadgeProps {
  color?: keyof typeof colorMap;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Badge({ color = "default", icon, className, children }: BadgeProps) {
  return (
    <span className={clsx(
      "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium",
      colorMap[color],
      className,
    )}>
      {icon}
      {children}
    </span>
  );
}
