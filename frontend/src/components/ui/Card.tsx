import { type ReactNode, type HTMLAttributes } from "react";
import { clsx } from "clsx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  glow?: boolean;
  hover?: boolean;
  selected?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
  children: ReactNode;
}

const paddings = {
  none: "",
  sm: "p-3",
  md: "p-5",
  lg: "p-6",
};

export function Card({ glow, hover, selected, padding = "md", className, children, ...props }: CardProps) {
  return (
    <div
      className={clsx(
        "bg-surface-1 rounded-xl border transition-all duration-200",
        selected ? "border-accent/50 ring-1 ring-accent/30" : "border-surface-3/50",
        hover && "hover:border-surface-3 hover:bg-surface-1/80 cursor-pointer",
        glow && "card-glow",
        paddings[padding],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={clsx("flex items-center justify-between mb-4", className)}>
      {children}
    </div>
  );
}

export function CardTitle({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <h3 className={clsx("text-lg font-semibold text-white", className)}>
      {children}
    </h3>
  );
}
