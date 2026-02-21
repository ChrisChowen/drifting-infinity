import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useRunStore } from "@/stores/useRunStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { Card, Badge, Button, EmptyState } from "@/components/ui";
import {
  Users, Play, Sparkles, BookOpen, RotateCcw, Trophy, ScrollText,
  GitBranch, Swords, Layers, Shield, Plus,
} from "lucide-react";
import { motion } from "framer-motion";
import { clsx } from "clsx";
import { getArbiterQuote } from "@/constants/lore";
import { TypewriterText } from "@/components/transitions/TypewriterText";
import { ArmillaryOrb } from "@/components/combat/ArmillaryOrb";

export function DashboardPage() {
  const navigate = useNavigate();
  const { campaigns, activeCampaignId, characters, fetchCampaigns, loading } = useCampaignStore();
  const { loadActiveRun, run } = useRunStore();
  const { meta, talents, lastRunMeta, fetchMeta, fetchTalents, clearLastRunMeta } = useMetaStore();

  useEffect(() => {
    fetchCampaigns();
  }, [fetchCampaigns]);

  useEffect(() => {
    if (activeCampaignId) {
      loadActiveRun(activeCampaignId);
      fetchMeta(activeCampaignId);
      fetchTalents(activeCampaignId);
    }
  }, [activeCampaignId, loadActiveRun, fetchMeta, fetchTalents]);

  // Redirect to welcome if no campaigns after loading
  useEffect(() => {
    if (!loading && campaigns.length === 0) {
      navigate("/welcome");
    }
  }, [loading, campaigns.length, navigate]);

  const activeCampaign = campaigns.find((c) => c.id === activeCampaignId);
  const hasActiveRun = run && !run.outcome;

  const essenceBalance = meta?.essence_balance ?? 0;
  const unlockedTalents = meta?.unlocked_talents?.length ?? 0;
  const earnedAchievements = meta?.achievements?.length ?? 0;
  const totalRuns = meta?.total_runs_completed ?? activeCampaign?.total_runs ?? 0;
  const totalWins = meta?.total_runs_won ?? 0;
  const highestFloor = meta?.highest_floor_reached ?? 0;
  const survivalRate = totalRuns > 0 ? Math.round((totalWins / totalRuns) * 100) : 0;
  const affordableTalents = talents.filter(
    (t) => !t.is_unlocked && t.can_afford && t.prerequisite_met,
  ).length;

  const arbiterQuote = useMemo(() => getArbiterQuote("lobby"), []);

  if (!activeCampaignId || !activeCampaign) {
    return (
      <EmptyState
        icon={<BookOpen size={48} />}
        title="No Campaign Selected"
        description="Create a campaign to begin your descent into the Armillary."
        action={<Button onClick={() => navigate("/campaign/new")}>Create Campaign</Button>}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Section 1: Hero Banner ─────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <HeroBanner
          hasActiveRun={!!hasActiveRun}
          hasCharacters={characters.length > 0}
          hasRuns={totalRuns > 0}
          affordableTalents={affordableTalents}
          essenceBalance={essenceBalance}
          arbiterQuote={arbiterQuote}
          run={run}
          onNavigate={navigate}
        />
      </motion.div>

      {/* ── Section 2: Party + Progression ──────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Party Overview */}
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15 }}
        >
          <Card
            padding="lg"
            hover
            onClick={() => navigate("/party")}
            className="cursor-pointer h-full"
          >
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                <Users size={14} />
                The Roster
              </h2>
              <Badge color="gray">{characters.length} champions</Badge>
            </div>

            {characters.length === 0 ? (
              <div className="text-center py-6">
                <Users size={24} className="mx-auto text-gray-600 mb-2" />
                <p className="text-sm text-gray-500 mb-3">No champions recruited yet.</p>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<Plus size={14} />}
                  onClick={(e: React.MouseEvent) => { e.stopPropagation(); navigate("/party/add"); }}
                >
                  Add Champion
                </Button>
              </div>
            ) : (
              <div className="space-y-1.5">
                {characters.slice(0, 5).map((char) => (
                  <div
                    key={char.id}
                    className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-surface-2/50 transition-colors"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-7 h-7 rounded-full bg-surface-3 flex items-center justify-center text-xs font-display font-bold text-accent flex-shrink-0">
                        {char.name.charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <div className="text-sm font-medium text-white truncate">{char.name}</div>
                        <div className="text-[11px] text-gray-500">
                          {char.character_class}{char.subclass ? ` \u2014 ${char.subclass}` : ""}
                        </div>
                      </div>
                    </div>
                    <Badge
                      color={char.is_dead ? "red" : "gold"}
                      className="text-[10px] flex-shrink-0"
                    >
                      {char.is_dead ? "Fallen" : `Lv ${char.level}`}
                    </Badge>
                  </div>
                ))}
                {characters.length > 5 && (
                  <p className="text-xs text-gray-500 text-center pt-1">
                    +{characters.length - 5} more champions
                  </p>
                )}
              </div>
            )}
          </Card>
        </motion.div>

        {/* Progression Stats */}
        <motion.div
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card padding="lg" className="h-full">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2 mb-3">
              <Sparkles size={14} />
              Progression
            </h2>

            <div className="grid grid-cols-2 gap-4">
              <StatBlock
                icon={<Swords size={14} />}
                label="Expeditions"
                value={String(totalRuns)}
                color="text-white"
              />
              <StatBlock
                icon={<Layers size={14} />}
                label="Highest Floor"
                value={highestFloor > 0 ? `Floor ${highestFloor}` : "\u2014"}
                color="text-accent"
              />
              <StatBlock
                icon={<Shield size={14} />}
                label="Survival Rate"
                value={totalRuns > 0 ? `${survivalRate}%` : "\u2014"}
                color={survivalRate >= 50 ? "text-emerald-400" : survivalRate > 0 ? "text-red-400" : "text-gray-500"}
              />
              <StatBlock
                icon={<GitBranch size={14} />}
                label="Talents"
                value={`${unlockedTalents} / ${talents.length || 15}`}
                color="text-purple-400"
              />
            </div>

            {/* Mini achievements/lore summary */}
            <div className="border-t border-surface-3 mt-4 pt-3 flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-xs">
                <Trophy size={12} className="text-gold" />
                <span className="text-gray-400">{earnedAchievements} achievements</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs">
                <ScrollText size={12} className="text-blue-400" />
                <span className="text-gray-400">{meta?.lore_fragments_found?.length ?? 0} lore</span>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* ── Section 3: Recent Activity ──────────────────────────────── */}
      {(lastRunMeta || totalRuns > 0) && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card padding="lg">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Recent Activity
            </h2>

            {lastRunMeta ? (
              <div className="space-y-3">
                {/* Essence earned */}
                <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-purple-500/5 border border-purple-500/10">
                  <div className="flex items-center gap-2">
                    <Sparkles size={14} className="text-purple-400" />
                    <span className="text-sm text-gray-300">Essence earned last run</span>
                  </div>
                  <span className="text-sm font-bold text-purple-400">+{lastRunMeta.essence_earned}</span>
                </div>

                {/* New achievements */}
                {lastRunMeta.new_achievements.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Trophy size={14} className="text-gold" />
                    <span className="text-gray-400">
                      {lastRunMeta.new_achievements.length} new achievement{lastRunMeta.new_achievements.length !== 1 ? "s" : ""} unlocked
                    </span>
                  </div>
                )}

                {/* New lore */}
                {lastRunMeta.lore_fragments_discovered.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <ScrollText size={14} className="text-blue-400" />
                    <span className="text-gray-400">
                      {lastRunMeta.lore_fragments_discovered.length} lore fragment{lastRunMeta.lore_fragments_discovered.length !== 1 ? "s" : ""} discovered
                    </span>
                  </div>
                )}

                <button
                  onClick={() => { clearLastRunMeta(); }}
                  className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
                >
                  Dismiss
                </button>
              </div>
            ) : (
              <p className="text-sm text-gray-500 italic font-display">
                {totalRuns > 0
                  ? `${totalRuns} expedition${totalRuns !== 1 ? "s" : ""} completed. The Armillary awaits your next descent.`
                  : "No expeditions recorded yet."}
              </p>
            )}
          </Card>
        </motion.div>
      )}
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────

