import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { prepApi, type PrepFloorResponse } from "@/api/prep";
import { Card, Button, PageHeader, LoadingState, Badge } from "@/components/ui";
import { Wand2, RefreshCw, ChevronRight, BookOpen } from "lucide-react";
import { motion } from "framer-motion";

const DANGER_COLORS: Record<string, "blue" | "gold" | "red" | "purple"> = {
  Challenging: "blue",
  Dangerous: "gold",
  Brutal: "red",
  Lethal: "purple",
};

export function FloorPrepPage() {
  const { floorNumber } = useParams<{ floorNumber: string }>();
  const navigate = useNavigate();
  const { floor, run } = useRunStore();

  const [floorData, setFloorData] = useState<PrepFloorResponse | null>(null);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);

  const floorId = floor?.id;

  // Load existing prep data
  useEffect(() => {
    if (!floorId) return;
    setLoading(true);
    prepApi
      .getFloor(floorId)
      .then(setFloorData)
      .catch(() => setFloorData(null))
      .finally(() => setLoading(false));
  }, [floorId]);

  const handleGenerate = async () => {
    if (!floorId) return;
    setGenerating(true);
    try {
      await prepApi.generateFloor(floorId);
      const data = await prepApi.getFloor(floorId);
      setFloorData(data);
    } finally {
      setGenerating(false);
    }
  };

  const hasArenas = floorData && floorData.arenas.length > 0;

  if (loading) {
    return <LoadingState message="Loading floor prep..." />;
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader
        title={`Floor ${floorNumber ?? floor?.floor_number ?? "?"} Prep`}
        subtitle={run ? `Run ${run.id.slice(-6)}` : undefined}
        backTo="/"
        backLabel="Dashboard"
      />

      {/* Generate button (if no arenas yet) */}
      {!hasArenas && (
        <Card padding="lg" className="text-center">
          <BookOpen size={32} className="mx-auto mb-3 text-gray-500" />
          <p className="text-gray-400 mb-4">
            Generate all encounters for this floor to review before your session.
          </p>
          <Button
            variant="primary"
            size="lg"
            glow
            icon={<Wand2 size={18} />}
            onClick={handleGenerate}
            loading={generating}
          >
            Generate Floor Encounters
          </Button>
        </Card>
      )}

      {/* Arena list */}
      {hasArenas && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
              {floorData.arenas.length} Arenas
            </h2>
            <Button
              variant="secondary"
              size="sm"
              icon={<RefreshCw size={14} />}
              onClick={handleGenerate}
              loading={generating}
            >
              Regenerate All
            </Button>
          </div>

          {floorData.arenas.map((entry, i) => {
            const arena = entry.arena;
            const narrative = arena.narrative_content;
            const creatureCount = entry.creatures.length;
            const dangerColor = DANGER_COLORS["Dangerous"];

            return (
              <motion.div
                key={arena.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Card
                  padding="md"
                  className="cursor-pointer hover:ring-1 hover:ring-accent/30 transition-all"
                  onClick={() => navigate(`/prep/floor/${floorNumber}/arena/${arena.arena_number}`)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-display font-semibold text-white">
                          Arena {arena.arena_number}
                        </span>
                        {arena.encounter_template && (
                          <span className="text-xs text-gray-500 capitalize">
                            {arena.encounter_template.replace(/_/g, " ")}
                          </span>
                        )}
                        <Badge color={dangerColor}>
                          {arena.environment ?? "unknown"}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-400 truncate">
                        {creatureCount} creature{creatureCount !== 1 ? "s" : ""}
                        {arena.xp_budget ? ` · ${arena.xp_budget} XP` : ""}
                      </p>
                      {narrative?.encounter_hook && (
                        <p className="text-xs text-gray-500 italic mt-1 truncate">
                          {narrative.encounter_hook}
                        </p>
                      )}
                    </div>
                    <ChevronRight size={16} className="text-gray-600 flex-shrink-0 ml-2" />
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Active affixes */}
      {floorData && floorData.active_affixes.length > 0 && (
        <Card padding="md" className="border-purple-500/20">
          <div className="text-xs text-purple-400 uppercase tracking-wider font-medium mb-2">
            Floor Affixes
          </div>
          <div className="flex flex-wrap gap-2">
            {floorData.active_affixes.map((affix, i) => (
              <span
                key={i}
                className="text-xs bg-purple-500/10 text-purple-300 px-2.5 py-1 rounded-lg border border-purple-500/30 capitalize"
              >
                {affix.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
