import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { archiveApi } from "@/api/economy";
import { Card, CardHeader, CardTitle, Badge, Button, PageHeader, EmptyState, LoadingState, Select } from "@/components/ui";
import { ScrollText, ArrowLeft, TrendingUp, Coins, Gem, Trophy, Layers, Percent } from "lucide-react";
import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

/* ------------------------------------------------------------------ */
/*  Local types (APIs return unknown)                                  */
/* ------------------------------------------------------------------ */

interface ArchiveStats {
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  abandoned_runs: number;
  total_gold_earned: number;
  total_shards_earned: number;
  average_floors_per_run: number;
  party_power_coefficient: number;
}

interface DifficultyCurvePoint {
  arena_index: number;
  planned: number;
  actual: number | null;
}

interface ArchiveRun {
  id: string;
  started_at: string;
  ended_at: string | null;
  starting_level: number;
  floor_count: number;
  floors_completed: number;
  total_gold_earned: number;
  total_shards_earned: number;
  outcome: string | null;
  difficulty_curve: DifficultyCurvePoint[];
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function outcomeLabel(outcome: string | null): string {
  if (!outcome) return "In Progress";
  switch (outcome.toLowerCase()) {
    case "completed":
      return "Completed";
    case "failed":
      return "Failed";
    case "abandoned":
      return "Abandoned";
    default:
      return outcome;
  }
}

function outcomeBadgeColor(outcome: string | null): "blue" | "emerald" | "red" | "gray" {
  if (!outcome) return "blue";
  switch (outcome.toLowerCase()) {
    case "completed":
      return "emerald";
    case "failed":
      return "red";
    default:
      return "gray";
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDuration(start: string, end: string | null): string {
  if (!end) return "--";
  const ms = new Date(end).getTime() - new Date(start).getTime();
  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export function ArchivePage() {
  const navigate = useNavigate();
  const { activeCampaignId, campaigns } = useCampaignStore();
  const activeCampaign = campaigns.find((c) => c.id === activeCampaignId);

  const [stats, setStats] = useState<ArchiveStats | null>(null);
  const [runs, setRuns] = useState<ArchiveRun[]>([]);
  const [difficultyCurves, setDifficultyCurves] = useState<ArchiveRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRunId, setExpandedRunId] = useState<string | null>(null);
  const [selectedCurveRunId, setSelectedCurveRunId] = useState<string | null>(null);

  useEffect(() => {
    if (!activeCampaignId) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([
      archiveApi.getStats(activeCampaignId),
      archiveApi.getRunHistory(activeCampaignId, 50),
      archiveApi.getDifficultyCurves(activeCampaignId, 5),
    ])
      .then(([statsData, runsData, curvesData]) => {
        if (cancelled) return;
        setStats(statsData as ArchiveStats);
        setRuns(runsData as ArchiveRun[]);
        setDifficultyCurves(curvesData as ArchiveRun[]);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(String(err));
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [activeCampaignId]);

  /* ---- No active campaign ---- */
  if (!activeCampaignId) {
    return (
      <EmptyState
        icon={<ScrollText size={48} />}
        title="No Campaign Selected"
        description="Return to the lobby to select a campaign."
        action={
          <Button variant="secondary" icon={<ArrowLeft size={16} />} onClick={() => navigate("/")}>
            Back to Lobby
          </Button>
        }
      />
    );
  }

  /* ---- Loading ---- */
  if (loading) {
    return <LoadingState message="Consulting the archives..." />;
  }

  /* ---- Error ---- */
  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader title="Archive" subtitle="Campaign history & statistics" />
        <Card padding="md">
          <div className="text-red-400 text-sm">Failed to load archive data: {error}</div>
        </Card>
        <Button variant="secondary" icon={<ArrowLeft size={16} />} onClick={() => navigate("/")}>
          Back to Lobby
        </Button>
      </div>
    );
  }

  /* ---- Derived values ---- */
  const winRate =
    stats && stats.total_runs > 0
      ? ((stats.completed_runs / stats.total_runs) * 100).toFixed(1)
      : "0.0";

  const ppc =
    stats?.party_power_coefficient ??
    activeCampaign?.party_power_coefficient ??
    0;

  const curveRun =
    difficultyCurves.find((r) => r.id === selectedCurveRunId) ??
    difficultyCurves[0] ??
    null;

  const curveChartData = curveRun
    ? curveRun.difficulty_curve.map((pt) => ({
        arena_index: pt.arena_index,
        Planned: pt.planned,
        Actual: pt.actual,
      }))
    : [];

  const sortedRuns = [...runs].sort(
    (a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime()
  );

  const STAT_CARDS = [
    { label: "Expeditions", value: stats?.total_runs ?? 0, icon: <Trophy size={16} />, color: "text-white" },
    { label: "Survival Rate", value: `${winRate}%`, icon: <Percent size={16} />, color: "text-white" },
    { label: "Gold Plundered", value: (stats?.total_gold_earned ?? 0).toLocaleString(), icon: <Coins size={16} />, color: "text-gold" },
    { label: "Shards Gathered", value: (stats?.total_shards_earned ?? 0).toLocaleString(), icon: <Gem size={16} />, color: "text-shard" },
    { label: "Armillary Assessment", value: ppc.toFixed(2), icon: <TrendingUp size={16} />, color: "text-white" },
    { label: "Avg Depth", value: (stats?.average_floors_per_run ?? 0).toFixed(1), icon: <Layers size={16} />, color: "text-white" },
  ];

  /* ---- Render ---- */
  return (
    <div className="space-y-6">
      <PageHeader
        title="The Chronicle"
        subtitle={`Records of past expeditions${activeCampaign ? ` — ${activeCampaign.name}` : ""}`}
      />

      {/* ====== Section 1: Overview Stats Cards ====== */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {STAT_CARDS.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card padding="sm">
              <div className="flex items-center gap-2 text-gray-500 mb-1">
                {stat.icon}
                <span className="text-xs uppercase tracking-wide">{stat.label}</span>
              </div>
              <div className={`text-xl font-bold font-display ${stat.color}`}>{stat.value}</div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* ====== Section 2: Difficulty Curve Chart ====== */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card padding="lg">
          <CardHeader>
            <CardTitle>The Armillary's Intensity Pattern</CardTitle>
            {difficultyCurves.length > 0 && (
              <Select
                value={selectedCurveRunId ?? difficultyCurves[0]?.id ?? ""}
                onChange={(e) => setSelectedCurveRunId(e.target.value)}
                className="w-auto min-w-[180px]"
              >
                {difficultyCurves.map((run, i) => (
                  <option key={run.id} value={run.id}>
                    Run {difficultyCurves.length - i} — {formatDate(run.started_at)}
                  </option>
                ))}
              </Select>
            )}
          </CardHeader>

          {curveChartData.length > 0 ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={curveChartData}
                  margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis
                    dataKey="arena_index"
                    stroke="#888"
                    tick={{ fill: "#888", fontSize: 12 }}
                    label={{
                      value: "Arena Index",
                      position: "insideBottom",
                      offset: -2,
                      fill: "#888",
                      fontSize: 12,
                    }}
                  />
                  <YAxis
                    stroke="#888"
                    tick={{ fill: "#888", fontSize: 12 }}
                    label={{
                      value: "Difficulty",
                      angle: -90,
                      position: "insideLeft",
                      fill: "#888",
                      fontSize: 12,
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1A1A25",
                      border: "1px solid #242430",
                      borderRadius: "8px",
                      color: "#fff",
                    }}
                    labelStyle={{ color: "#888" }}
                  />
                  <Legend wrapperStyle={{ color: "#888" }} />
                  <Line
                    type="monotone"
                    dataKey="Planned"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    dot={{ fill: "#3B82F6", r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="Actual"
                    stroke="#F97316"
                    strokeWidth={2}
                    dot={{ fill: "#F97316", r: 3 }}
                    activeDot={{ r: 5 }}
                    connectNulls
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState
              icon={<TrendingUp size={32} />}
              title="No Curve Data"
              description="Complete some runs to see difficulty curve analysis."
              className="py-8"
            />
          )}
        </Card>
      </motion.div>

      {/* ====== Section 3: Run History Table ====== */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card padding="lg">
          <CardHeader>
            <CardTitle>Chapters of the Chronicle</CardTitle>
          </CardHeader>

          {sortedRuns.length === 0 ? (
            <EmptyState
              icon={<ScrollText size={32} />}
              title="No Chapters Yet"
              description="Begin your first expedition from the Nexus!"
              className="py-8"
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-3 text-gray-400 text-left">
                    <th className="pb-3 pr-4 font-medium">#</th>
                    <th className="pb-3 pr-4 font-medium">Date</th>
                    <th className="pb-3 pr-4 font-medium">Level</th>
                    <th className="pb-3 pr-4 font-medium">Floors</th>
                    <th className="pb-3 pr-4 font-medium">Outcome</th>
                    <th className="pb-3 pr-4 font-medium text-right">Gold</th>
                    <th className="pb-3 pr-4 font-medium text-right">Shards</th>
                    <th className="pb-3 font-medium text-right">Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedRuns.map((run, idx) => {
                    const isExpanded = expandedRunId === run.id;
                    const runNumber = sortedRuns.length - idx;

                    return (
                      <RunRow
                        key={run.id}
                        run={run}
                        runNumber={runNumber}
                        isExpanded={isExpanded}
                        onToggle={() =>
                          setExpandedRunId(isExpanded ? null : run.id)
                        }
                      />
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function RunRow({
  run,
  runNumber,
  isExpanded,
  onToggle,
}: {
  run: ArchiveRun;
  runNumber: number;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <>
      <tr
        className="border-b border-surface-3/50 hover:bg-surface-2/50 cursor-pointer transition-colors"
        onClick={onToggle}
      >
        <td className="py-3 pr-4 text-gray-400">{runNumber}</td>
        <td className="py-3 pr-4 text-white">{formatDate(run.started_at)}</td>
        <td className="py-3 pr-4 text-white">{run.starting_level}</td>
        <td className="py-3 pr-4 text-white">
          {run.floors_completed}
          <span className="text-gray-500">/{run.floor_count}</span>
        </td>
        <td className="py-3 pr-4">
          <Badge color={outcomeBadgeColor(run.outcome)}>
            {outcomeLabel(run.outcome)}
          </Badge>
        </td>
        <td className="py-3 pr-4 text-right text-gold">
          {run.total_gold_earned.toLocaleString()}
        </td>
        <td className="py-3 pr-4 text-right text-shard">
          {run.total_shards_earned.toLocaleString()}
        </td>
        <td className="py-3 text-right text-gray-400">
          {formatDuration(run.started_at, run.ended_at)}
        </td>
      </tr>

      {isExpanded && (
        <tr className="bg-surface-2/30">
          <td colSpan={8} className="px-4 py-4">
            <RunDetails run={run} />
          </td>
        </tr>
      )}
    </>
  );
}

function RunDetails({ run }: { run: ArchiveRun }) {
  const hasCurve =
    run.difficulty_curve && run.difficulty_curve.length > 0;

  const chartData = hasCurve
    ? run.difficulty_curve.map((pt) => ({
        arena_index: pt.arena_index,
        Planned: pt.planned,
        Actual: pt.actual,
      }))
    : [];

  return (
    <div className="space-y-4">
      {/* Run metadata */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
        <div>
          <span className="text-gray-400">Started:</span>{" "}
          <span className="text-white">
            {new Date(run.started_at).toLocaleString()}
          </span>
        </div>
        <div>
          <span className="text-gray-400">Ended:</span>{" "}
          <span className="text-white">
            {run.ended_at ? new Date(run.ended_at).toLocaleString() : "--"}
          </span>
        </div>
        <div>
          <span className="text-gray-400">Floors:</span>{" "}
          <span className="text-white">
            {run.floors_completed} / {run.floor_count}
          </span>
        </div>
        <div>
          <span className="text-gray-400">Duration:</span>{" "}
          <span className="text-white">
            {formatDuration(run.started_at, run.ended_at)}
          </span>
        </div>
      </div>

      {/* Inline difficulty curve for this run */}
      {hasCurve ? (
        <div className="h-48">
          <p className="text-xs text-gray-400 mb-2">
            Difficulty curve for this run
          </p>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                dataKey="arena_index"
                stroke="#888"
                tick={{ fill: "#888", fontSize: 11 }}
              />
              <YAxis
                stroke="#888"
                tick={{ fill: "#888", fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1A1A25",
                  border: "1px solid #242430",
                  borderRadius: "8px",
                  color: "#fff",
                }}
                labelStyle={{ color: "#888" }}
              />
              <Line
                type="monotone"
                dataKey="Planned"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: "#3B82F6", r: 2 }}
              />
              <Line
                type="monotone"
                dataKey="Actual"
                stroke="#F97316"
                strokeWidth={2}
                dot={{ fill: "#F97316", r: 2 }}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="text-xs text-gray-500">
          No difficulty curve data for this run.
        </p>
      )}
    </div>
  );
}
