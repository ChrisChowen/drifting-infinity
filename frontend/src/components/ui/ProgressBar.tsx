import { clsx } from "clsx";

interface ProgressBarProps {
  value: number;
  max: number;
  label?: string;
  sublabel?: string;
  color?: "green" | "gold" | "arcane" | "hp" | "red";
  size?: "sm" | "md" | "lg";
  animated?: boolean;
  className?: string;
}

const colorClasses = {
  green: "bg-emerald-500",
  gold: "bg-accent",
  arcane: "bg-arcane",
  hp: "", // handled dynamically
  red: "bg-red-500",
};

function getHpColor(percent: number): string {
  if (percent > 75) return "bg-hp-full";
  if (percent > 50) return "bg-hp-high";
  if (percent > 25) return "bg-hp-mid";
  if (percent > 10) return "bg-hp-low";
  return "bg-hp-critical";
}

export function ProgressBar({
  value, max, label, sublabel, color = "green", size = "md", animated = true, className,
}: ProgressBarProps) {
  const percent = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  const barColor = color === "hp" ? getHpColor(percent) : colorClasses[color];
  const heights = { sm: "h-1.5", md: "h-2.5", lg: "h-4" };

  return (
    <div className={clsx("space-y-1", className)}>
      {(label || sublabel) && (
        <div className="flex justify-between text-xs text-gray-400">
          <span>{label}</span>
          <span>{sublabel ?? `${percent}%`}</span>
        </div>
      )}
      <div className={clsx("w-full bg-surface-3/50 rounded-full overflow-hidden", heights[size])}>
        <div
          className={clsx(
            barColor,
            heights[size],
            "rounded-full",
            animated && "transition-all duration-500 ease-out",
          )}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
