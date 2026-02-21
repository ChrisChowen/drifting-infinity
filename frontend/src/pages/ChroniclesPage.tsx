import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { Card, Badge, Button, PageHeader, EmptyState } from "@/components/ui";
import {
  BookOpen, Trophy, Lock, Sparkles, ScrollText, Filter,
  CheckCircle2, Eye,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import type { LoreFragmentResponse, AchievementResponse } from "@/api/meta";

type Tab = "lore" | "achievements";

const LORE_CATEGORIES = [
  "all", "armillary", "aethon", "korvath", "merchant", "history", "meta",
] as const;

const CATEGORY_COLORS: Record<string, string> = {
  armillary: "text-accent",
  aethon: "text-red-400",
  korvath: "text-orange-400",
  merchant: "text-emerald-400",
  history: "text-blue-400",
  meta: "text-purple-400",
};

const ACHIEVEMENT_CATEGORY_ICONS: Record<string, typeof Trophy> = {
  combat: Trophy,
  exploration: Eye,
  meta: Sparkles,
};

export function ChroniclesPage() {
  const navigate = useNavigate();
  const { activeCampaignId } = useCampaignStore();
  const { achievements, lore, fetchAchievements, fetchLore, fetchMeta } = useMetaStore();

  const [activeTab, setActiveTab] = useState<Tab>("lore");
  const [loreCategory, setLoreCategory] = useState<string>("all");
  const [expandedLore, setExpandedLore] = useState<string | null>(null);

  useEffect(() => {
    if (activeCampaignId) {
      fetchAchievements(activeCampaignId);
      fetchLore(activeCampaignId);
      fetchMeta(activeCampaignId);
    }
  }, [activeCampaignId, fetchAchievements, fetchLore, fetchMeta]);

  if (!activeCampaignId) {
    return (
      <EmptyState
        icon={<BookOpen size={48} />}
        title="No Campaign Selected"
        description="Select or create a campaign from the Nexus first."
        action={<Button onClick={() => navigate("/")}>Go to Nexus</Button>}
      />
    );
  }

  const discoveredCount = lore.filter((f) => f.is_discovered).length;
  const earnedCount = achievements.filter((a) => a.is_earned).length;
  const totalAchievementEssence = achievements
    .filter((a) => a.is_earned)
    .reduce((sum, a) => sum + a.essence_reward, 0);

  const filteredLore = loreCategory === "all"
    ? lore
    : lore.filter((f) => f.category === loreCategory);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="The Chronicle"
        subtitle="A record of discoveries, triumphs, and the Armillary's secrets"
        action={
          <div className="flex items-center gap-2">
            <Badge color="blue">
              <ScrollText size={12} className="inline mr-1" />
              {discoveredCount} / {lore.length} fragments
            </Badge>
            <Badge color="gold">
              <Trophy size={12} className="inline mr-1" />
              {earnedCount} / {achievements.length} achievements
            </Badge>
          </div>
        }
      />

      {/* Tab Switcher */}
      <div className="flex gap-1 p-1 bg-surface-1 rounded-lg">
        {(["lore", "achievements"] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={clsx(
              "flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all",
              activeTab === tab
                ? "bg-surface-3 text-white shadow-sm"
                : "text-gray-500 hover:text-gray-300",
            )}
          >
            {tab === "lore" ? (
              <span className="flex items-center justify-center gap-1.5">
                <ScrollText size={14} />
                Lore Fragments
              </span>
            ) : (
              <span className="flex items-center justify-center gap-1.5">
                <Trophy size={14} />
                Achievements
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Lore Tab */}
      <AnimatePresence mode="wait">
        {activeTab === "lore" && (
          <motion.div
            key="lore"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-4"
          >
            {/* Category Filter */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              <Filter size={14} className="text-gray-500 flex-shrink-0" />
              {LORE_CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setLoreCategory(cat)}
                  className={clsx(
                    "px-3 py-1 rounded-full text-xs font-medium transition-all whitespace-nowrap",
                    loreCategory === cat
                      ? "bg-accent/20 text-accent border border-accent/30"
                      : "bg-surface-2 text-gray-500 hover:text-gray-300 border border-transparent",
                  )}
                >
                  {cat === "all" ? "All" : cat.charAt(0).toUpperCase() + cat.slice(1)}
                </button>
              ))}
            </div>

            {/* Lore Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {filteredLore.map((fragment, i) => (
                <LoreCard
                  key={fragment.id}
                  fragment={fragment}
                  index={i}
                  isExpanded={expandedLore === fragment.id}
                  onToggle={() =>
                    setExpandedLore((prev) => (prev === fragment.id ? null : fragment.id))
                  }
                />
              ))}
            </div>

            {filteredLore.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <ScrollText size={32} className="mx-auto mb-2 opacity-50" />
                <p>No fragments in this category yet.</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Achievements Tab */}
        {activeTab === "achievements" && (
          <motion.div
            key="achievements"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-4"
          >
            {/* Achievement Summary */}
            <Card padding="md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gold font-display">{earnedCount}</div>
                    <div className="text-[11px] text-gray-500">Earned</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-500 font-display">
                      {achievements.length - earnedCount}
                    </div>
                    <div className="text-[11px] text-gray-500">Remaining</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-purple-400">
                    <Sparkles size={14} />
                    <span className="text-lg font-bold font-display">{totalAchievementEssence}</span>
                  </div>
                  <div className="text-[11px] text-gray-500">Essence from achievements</div>
                </div>
              </div>
            </Card>

            {/* Achievement Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {achievements.map((achievement, i) => (
                <AchievementCard key={achievement.id} achievement={achievement} index={i} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────

function LoreCard({
  fragment,
  index,
  isExpanded,
  onToggle,
}: {
  fragment: LoreFragmentResponse;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const categoryColor = CATEGORY_COLORS[fragment.category] ?? "text-gray-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
    >
      <Card
        padding="md"
        hover={fragment.is_discovered}
        onClick={fragment.is_discovered ? onToggle : undefined}
        className={clsx(
          "transition-all",
          !fragment.is_discovered && "opacity-50",
          isExpanded && "ring-1 ring-accent/30",
        )}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              {fragment.is_discovered ? (
                <ScrollText size={14} className={categoryColor} />
              ) : (
                <Lock size={14} className="text-gray-600" />
              )}
              <span className="font-display font-semibold text-sm text-white truncate">
                {fragment.title}
              </span>
            </div>
            {fragment.is_discovered && fragment.source && (
              <p className="text-[11px] text-gray-600 mt-0.5 ml-6">{fragment.source}</p>
            )}
          </div>
          <Badge
            color={fragment.is_discovered ? "blue" : "gray"}
            className="text-[10px] flex-shrink-0"
          >
            {fragment.category}
          </Badge>
        </div>

        {/* Expanded text */}
        <AnimatePresence>
          {isExpanded && fragment.is_discovered && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-3 pt-3 border-t border-surface-3">
                <p className="text-sm text-gray-300 leading-relaxed italic font-display">
                  {fragment.text}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
}

function AchievementCard({
  achievement,
  index,
}: {
  achievement: AchievementResponse;
  index: number;
}) {
  const Icon = ACHIEVEMENT_CATEGORY_ICONS[achievement.category] ?? Trophy;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
    >
      <Card
        padding="md"
        className={clsx(
          "transition-all",
          achievement.is_earned
            ? "border border-gold/30"
            : "opacity-50",
        )}
      >
        <div className="flex items-start gap-3">
          <div className={clsx(
            "p-2 rounded-lg flex-shrink-0",
            achievement.is_earned ? "bg-gold/10" : "bg-surface-2",
          )}>
            {achievement.is_earned ? (
              <Icon size={18} className="text-gold" />
            ) : (
              <Lock size={18} className="text-gray-600" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-display font-semibold text-sm text-white">
                {achievement.name}
              </span>
              {achievement.is_earned && (
                <CheckCircle2 size={14} className="text-emerald-400 flex-shrink-0" />
              )}
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{achievement.description}</p>
            <div className="flex items-center gap-1 mt-1.5 text-[11px]">
              <Sparkles size={10} className="text-purple-400" />
              <span className="text-purple-400">{achievement.essence_reward} essence</span>
              <span className="text-gray-600 ml-1">{achievement.category}</span>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
