import { Minus, Plus } from "lucide-react";
import { clsx } from "clsx";

interface NumberStepperProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  label?: string;
  description?: string;
  size?: "sm" | "md" | "lg";
}

const sizes = {
  sm: { display: "text-xl", button: "w-8 h-8", icon: 14 },
  md: { display: "text-3xl", button: "w-10 h-10", icon: 18 },
  lg: { display: "text-5xl", button: "w-12 h-12", icon: 22 },
};

export function NumberStepper({
  value, onChange, min = 0, max = 99, step = 1, label, description, size = "md",
}: NumberStepperProps) {
  const s = sizes[size];
  const canDecrement = value - step >= min;
  const canIncrement = value + step <= max;

  return (
    <div className="space-y-1">
      {label && <div className="text-sm font-medium text-gray-300">{label}</div>}
      {description && <p className="text-xs text-gray-500">{description}</p>}
      <div className="flex items-center gap-4">
        <button
          type="button"
          className={clsx(
            s.button,
            "rounded-full flex items-center justify-center transition-colors",
            canDecrement
              ? "bg-surface-2 hover:bg-surface-3 text-gray-300 border border-surface-3"
              : "bg-surface-1 text-gray-600 cursor-not-allowed",
          )}
          onClick={() => canDecrement && onChange(value - step)}
          disabled={!canDecrement}
        >
          <Minus size={s.icon} />
        </button>
        <span className={clsx(s.display, "font-bold text-white font-display min-w-[2ch] text-center")}>
          {value}
        </span>
        <button
          type="button"
          className={clsx(
            s.button,
            "rounded-full flex items-center justify-center transition-colors",
            canIncrement
              ? "bg-surface-2 hover:bg-surface-3 text-gray-300 border border-surface-3"
              : "bg-surface-1 text-gray-600 cursor-not-allowed",
          )}
          onClick={() => canIncrement && onChange(value + step)}
          disabled={!canIncrement}
        >
          <Plus size={s.icon} />
        </button>
      </div>
    </div>
  );
}
