import { useMemo, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { useToastStore } from "@/stores/useToastStore";
import { Card, Badge, Button, ProgressBar } from "@/components/ui";
import {
  Trophy, Skull, Home, BookOpen, Play, Coins, Sparkles, Clock, Layers, Swords,
  GitBranch, ScrollText, CheckCircle2, Copy,
} from "lucide-react";
import { generateSessionMarkdown, copyToClipboard } from "@/lib/sessionExport";
import { motion } from "framer-motion";
import { clsx } from "clsx";

function formatDuration(startedAt: string): string {
  const start = new Date(startedAt).getTime();
  const now = Date.now();
  const totalSeconds = Math.floor((now - start) / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
  if (minutes > 0) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

export function RunCompletePage() {
  const navigate = useNavigate();
  const { run, reset } = useRunStore();
  const { activeCampaignId } = useCampaignStore();
  const { lastRunMeta, completeRunMeta, clearLastRunMeta } = useMetaStore();

  const isVictory = run?.outcome === "completed";

  // Trigger meta-progression computation on mount
  useEffect(() => {
    if (activeCampaignId && run?.id && !lastRunMeta) {
      completeRunMeta(activeCampaignId, run.id).catch((err) => {
        console.error("[RunComplete] Meta computation failed:", err);
      });
    }
  }, [activeCampaignId, run?.id, lastRunMeta, completeRunMeta]);
  const duration = useMemo(
    () => (run?.started_at ? formatDuration(run.started_at) : "--"),
    [run?.started_at],
  );

  const addToast = useToastStore((s) => s.addToast);

  const handleReturnToLobby = () => {
    clearLastRunMeta();
    reset();
    navigate("/");
  };

  const handleExport = useCallback(async () => {
    if (!run) return;
    const md = generateSessionMarkdown(run, lastRunMeta ?? null);
    const ok = await copyToClipboard(md);
    if (ok) {
      addToast("Session summary copied to clipboard!", "success");
    } else {
      addToast("Failed to copy — check browser permissions.", "error");
    }
  }, [run, lastRunMeta, addToast]);

  if (!run) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-gray-400">No run data available.</p>
          <Button onClick={() => navigate("/")}>Return to Lobby</Button>
        </div>
      </div>
    );
  }

  const stats = [
    { icon: Layers, label: "Floors", value: `${run.floors_completed} / ${run.floor_count}`, color: "text-white" },
    { icon: Coins, label: "Gold", value: run.total_gold_earned.toLocaleString(), color: "text-gold" },
    { icon: Sparkles, label: "Shards", value: run.total_shards_earned.toLocaleString(), color: "text-shard" },
    { icon: Clock, label: "Duration", value: duration, color: "text-white" },
    { icon: Swords, label: "Starting Level", value: String(run.starting_level), color: "text-white" },
    { icon: Swords, label: "Favour", value: String(run.armillary_favour), color: "text-accent" },
    ...(run.seed ? [{ icon: GitBranch, label: "Seed", value: String(run.seed), color: "text-gray-400" }] : []),
  ];

  return (
    <div className="space-y-8 max-w-2xl mx-auto py-8">
      {/* Hero Banner */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-4"
      >
        <motion.div
          initial={{ y: -20 }}
          animate={{ y: 0 }}
          transition={{ type: "spring", stiffness: 150, delay: 0.2 }}
        >
          {isVictory ? (
            <Trophy size={56} className="mx-auto text-gold animate-float" />
          ) : (
            <Skull size={56} className="mx-auto text-red-500" />
          )}
        </motion.div>

        <h1 className={clsx(
          "text-4xl font-display font-bold",
          isVictory ? "text-gradient-gold" : "text-red-500"
        )}>
          {isVictory ? "Victory!" : "Defeat"}
        </h1>
        <p className="text-gray-400">
          {isVictory
            ? "Your party has conquered the Armillary."
            : "The Armillary has claimed your party."}
        </p>
      </motion.div>

      {/* Floor progress */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <ProgressBar
          value={run.floors_completed}
          max={run.floor_count}
          label={`Floors: ${run.floors_completed} / ${run.floor_count}`}
          color={isVictory ? "gold" : "red"}
          size="md"
        />
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card padding="lg">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Run Statistics
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {stats.map((stat, i) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 + i * 0.08 }}
                  className="text-center"
                >
                  <Icon size={16} className="mx-auto text-gray-500 mb-1" />
                  <div className={clsx("text-xl font-bold font-display", stat.color)}>
                    {stat.value}
                  </div>
                  <div className="text-xs text-gray-500">{stat.label}</div>
                </motion.div>
              );
            })}
          </div>
        </Card>
      </motion.div>

      {/* Meta-Progression Rewards */}
      {lastRunMeta && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="space-y-4"
        >
          {/* Essence Earned */}
          <Card glow padding="lg" className="border-purple-400/30 text-center">
            <Sparkles size={28} className="mx-auto text-purple-400 mb-2" />
            <div className="text-3xl font-bold font-display text-purple-400">
              +{lastRunMeta.essence_earned}
            </div>
            <div className="text-sm text-gray-400 mt-1">Essence Earned</div>
            <div className="text-xs text-gray-600 mt-2">
              Total: {lastRunMeta.total_essence} essence
            </div>
          </Card>

          {/* New Achievements */}
          {lastRunMeta.new_achievements.length > 0 && (
            <Card padding="lg">
              <h2 className="text-sm font-semibold text-gold uppercase tracking-wider mb-3 flex items-center gap-2">
                <Trophy size={14} />
                Achievements Unlocked
              </h2>
              <div className="space-y-2">
                {lastRunMeta.new_achievements.map((a, i) => (
                  <motion.div
                    key={a.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.0 + i * 0.15 }}
                    className="flex items-center justify-between py-2 border-b border-surface-3 last:border-0"
                  >
                    <div className="flex items-center gap-2">
                      <CheckCircle2 size={16} className="text-emerald-400" />
                      <div>
                        <div className="text-sm font-semibold text-white">{a.name}</div>
                        <div className="text-xs text-gray-500">{a.description}</div>
                      </div>
                    </div>
                    <Badge color="purple" className="text-xs">
                      <Sparkles size={10} className="inline mr-0.5" />
                      +{a.essence_reward}
                    </Badge>
                  </motion.div>
                ))}
              </div>
            </Card>
          )}

          {/* Lore Discovered */}
          {lastRunMeta.lore_fragments_discovered.length > 0 && (
            <Card padding="lg">
              <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <ScrollText size={14} />
                Lore Discovered
              </h2>
              <div className="space-y-2">
                {lastRunMeta.lore_fragments_discovered.map((f, i) => (
                  <motion.div
                    key={f.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.2 + i * 0.15 }}
                    className="py-2 border-b border-surface-3 last:border-0"
                  >
                    <div className="flex items-center gap-2">
                      <ScrollText size={14} className="text-blue-400" />
                      <span className="text-sm font-semibold text-white">{f.title}</span>
                      <Badge color="blue" className="text-[10px]">{f.category}</Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 ml-6 italic">{f.text}</p>
                  </motion.div>
                ))}
              </div>
            </Card>
          )}

          {/* Talent Hint */}
          {lastRunMeta.talents_affordable > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.4 }}
            >
              <Card
                padding="md"
                hover
                className="border-purple-400/20 cursor-pointer"
                onClick={() => { clearLastRunMeta(); navigate("/attunement"); }}
              >
                <div className="flex items-center gap-3">
                  <GitBranch size={20} className="text-purple-400" />
                  <div>
                    <div className="text-sm font-semibold text-purple-400">
                      {lastRunMeta.talents_affordable} talent{lastRunMeta.talents_affordable !== 1 ? "s" : ""} now unlockable!
                    </div>
                    <div className="text-xs text-gray-500">Visit the Attunement to spend your essence</div>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* Actions */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: lastRunMeta ? 1.6 : 1.0 }}
        className="flex flex-col sm:flex-row gap-3"
      >
        <Button
          variant="primary"
          size="lg"
          icon={<Home size={18} />}
          onClick={handleReturnToLobby}
          className="flex-1"
        >
          Return to Lobby
        </Button>
        <Button
          variant="secondary"
          size="lg"
          icon={<BookOpen size={16} />}
          onClick={() => navigate("/archive")}
          className="flex-1"
        >
          View Archive
        </Button>
        <Button
          variant="secondary"
          size="lg"
          icon={<Play size={16} />}
          onClick={() => { clearLastRunMeta(); reset(); navigate("/run/setup"); }}
          className="flex-1"
        >
          New Run
        </Button>
        <Button
          variant="ghost"
          size="lg"
          icon={<Copy size={16} />}
          onClick={handleExport}
          className="flex-1"
        >
          Export Summary
        </Button>
      </motion.div>
    </div>
  );
}
