import { Link, useLocation } from "react-router-dom";
import { Home, Users, Anvil, Sparkles, BookOpen, Settings, Coins, Heart, GitBranch, ScrollText } from "lucide-react";
import { clsx } from "clsx";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useRunStore } from "@/stores/useRunStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { NAV_LABELS } from "@/constants/lore";

const ICON_MAP = { Home, Users, Anvil, Sparkles, BookOpen, Settings, GitBranch, ScrollText } as const;

const LOBBY_NAV = [
  { to: "/", key: "lobby" as const },
  { to: "/party", key: "party" as const },
  { to: "/attunement", key: "attunement" as const },
  { to: "/chronicles", key: "chronicles" as const },
  { to: "/forge", key: "forge" as const },
  { to: "/gacha", key: "gacha" as const },
  { to: "/archive", key: "archive" as const },
];

const PHASE_LABELS: Record<string, string> = {
  setup: "Expedition Planning",
  "encounter-brief": "Arena Briefing",
  "encounter-active": "The Arena",
  combat: "The Arena",
  "post-arena": "Aftermath",
  reward: "Spoils of Battle",
  shop: "The Merchant",
  "floor-transition": "Descent",
  complete: "Expedition's End",
};

interface TopBarProps {
  onOpenSettings?: () => void;
}

export function TopBar({ onOpenSettings }: TopBarProps) {
  const location = useLocation();
  const { activeCampaignId } = useCampaignStore();
  const { run, floor, arena, phase, livesRemaining } = useRunStore();
  const { goldBalance, astralShardBalance } = useEconomyStore();
  const { meta } = useMetaStore();

  const isRunActive = run && !run.outcome && location.pathname.startsWith("/run");

  // Dynamic max lives based on meta talents (resilience_1 adds +1 life)
  const maxLives = meta?.unlocked_talents?.includes("resilience_1") ? 4 : 3;
  const essenceBalance = meta?.essence_balance ?? 0;

  return (
    <header className="bg-surface-1 border-b border-surface-3/50 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link
          to="/"
          className="text-xl font-display font-bold text-gradient-gold hover:opacity-80 transition-opacity"
        >
          Drifting Infinity
        </Link>

        {/* Navigation */}
        {isRunActive ? (
          /* Run Mode: Breadcrumb with lore labels */
          <nav className="flex items-center gap-2 text-sm">
            <span className="text-gray-500">Floor {floor?.floor_number ?? "?"}</span>
            <span className="text-gray-600">/</span>
            <span className="text-gray-500">Arena {arena?.arena_number ?? "?"}</span>
            <span className="text-gray-600">/</span>
            <span className="text-accent font-medium font-display">{PHASE_LABELS[phase] ?? phase}</span>
          </nav>
        ) : (
          /* Lobby Mode: In-world nav names with tooltips */
          <nav className="flex items-center gap-1">
            {LOBBY_NAV.map(({ to, key }) => {
              const navInfo = NAV_LABELS[key];
              const Icon = ICON_MAP[navInfo.icon as keyof typeof ICON_MAP];
              const isActive = to === "/" ? location.pathname === "/" : location.pathname.startsWith(to);
              return (
                <Link
                  key={to}
                  to={to}
                  title={navInfo.tooltip}
                  className={clsx(
                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-accent/10 text-accent"
                      : "text-gray-400 hover:text-gray-200 hover:bg-surface-2",
                  )}
                >
                  <Icon size={16} />
                  <span className="hidden sm:inline">{navInfo.name}</span>
                </Link>
              );
            })}
          </nav>
        )}

        {/* Right Side: Balances & Settings */}
        <div className="flex items-center gap-3">
          {activeCampaignId && (
            <>
              {isRunActive && (
                <div className="flex items-center gap-1 text-sm" title="Lives remaining">
                  {Array.from({ length: maxLives }, (_, i) => (
                    <Heart
                      key={i}
                      size={14}
                      className={i < livesRemaining ? "text-red-400 fill-red-400" : "text-gray-600"}
                    />
                  ))}
                </div>
              )}
              {!isRunActive && essenceBalance > 0 && (
                <Link
                  to="/attunement"
                  className="flex items-center gap-1 text-sm hover:opacity-80 transition-opacity"
                  title="Essence — visit Attunement to spend"
                >
                  <Sparkles size={14} className="text-purple-400" />
                  <span className="text-purple-400 font-medium">{essenceBalance}</span>
                </Link>
              )}
              <div className="flex items-center gap-1 text-sm">
                <Coins size={14} className="text-gold" />
                <span className="text-gold font-medium">{goldBalance}</span>
              </div>
              <div className="flex items-center gap-1 text-sm">
                <Sparkles size={14} className="text-shard" />
                <span className="text-shard font-medium">{astralShardBalance}</span>
              </div>
            </>
          )}
          {isRunActive && onOpenSettings ? (
            <button
              className="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-surface-2 transition-colors"
              onClick={onOpenSettings}
              aria-label="Settings"
            >
              <Settings size={18} />
            </button>
          ) : (
            <Link
              to="/settings"
              className="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-surface-2 transition-colors"
              aria-label="Settings"
            >
              <Settings size={18} />
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