function HeroBanner({
  hasActiveRun,
  hasCharacters,
  hasRuns,
  affordableTalents,
  essenceBalance,
  arbiterQuote,
  run,
  onNavigate,
}: {
  hasActiveRun: boolean;
  hasCharacters: boolean;
  hasRuns: boolean;
  affordableTalents: number;
  essenceBalance: number;
  arbiterQuote: string;
  run: { floors_completed?: number; floor_count?: number } | null;
  onNavigate: (to: string) => void;
}) {
  // Priority-based banner content
  if (hasActiveRun && run) {
    return (
      <Card glow padding="lg" className="border-amber-500/20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display font-bold text-amber-400 text-lg">
              Expedition in Progress
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              Floor {(run.floors_completed ?? 0) + 1} of {run.floor_count ?? 4} \u2014 The Armillary awaits your return
            </p>
          </div>
          <Button
            variant="primary"
            icon={<RotateCcw size={16} />}
            onClick={() => onNavigate("/run/setup")}
          >
            Resume
          </Button>
        </div>
      </Card>
    );
  }

  if (!hasCharacters) {
    return (
      <Card glow padding="lg" className="border-accent/20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display font-bold text-accent text-lg">
              Your Party Awaits
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              Recruit champions before descending into the Armillary.
            </p>
          </div>
          <Button
            variant="primary"
            icon={<Users size={16} />}
            onClick={() => onNavigate("/party/add")}
          >
            Add Champion
          </Button>
        </div>
      </Card>
    );
  }

  if (affordableTalents > 0) {
    return (
      <Card glow padding="lg" className="border-purple-400/20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display font-bold text-purple-400 text-lg">
              New Talents Available
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              {affordableTalents} talent{affordableTalents !== 1 ? "s" : ""} ready to unlock \u2014 channel your {essenceBalance} essence.
            </p>
            <p className="text-xs text-gray-600 mt-2 italic font-display">
              "{arbiterQuote}"
            </p>
          </div>
          <Button
            variant="secondary"
            icon={<GitBranch size={16} />}
            onClick={() => onNavigate("/attunement")}
          >
            Attune
          </Button>
        </div>
      </Card>
    );
  }

  if (!hasRuns) {
    return (
      <Card glow padding="lg" className="border-accent/20 relative overflow-hidden">
        <div className="flex items-center justify-between relative z-10">
          <div className="flex-1">
            <h2 className="font-display font-bold text-accent text-xl">
              The Armillary Beckons
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              Your party is assembled. Begin your first descent into the arena.
            </p>
            <div className="mt-3">
              <TypewriterText
                text={`"${arbiterQuote}"`}
                speed={30}
                delay={500}
                className="text-xs text-gray-600 italic font-display"
                cursorColor="bg-accent"
              />
            </div>
          </div>
          <div className="flex flex-col items-center gap-3 ml-6">
            <ArmillaryOrb size="lg" intensity={0.6} />
            <Button
              variant="primary"
              glow
              icon={<Play size={16} />}
              onClick={() => onNavigate("/run/setup")}
            >
              Begin Expedition
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  // Default: between runs
  return (
    <Card padding="lg" className="relative overflow-hidden">
      <div className="flex items-center gap-6">
        <ArmillaryOrb size="md" intensity={0.3} />
        <div className="flex-1">
          <TypewriterText
            text={`"${arbiterQuote}"`}
            speed={25}
            delay={300}
            className="text-sm text-gray-500 italic font-display"
            cursorColor="bg-accent"
          />
          <p className="text-[11px] text-accent mt-2">— The Arbiter</p>
        </div>
        <Button
          variant="primary"
          glow
          icon={<Play size={16} />}
          onClick={() => onNavigate("/run/setup")}
        >
          New Expedition
        </Button>
      </div>
    </Card>
  );
}

function StatBlock({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <motion.div
      className="flex items-start gap-2.5 py-2"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className={clsx("p-1.5 rounded-lg bg-surface-2 flex-shrink-0 mt-0.5", color)}>
        {icon}
      </div>
      <div>
        <div className={clsx("text-lg font-bold font-display", color)}>{value}</div>
        <div className="text-[11px] text-gray-500">{label}</div>
      </div>
    </motion.div>
  );
}
