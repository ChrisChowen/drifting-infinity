import { type ReactNode } from "react";
import { getRarityConfig } from "@/lib/rarity";
import { clsx } from "clsx";

interface RarityFrameProps {
  rarity: string;
  children: ReactNode;
  className?: string;
  /** Show the glow effect (default true) */
  glow?: boolean;
  /** Additional padding (default true) */
  padded?: boolean;
}

/**
 * Wraps content with rarity-appropriate border, glow, and animation effects.
 * - Common/Uncommon: clean border
 * - Rare: static glow
 * - Very Rare: pulsing glow
 * - Legendary: animated rotating gradient border + glow
 */
export function RarityFrame({
  rarity,
  children,
  className,
  glow = true,
  padded = true,
}: RarityFrameProps) {
  const config = getRarityConfig(rarity);

  return (
    <div
      className={clsx(
        "relative rounded-lg border transition-all duration-300",
        config.border,
        glow && config.glow,
        config.frameAnimation,
        padded && "p-4",
        className,
      )}
    >
      {/* Legendary animated border overlay */}
      {config.frameAnimation === "rarity-border-rotate" && (
        <div className="absolute inset-0 rounded-lg rarity-border-rotate-overlay pointer-events-none" />
      )}
      {children}
    </div>
  );
}
