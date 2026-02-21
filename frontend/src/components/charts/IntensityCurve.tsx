import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip as RTooltip,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { runsApi, type IntensityCurvePoint } from "@/api/runs";

interface IntensityCurveProps {
  runId: string;
  /** Compact sparkline mode for status bars */
  compact?: boolean;
}

const PHASE_COLORS: Record<string, string> = {
  warmup: "#60a5fa",
  escalation: "#f59e0b",
  climax: "#ef4444",
};

const DIFFICULTY_COLORS: Record<string, string> = {
  low: "#34d399",
  moderate: "#fbbf24",
  high: "#ef4444",
};

interface ChartPoint {
  label: string;
  planned: number;
  actual: number | null;
  phase: string;
  difficulty: string;
  actualDifficulty: string | null;
  isComplete: boolean;
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: ChartPoint }[];
}) {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-surface-1 border border-surface-3 rounded px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold text-white mb-1">{d.label}</div>
      <div className="flex items-center gap-2">
        <span className="text-gray-400">Planned:</span>
        <span
          className="font-medium"
          style={{ color: DIFFICULTY_COLORS[d.difficulty] ?? "#9ca3af" }}
        >
          {(d.planned * 100).toFixed(0)}% ({d.difficulty})
        </span>
      </div>
      {d.isComplete && d.actualDifficulty && (
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Actual:</span>
          <span
            className="font-medium"
            style={{
              color: DIFFICULTY_COLORS[d.actualDifficulty] ?? "#9ca3af",
            }}
          >
            {d.actualDifficulty}
          </span>
        </div>
      )}
      <div className="text-gray-500 mt-0.5 capitalize">{d.phase} phase</div>
    </div>
  );
}

export function IntensityCurve({ runId, compact = false }: IntensityCurveProps) {
  const { activeCampaignId } = useCampaignStore();
  const [points, setPoints] = useState<IntensityCurvePoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeCampaignId || !runId) return;
    let cancelled = false;
    runsApi
      .getIntensityCurve(activeCampaignId, runId)
      .then((res) => {
        if (!cancelled) setPoints(res.curve);
      })
      .catch(() => {
        /* silently fail — chart just won't show */
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeCampaignId, runId]);

  if (loading || points.length === 0) return null;

  const data: ChartPoint[] = points.map((p) => ({
    label: `F${p.floor} A${p.arena}`,
    planned: p.planned_intensity,
    actual: p.difficulty_target,
    phase: p.phase,
    difficulty: p.planned_difficulty,
    actualDifficulty: p.actual_difficulty,
    isComplete: p.is_complete,
  }));

  const completedPoints = data.filter((d) => d.isComplete && d.actual != null);

  const height = compact ? 40 : 120;

  if (compact) {
    return (
      <div className="w-full" style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
            <defs>
              <linearGradient id="intensityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="planned"
              stroke="#8b5cf6"
              strokeWidth={1.5}
              fill="url(#intensityGrad)"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 4, left: -20 }}>
          <defs>
            <linearGradient id="intensityGradFull" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="label"
            tick={{ fontSize: 9, fill: "#6b7280" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, 1]}
            tick={{ fontSize: 9, fill: "#6b7280" }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
          />
          <RTooltip
            content={<CustomTooltip />}
            cursor={{ stroke: "#6b7280", strokeDasharray: "3 3" }}
          />
          <Area
            type="monotone"
            dataKey="planned"
            stroke="#8b5cf6"
            strokeWidth={2}
            fill="url(#intensityGradFull)"
            dot={(props: { cx?: number; cy?: number; index?: number }) => {
              const idx = props.index ?? 0;
              const pt = data[idx];
              if (!pt || props.cx == null || props.cy == null) return <></>;
              return (
                <circle
                  key={idx}
                  cx={props.cx}
                  cy={props.cy}
                  r={3}
                  fill={PHASE_COLORS[pt.phase] ?? "#8b5cf6"}
                  stroke="none"
                />
              );
            }}
          />
          {/* Actual difficulty dots for completed arenas */}
          {completedPoints.map((pt, i) => (
            <ReferenceDot
              key={`actual-${i}`}
              x={pt.label}
              y={pt.actual ?? 0}
              r={4}
              fill={DIFFICULTY_COLORS[pt.actualDifficulty ?? "moderate"] ?? "#fbbf24"}
              stroke="#1f2937"
              strokeWidth={1}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
