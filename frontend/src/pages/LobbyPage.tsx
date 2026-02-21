import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useRunStore } from "@/stores/useRunStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { Button, Card, Badge, PageHeader } from "@/components/ui";
import {
  Play, Users, Anvil, Sparkles, BookOpen, Settings, Plus, Coins, RotateCcw,
  GitBranch, ScrollText, Trophy,
} from "lucide-react";
import { clsx } from "clsx";
import { motion } from "framer-motion";
import {
  SCREEN_DESCRIPTIONS, NAV_LABELS, getArbiterQuote,
} from "@/constants/lore";

const QUICK_ACTIONS = [
  { key: "party" as const, icon: Users, to: "/party" },
  { key: "forge" as const, icon: Anvil, to: "/forge" },
  { key: "gacha" as const, icon: Sparkles, to: "/gacha" },
  { key: "archive" as const, icon: BookOpen, to: "/archive" },
  { key: "settings" as const, icon: Settings, to: "/settings" },
] as const;

export function LobbyPage() {
  const navigate = useNavigate();
  const { campaigns, activeCampaignId, characters, loading, fetchCampaigns, setActiveCampaign } = useCampaignStore();
  const { loadActiveRun, run } = useRunStore();
  const { goldBalance, astralShardBalance, fetchBalance } = useEconomyStore();
  const { meta, talents, fetchMeta, fetchTalents } = useMetaStore();

  useEffect(() => {
    fetchCampaigns();
  }, [fetchCampaigns]);

  useEffect(() => {
    if (activeCampaignId) {
      fetchBalance(activeCampaignId);
      loadActiveRun(activeCampaignId);
      fetchMeta(activeCampaignId);
      fetchTalents(activeCampaignId);
    }
  }, [activeCampaignId, fetchBalance, loadActiveRun, fetchMeta, fetchTalents]);

  // Redirect to welcome if no campaigns after loading
  useEffect(() => {
    if (!loading && campaigns.length === 0) {
      navigate("/welcome");
    }
  }, [loading, campaigns.length, navigate]);

  const activeCampaign = campaigns.find((c) => c.id === activeCampaignId);
  const avgLevel = characters.length > 0
    ? Math.max(1, Math.floor(characters.reduce((s, c) => s + c.level, 0) / characters.length))
    : 0;
  const hasActiveRun = run && !run.outcome;

  const essenceBalance = meta?.essence_balance ?? 0;
  const unlockedTalents = meta?.unlocked_talents?.length ?? 0;
  const earnedAchievements = meta?.achievements?.length ?? 0;
  const loreFound = meta?.lore_fragments_found?.length ?? 0;
  const affordableTalents = talents.filter(
    (t) => !t.is_unlocked && t.can_afford && t.prerequisite_met,
  ).length;

  // Stable Arbiter quote for this render
  const arbiterQuote = useMemo(() => getArbiterQuote("lobby"), []);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <PageHeader
        title="The Nexus"
        subtitle={SCREEN_DESCRIPTIONS.lobby}
        action={
          <Button
            variant="secondary"
            size="sm"
            icon={<Plus size={16} />}
            onClick={() => navigate("/campaign/new")}
          >
            New Campaign
          </Button>
        }
      />

      {/* Arbiter Quote */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="text-center"
      >
        <p className="text-sm text-gray-500 italic font-display">
          "{arbiterQuote}"
        </p>
      </motion.div>

      {/* Campaign Selection */}
      <section className="space-y-3">
        {campaigns.map((c, i) => (
          <motion.div
            key={c.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card
              hover
              selected={c.id === activeCampaignId}
              onClick={() => setActiveCampaign(c.id)}
              className="cursor-pointer"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-display font-semibold text-white">{c.name}</h3>
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                    <span>{c.total_runs} expeditions</span>
                    <span>Armillary Assessment: {c.party_power_coefficient.toFixed(2)}</span>
                  </div>
                </div>
                {c.id === activeCampaignId && (
                  <Badge color="gold">Active</Badge>
                )}
              </div>
            </Card>
          </motion.div>
        ))}
      </section>

      {/* Active Campaign Dashboard */}
      {activeCampaign && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-6"
        >
          {/* Resume Run Banner */}
          {hasActiveRun && (
            <Card glow padding="lg" className="border-accent/30">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-display font-semibold text-accent">Expedition in Progress</h3>
                  <p className="text-sm text-gray-400 mt-1">
                    Floor {run.floors_completed + 1} of {run.floor_count} — The Armillary awaits your return
                  </p>
                </div>
                <Button
                  variant="primary"
                  icon={<RotateCcw size={16} />}
                  onClick={() => navigate("/run/setup")}
                >
                  Resume Expedition
                </Button>
              </div>
            </Card>
          )}

          {/* Stats Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Card padding="sm">
              <div className="flex items-center gap-2">
                <Coins size={16} className="text-gold" />
                <div>
                  <div className="text-lg font-bold text-gold">{goldBalance}</div>
                  <div className="text-xs text-gray-500">Gold</div>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div className="flex items-center gap-2">
                <Sparkles size={16} className="text-shard" />
                <div>
                  <div className="text-lg font-bold text-shard">{astralShardBalance}</div>
                  <div className="text-xs text-gray-500">Astral Shards</div>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div className="flex items-center gap-2">
                <Users size={16} className="text-gray-400" />
                <div>
                  <div className="text-lg font-bold text-white">{characters.length}</div>
                  <div className="text-xs text-gray-500">Champions</div>
                </div>
              </div>
            </Card>
            <Card padding="sm">
              <div>
                <div className={clsx("text-lg font-bold", avgLevel > 0 ? "text-emerald-400" : "text-gray-600")}>
                  {avgLevel > 0 ? `Lv ${avgLevel}` : "—"}
                </div>
                <div className="text-xs text-gray-500">Avg Level</div>
              </div>
            </Card>
          </div>

          {/* Meta-Progression Stats */}
          {meta && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <Card padding="sm">
                <div className="flex items-center gap-2">
                  <Sparkles size={16} className="text-purple-400" />
                  <div>
                    <div className="text-lg font-bold text-purple-400">{essenceBalance}</div>
                    <div className="text-xs text-gray-500">Essence</div>
                  </div>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center gap-2">
                  <GitBranch size={16} className="text-accent" />
                  <div>
                    <div className="text-lg font-bold text-white">{unlockedTalents} / {talents.length || 15}</div>
                    <div className="text-xs text-gray-500">Talents</div>
                  </div>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center gap-2">
                  <Trophy size={16} className="text-gold" />
                  <div>
                    <div className="text-lg font-bold text-gold">{earnedAchievements}</div>
                    <div className="text-xs text-gray-500">Achievements</div>
                  </div>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center gap-2">
                  <ScrollText size={16} className="text-blue-400" />
                  <div>
                    <div className="text-lg font-bold text-blue-400">{loreFound}</div>
                    <div className="text-xs text-gray-500">Lore Fragments</div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Talent Available Callout */}
          {affordableTalents > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <Card glow padding="md" className="border-purple-400/30 cursor-pointer" onClick={() => navigate("/attunement")}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-purple-400/10">
                      <GitBranch size={20} className="text-purple-400" />
                    </div>
                    <div>
                      <h3 className="font-display font-semibold text-purple-400 text-sm">
                        New Talents Available!
                      </h3>
                      <p className="text-xs text-gray-500">
                        {affordableTalents} talent{affordableTalents !== 1 ? "s" : ""} ready to unlock
                      </p>
                    </div>
                  </div>
                  <Button variant="secondary" size="sm" icon={<GitBranch size={14} />}>
                    Attune
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Quick Actions */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {!hasActiveRun && (
              <Button
                variant="success"
                size="lg"
                icon={<Play size={18} />}
                onClick={() => navigate("/run/setup")}
                className="col-span-2 sm:col-span-1"
              >
                Begin Expedition
              </Button>
            )}
            <Button
              variant="secondary"
              size="lg"
              icon={<GitBranch size={18} />}
              onClick={() => navigate("/attunement")}
              title="Channel essence into permanent talents"
            >
              Attunement
            </Button>
            <Button
              variant="secondary"
              size="lg"
              icon={<ScrollText size={18} />}
              onClick={() => navigate("/chronicles")}
              title="View lore fragments and achievements"
            >
              Chronicles
            </Button>
            {QUICK_ACTIONS.map(({ key, icon: Icon, to }) => {
              const nav = NAV_LABELS[key];
              return (
                <Button
                  key={key}
                  variant="secondary"
                  size="lg"
                  icon={<Icon size={18} />}
                  onClick={() => navigate(to)}
                  title={nav.tooltip}
                >
                  {nav.name}
                </Button>
              );
            })}
          </div>
        </motion.div>
      )}
    </div>
  );
}
