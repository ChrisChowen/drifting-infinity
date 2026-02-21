import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { Card, Badge, Button, PageHeader, EmptyState } from "@/components/ui";
import { GitBranch, Shield, Eye, Coins, Sparkles, Lock, Check, ChevronUp, ArrowLeft } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";

const BRANCH_CONFIG = {
  resilience: {
    label: "Resilience",
    icon: Shield,
    color: "text-red-400",
    bgColor: "bg-red-400/10",
    borderColor: "border-red-400/30",
    glowColor: "shadow-red-400/20",
    description: "Survival, recovery, and second chances",
  },
  insight: {
    label: "Insight",
    icon: Eye,
    color: "text-blue-400",
    bgColor: "bg-blue-400/10",
    borderColor: "border-blue-400/30",
    glowColor: "shadow-blue-400/20",
    description: "Knowledge, preparation, and tactical advantage",
  },
  fortune: {
    label: "Fortune",
    icon: Coins,
    color: "text-yellow-400",
    bgColor: "bg-yellow-400/10",
    borderColor: "border-yellow-400/30",
    glowColor: "shadow-yellow-400/20",
    description: "Wealth, luck, and better rewards",
  },
} as const;

const BRANCHES = ["resilience", "insight", "fortune"] as const;

export function AttunementPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnTo = searchParams.get("returnTo");

  const { activeCampaignId } = useCampaignStore();
  const { talents, talentEssence, meta, loading, fetchTalents, fetchMeta, unlockTalent } = useMetaStore();

  useEffect(() => {
    if (activeCampaignId) {
      fetchTalents(activeCampaignId);
      fetchMeta(activeCampaignId);
    }
  }, [activeCampaignId, fetchTalents, fetchMeta]);

  if (!activeCampaignId) {
    return (
      <EmptyState
        icon={<GitBranch size={48} />}
        title="No Campaign Selected"
        description="Select or create a campaign from the Nexus first."
        action={<Button onClick={() => navigate("/")}>Go to Nexus</Button>}
      />
    );
  }

  const handleUnlock = async (talentId: string) => {
    if (!activeCampaignId) return;
    await unlockTalent(activeCampaignId, talentId);
  };

  const unlockedCount = talents.filter((t) => t.is_unlocked).length;
  const lifetimeEssence = meta?.essence_lifetime ?? 0;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <PageHeader
        title="Armillary Attunement"
        subtitle="Channel essence into the Armillary's talent matrix to unlock permanent advantages"
        action={
          <div className="flex items-center gap-3">
            <Badge color="purple" className="text-base px-3 py-1">
              <Sparkles size={14} className="inline mr-1" />
              {talentEssence} Essence
            </Badge>
          </div>
        }
      />

      {returnTo && (
        <Button
          variant="secondary"
          size="md"
          icon={<ArrowLeft size={16} />}
          onClick={() => navigate(returnTo)}
        >
          Return to Expedition
        </Button>
      )}

      {/* Essence Stats Bar */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card padding="sm">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <Sparkles size={14} className="text-purple-400" />
                <span className="text-gray-400">Available:</span>
                <span className="font-bold text-purple-400">{talentEssence}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-gray-500">Lifetime:</span>
                <span className="font-medium text-gray-400">{lifetimeEssence}</span>
              </div>
            </div>
            <div className="text-gray-500">
              {unlockedCount} / {talents.length} talents unlocked
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Talent Tree — 3 Columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {BRANCHES.map((branch, bi) => {
          const config = BRANCH_CONFIG[branch];
          const Icon = config.icon;
          const branchTalents = talents
            .filter((t) => t.branch === branch)
            .sort((a, b) => a.tier - b.tier);

          return (
            <motion.div
              key={branch}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + bi * 0.1 }}
              className="space-y-3"
            >
              {/* Branch Header */}
              <div className={clsx("text-center py-3 rounded-lg border", config.bgColor, config.borderColor)}>
                <Icon size={24} className={clsx("mx-auto mb-1", config.color)} />
                <h2 className={clsx("font-display font-bold text-lg", config.color)}>
                  {config.label}
                </h2>
                <p className="text-xs text-gray-500 mt-0.5">{config.description}</p>
              </div>

              {/* Connection Line + Talent Cards */}
              <div className="relative space-y-2">
                {/* Vertical connector */}
                {branchTalents.length > 1 && (
                  <div className="absolute left-1/2 top-0 bottom-0 w-px bg-surface-3/60 -translate-x-1/2 z-0" />
                )}

                <AnimatePresence>
                  {branchTalents.map((talent, ti) => {
                    const canUnlockNow = !talent.is_unlocked && talent.can_afford && talent.prerequisite_met;
                    const isLocked = !talent.is_unlocked && !canUnlockNow;

                    return (
                      <motion.div
                        key={talent.id}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3 + ti * 0.06 }}
                        className="relative z-10"
                      >
                        <Card
                          padding="md"
                          className={clsx(
                            "transition-all duration-300",
                            talent.is_unlocked && [config.borderColor, "border", config.glowColor, "shadow-lg"],
                            canUnlockNow && "border border-accent/40 hover:border-accent/70 cursor-pointer",
                            isLocked && "opacity-50",
                          )}
                          onClick={canUnlockNow ? () => handleUnlock(talent.id) : undefined}
                          hover={canUnlockNow}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-display font-semibold text-sm text-white">
                                  {talent.name}
                                </span>
                                <Badge color="gray" className="text-[10px]">
                                  T{talent.tier}
                                </Badge>
                              </div>
                              <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                                {talent.description}
                              </p>
                            </div>

                            <div className="flex-shrink-0">
                              {talent.is_unlocked ? (
                                <div className={clsx("p-1.5 rounded-full", config.bgColor)}>
                                  <Check size={14} className={config.color} />
                                </div>
                              ) : canUnlockNow ? (
                                <Button
                                  variant="primary"
                                  size="sm"
                                  loading={loading}
                                  onClick={(e: React.MouseEvent) => {
                                    e.stopPropagation();
                                    handleUnlock(talent.id);
                                  }}
                                >
                                  <Sparkles size={12} className="mr-1" />
                                  {talent.cost}
                                </Button>
                              ) : (
                                <div className="p-1.5 rounded-full bg-surface-2">
                                  <Lock size={14} className="text-gray-600" />
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Cost / Status line */}
                          {!talent.is_unlocked && (
                            <div className="flex items-center gap-2 mt-2 text-[11px]">
                              <span className={clsx(
                                "flex items-center gap-1",
                                talent.can_afford ? "text-purple-400" : "text-gray-600",
                              )}>
                                <Sparkles size={10} />
                                {talent.cost} essence
                              </span>
                              {!talent.prerequisite_met && (
                                <span className="flex items-center gap-1 text-gray-600">
                                  <ChevronUp size={10} />
                                  Requires Tier {talent.tier - 1}
                                </span>
                              )}
                            </div>
                          )}
                        </Card>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
