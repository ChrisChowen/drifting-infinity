import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Home, Users, Anvil, Sparkles, BookOpen, Settings, Play, RotateCcw,
  GitBranch, ScrollText, Coins, ChevronLeft, ChevronRight, Trophy, WifiOff,
} from "lucide-react";
import { clsx } from "clsx";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useRunStore } from "@/stores/useRunStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { useConnectionStatus } from "@/hooks/useConnectionStatus";

// ── Navigation config ─────────────────────────────────────────────────────

interface NavItem {
  to: string;
  label: string;
  icon: typeof Home;
  tooltip: string;
  badge?: () => { count: number; color: string } | null;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

// ── Component ─────────────────────────────────────────────────────────────

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  onOpenSettings: () => void;
}

export function Sidebar({ collapsed, onToggle, onOpenSettings }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { campaigns, activeCampaignId, setActiveCampaign } = useCampaignStore();
  const { run } = useRunStore();
  const { goldBalance, astralShardBalance } = useEconomyStore();
  const { meta, talents } = useMetaStore();

  const { status: connectionStatus } = useConnectionStatus();
  const hasActiveRun = run && !run.outcome;
  const essenceBalance = meta?.essence_balance ?? 0;
  const affordableTalents = talents.filter(
    (t) => !t.is_unlocked && t.can_afford && t.prerequisite_met,
  ).length;

  const activeCampaign = campaigns.find((c) => c.id === activeCampaignId);

  // Build nav groups
  const navGroups: NavGroup[] = [
    {
      label: "Command Center",
      items: [
        {
          to: "/",
          label: "Dashboard",
          icon: Home,
          tooltip: "Central hub \u2014 campaign overview and next steps",
        },
        {
          to: "/party",
          label: "The Roster",
          icon: Users,
          tooltip: "Assemble and manage your champions",
        },
      ],
    },
    {
      label: "Armillary Powers",
      items: [
        {
          to: "/forge",
          label: "The Forge",
          icon: Anvil,
          tooltip: "Purchase permanent enhancements",
        },
        {
          to: "/gacha",
          label: "The Vault",
          icon: Sparkles,
          tooltip: "Acquire magic items and boons",
        },
        {
          to: "/attunement",
          label: "Attunement",
          icon: GitBranch,
          tooltip: "Channel essence into permanent talents",
          badge: () =>
            affordableTalents > 0
              ? { count: affordableTalents, color: "bg-purple-500" }
              : null,
        },
      ],
    },
    {
      label: "Chronicles",
      items: [
        {
          to: "/chronicles",
          label: "Lore & Triumphs",
          icon: ScrollText,
          tooltip: "Lore fragments and achievements",
        },
        {
          to: "/archive",
          label: "The Archive",
          icon: BookOpen,
          tooltip: "Review expedition history and statistics",
        },
      ],
    },
  ];

  const isActive = (to: string) =>
    to === "/" ? location.pathname === "/" : location.pathname.startsWith(to);

  return (
    <aside
      className={clsx(
        "fixed left-0 top-0 bottom-0 z-30 bg-surface-1 border-r border-surface-3/50 flex flex-col transition-all duration-300",
        collapsed ? "w-16" : "w-60",
      )}
    >
      {/* ── Logo & Campaign Selector ──────────────────────────────── */}
      <div className="px-3 pt-4 pb-2">
        {/* Logo */}
        <Link to="/" className="block mb-3">
          {collapsed ? (
            <div className="w-10 h-10 mx-auto rounded-lg bg-accent/10 flex items-center justify-center">
              <span className="text-gradient-gold font-display font-bold text-lg">DI</span>
            </div>
          ) : (
            <h1 className="text-lg font-display font-bold text-gradient-gold px-1 truncate">
              Drifting Infinity
            </h1>
          )}
        </Link>

        {/* Campaign Selector */}
        {!collapsed && campaigns.length > 0 && (
          <select
            value={activeCampaignId ?? ""}
            onChange={(e) => {
              if (e.target.value) setActiveCampaign(e.target.value);
            }}
            className="w-full bg-surface-2 text-gray-300 text-xs rounded-lg px-2.5 py-2 border border-surface-3 focus:border-accent/50 focus:outline-none transition-colors font-display truncate"
            title="Select campaign"
          >
            {campaigns.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        )}

        {collapsed && activeCampaign && (
          <div
            className="w-10 h-10 mx-auto rounded-lg bg-surface-2 flex items-center justify-center text-accent font-display font-bold text-sm cursor-pointer"
            title={activeCampaign.name}
          >
            {activeCampaign.name.charAt(0)}
          </div>
        )}
      </div>

      {/* ── Expedition Button ─────────────────────────────────────── */}
      {activeCampaignId && (
        <div className={clsx("px-3 mb-2", collapsed && "flex justify-center")}>
          {collapsed ? (
            <button
              onClick={() => navigate(hasActiveRun ? "/run/setup" : "/run/setup")}
              className={clsx(
                "w-10 h-10 rounded-lg flex items-center justify-center transition-all",
                hasActiveRun
                  ? "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30"
                  : "bg-accent/20 text-accent hover:bg-accent/30",
              )}
              title={hasActiveRun ? "Resume Expedition" : "Begin Expedition"}
              aria-label={hasActiveRun ? "Resume Expedition" : "Begin Expedition"}
            >
              {hasActiveRun ? <RotateCcw size={18} /> : <Play size={18} />}
            </button>
          ) : (
            <button
              onClick={() => navigate("/run/setup")}
              className={clsx(
                "w-full py-2.5 px-3 rounded-lg font-display font-semibold text-sm flex items-center gap-2 transition-all",
                hasActiveRun
                  ? "bg-amber-500/15 text-amber-400 hover:bg-amber-500/25 border border-amber-500/20"
                  : "bg-accent/15 text-accent hover:bg-accent/25 border border-accent/20 animate-glow-pulse",
              )}
            >
              {hasActiveRun ? (
                <>
                  <RotateCcw size={16} />
                  <span>Resume Expedition</span>
                </>
              ) : (
                <>
                  <Play size={16} />
                  <span>Begin Expedition</span>
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* ── Nav Groups ────────────────────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto px-2 space-y-4 mt-2">
        {navGroups.map((group) => (
          <div key={group.label}>
            {/* Group label */}
            {!collapsed && (
              <div className="px-2 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-600">
                {group.label}
              </div>
            )}

            {collapsed && <div className="w-8 mx-auto border-t border-surface-3 mb-2" />}

            {/* Nav items */}
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.to);
                const badgeData = item.badge?.();

                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    title={collapsed ? `${item.label} \u2014 ${item.tooltip}` : item.tooltip}
                    className={clsx(
                      "flex items-center gap-2.5 rounded-lg transition-all duration-200 relative",
                      collapsed ? "w-10 h-10 mx-auto justify-center" : "px-2.5 py-2",
                      active
                        ? "bg-surface-2 text-accent"
                        : "text-gray-400 hover:text-gray-200 hover:bg-surface-2/50",
                    )}
                  >
                    {/* Active indicator bar */}
                    {active && !collapsed && (
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-accent rounded-r" />
                    )}

                    <Icon size={collapsed ? 18 : 16} className="flex-shrink-0" />

                    {!collapsed && (
                      <span className="text-sm font-medium truncate">{item.label}</span>
                    )}

                    {/* Notification badge */}
                    {badgeData && (
                      <span
                        className={clsx(
                          "rounded-full text-[9px] font-bold text-white flex items-center justify-center",
                          badgeData.color,
                          collapsed
                            ? "absolute -top-0.5 -right-0.5 w-3.5 h-3.5"
                            : "ml-auto w-4 h-4",
                        )}
                      >
                        {collapsed ? "" : badgeData.count}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* ── Bottom Section ────────────────────────────────────────── */}
      <div className="border-t border-surface-3/50 px-2 py-3 space-y-2">
        {/* Settings */}
        <button
          onClick={onOpenSettings}
          className={clsx(
            "flex items-center gap-2.5 rounded-lg transition-all text-gray-400 hover:text-gray-200 hover:bg-surface-2/50",
            collapsed ? "w-10 h-10 mx-auto justify-center" : "w-full px-2.5 py-2",
          )}
          title="Campaign Settings"
          aria-label="Campaign Settings"
        >
          <Settings size={collapsed ? 18 : 16} className="flex-shrink-0" />
          {!collapsed && <span className="text-sm font-medium">Settings</span>}
        </button>

        {/* Currency display */}
        {activeCampaignId && (
          <div
            className={clsx(
              "flex items-center rounded-lg bg-surface-2/50 px-2 py-1.5",
              collapsed ? "flex-col gap-1.5 mx-auto w-12" : "gap-3 justify-center",
            )}
          >
            <div className="flex items-center gap-1" title="Gold">
              <Coins size={12} className="text-gold" />
              {!collapsed && (
                <span className="text-xs text-gold font-medium">{goldBalance}</span>
              )}
            </div>
            <div className="flex items-center gap-1" title="Astral Shards">
              <Sparkles size={12} className="text-shard" />
              {!collapsed && (
                <span className="text-xs text-shard font-medium">{astralShardBalance}</span>
              )}
            </div>
            <div className="flex items-center gap-1" title="Essence">
              <Trophy size={12} className="text-purple-400" />
              {!collapsed && (
                <span className="text-xs text-purple-400 font-medium">{essenceBalance}</span>
              )}
            </div>
          </div>
        )}

        {/* Connection status */}
        {connectionStatus === "disconnected" && (
          <div
            className={clsx(
              "flex items-center gap-2 rounded-lg bg-red-500/10 text-red-400",
              collapsed ? "w-10 h-8 mx-auto justify-center" : "px-2.5 py-1.5",
            )}
            title="Backend unavailable"
          >
            <WifiOff size={collapsed ? 14 : 12} className="flex-shrink-0" />
            {!collapsed && <span className="text-xs font-medium">Offline</span>}
          </div>
        )}

        {/* Collapse toggle */}
        <button
          onClick={onToggle}
          className={clsx(
            "flex items-center justify-center rounded-lg text-gray-500 hover:text-gray-300 hover:bg-surface-2/50 transition-all",
            collapsed ? "w-10 h-8 mx-auto" : "w-full h-8",
          )}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>
    </aside>
  );
}
