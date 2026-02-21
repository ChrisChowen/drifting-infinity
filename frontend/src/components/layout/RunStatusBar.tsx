import { useRunStore } from "@/stores/useRunStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { Heart, Coins, Sparkles, Settings } from "lucide-react";
import { clsx } from "clsx";
import { IntensityCurve } from "@/components/charts/IntensityCurve";

const PHASE_LABELS: Record<string, string> = {
  setup: "Expedition Planning",
  "encounter-brief": "Arena Briefing",
  "encounter-active": "The Arena",
  combat: "The Arena",
  "post-arena": "Arena Aftermath",
  reward: "Spoils of Battle",
  shop: "The Wandering Merchant",
  "floor-transition": "Descent",
  "run-complete": "Expedition's End",
};

interface RunStatusBarProps {
  onOpenSettings?: () => void;
}

export function RunStatusBar({ onOpenSettings }: RunStatusBarProps) {
  const { run, floor, arena, phase, livesRemaining } = useRunStore();
  const { goldBalance, astralShardBalance } = useEconomyStore();
  const { meta } = useMetaStore();

  const maxLives = meta?.unlocked_talents?.includes("resilience_1") ? 4 : 3;

  return (
    <header className="bg-surface-1 border-b border-surface-3/50 px-3 md:px-4 py-2">
      <div className="flex items-center justify-between gap-2">
        {/* Left: Location */}
        <div className="flex items-center gap-1.5 md:gap-2 text-xs md:text-sm flex-shrink-0">
          <span className="text-gray-500 font-medium">
            <span className="hidden sm:inline">Floor </span>F{floor?.floor_number ?? "?"}
          </span>
          <span className="text-gray-600">/</span>
          <span className="text-gray-500 font-medium">
            <span className="hidden sm:inline">Arena </span>A{arena?.arena_number ?? "?"}
          </span>
        </div>

        {/* Center: Phase + mini sparkline */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="text-xs md:text-sm font-display font-semibold text-accent truncate">
            {PHASE_LABELS[phase] ?? phase}
          </div>
          {run?.id && (
            <div className="hidden lg:block w-24 flex-shrink-0" title="Intensity curve">
              <IntensityCurve runId={run.id} compact />
            </div>
          )}
        </div>

        {/* Right: Lives + currencies + settings */}
        <div className="flex items-center gap-2 md:gap-4 flex-shrink-0">
          {/* Lives */}
          <div className="flex items-center gap-0.5" title={`${livesRemaining} / ${maxLives} lives`} role="img" aria-label={`${livesRemaining} of ${maxLives} lives remaining`}>
            {Array.from({ length: maxLives }, (_, i) => (
              <Heart
                key={i}
                size={12}
                className={clsx(
                  i < livesRemaining ? "text-red-400 fill-red-400" : "text-gray-600",
                )}
              />
            ))}
          </div>

          {/* Gold */}
          <div className="flex items-center gap-0.5 text-xs md:text-sm">
            <Coins size={12} className="text-gold" />
            <span className="text-gold font-medium">{goldBalance}</span>
          </div>

          {/* Shards — hidden on very small screens */}
          <div className="hidden sm:flex items-center gap-0.5 text-xs md:text-sm">
            <Sparkles size={12} className="text-shard" />
            <span className="text-shard font-medium">{astralShardBalance}</span>
          </div>

          {/* Settings */}
          {onOpenSettings && (
            <button
              className="p-1 md:p-1.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-surface-2 transition-colors"
              onClick={onOpenSettings}
              aria-label="Settings"
            >
              <Settings size={14} />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
