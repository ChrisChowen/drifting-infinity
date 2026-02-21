import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { prepApi, type PrepFloorResponse, type PrepArenaDetail } from "@/api/prep";
import { Card, Button, PageHeader, LoadingState, Badge, Select } from "@/components/ui";
import { RefreshCw, Save } from "lucide-react";
import { motion } from "framer-motion";
import { ReadAloudBlock } from "@/components/module/ReadAloudBlock";
import { DmGuidanceBox } from "@/components/module/DmGuidanceBox";
import { ENVIRONMENTS } from "@/constants/campaignSettings";

export function ArenaPrepPage() {
  const { floorNumber, arenaNumber } = useParams<{
    floorNumber: string;
    arenaNumber: string;
  }>();
  const { floor } = useRunStore();
  const floorId = floor?.id;

  const [floorData, setFloorData] = useState<PrepFloorResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [envOverride, setEnvOverride] = useState("");
  const [localNotes, setLocalNotes] = useState("");
  const [localReadAloud, setLocalReadAloud] = useState("");

  const arenaNum = arenaNumber ? parseInt(arenaNumber, 10) : 0;

  // Load floor data
  useEffect(() => {
    if (!floorId) return;
    setLoading(true);
    prepApi
      .getFloor(floorId)
      .then((data) => {
        setFloorData(data);
        const arena = data.arenas.find(
          (a) => a.arena.arena_number === arenaNum,
        );
        if (arena) {
          setLocalNotes(arena.arena.dm_notes ?? "");
          const narrative = (arena.arena.narrative_content ?? {}) as Record<
            string,
            unknown
          >;
          setLocalReadAloud(
            (arena.arena.custom_read_aloud as string) ??
              (narrative["read_aloud_text"] as string) ??
              "",
          );
        }
      })
      .finally(() => setLoading(false));
  }, [floorId, arenaNum]);

  const arenaDetail: PrepArenaDetail | undefined = floorData?.arenas.find(
    (a) => a.arena.arena_number === arenaNum,
  );

  const handleRegenerate = async () => {
    if (!floorId) return;
    setRegenerating(true);
    try {
      await prepApi.regenerateArena(
        floorId,
        arenaNum,
        envOverride ? { environment: envOverride } : undefined,
      );
      const data = await prepApi.getFloor(floorId);
      setFloorData(data);
      const arena = data.arenas.find((a) => a.arena.arena_number === arenaNum);
      if (arena) {
        const narrative = (arena.arena.narrative_content ?? {}) as Record<
          string,
          unknown
        >;
        setLocalReadAloud(
          (narrative["read_aloud_text"] as string) ?? "",
        );
      }
    } finally {
      setRegenerating(false);
    }
  };

  const handleSaveNotes = useCallback(async () => {
    if (!floorId || !arenaDetail) return;
    setSaving(true);
    try {
      await prepApi.updateNotes(floorId, arenaDetail.arena.id, {
        dm_notes: localNotes,
        custom_read_aloud: localReadAloud,
      });
    } finally {
      setSaving(false);
    }
  }, [floorId, arenaDetail, localNotes, localReadAloud]);

  if (loading) {
    return <LoadingState message="Loading arena prep..." />;
  }

  if (!arenaDetail) {
    return (
      <div className="text-center py-12 text-gray-500">
        Arena not found. Generate floor encounters first.
      </div>
    );
  }

  const arena = arenaDetail.arena;
  const narrative = arena.narrative_content;
  const guidanceBoxes = narrative?.dm_guidance_boxes ?? [];
  const creatureFlavor = narrative?.creature_flavor ?? [];
  const weaknessTips = narrative?.weakness_tips ?? [];
  const encounterHook = narrative?.encounter_hook ?? "";
  const readAloudText = narrative?.read_aloud_text ?? "";

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader
        title={`Arena ${arenaNum}`}
        subtitle={`Floor ${floorNumber} · ${(arena.encounter_template ?? "").replace(/_/g, " ")}`}
        backTo={`/prep/floor/${floorNumber}`}
        backLabel="Floor Overview"
      />

      {/* Read-aloud text */}
      <ReadAloudBlock
        text={localReadAloud || readAloudText}
        editable
        onEdit={(text) => setLocalReadAloud(text)}
      />

      {/* Encounter hook */}
      {encounterHook && (
        <Card padding="md" className="border-gray-700/40">
          <div className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
            Encounter Hook
          </div>
          <p className="text-sm text-gray-300 leading-relaxed italic">
            {encounterHook}
          </p>
        </Card>
      )}

      {/* Creatures */}
      <div className="space-y-2">
        <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium">
          Creatures ({arenaDetail.creatures.length})
        </h3>
        {arenaDetail.creatures.map((c) => {
          const flavor = creatureFlavor.find((f) => f.monster_id === c.monster_id);
          return (
            <motion.div
              key={c.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-white">
                    {c.instance_label}
                  </span>
                  <Badge color="gray">{c.status}</Badge>
                </div>
                {flavor && (
                  <div className="mt-1 text-xs text-gray-400">
                    <span className="text-gray-500">Personality:</span>{" "}
                    {flavor.personality}
                  </div>
                )}
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* DM Guidance */}
      {guidanceBoxes.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium">
            DM Guidance
          </h3>
          {guidanceBoxes.map((box, i) => (
            <DmGuidanceBox
              key={i}
              title={box.title}
              content={box.content}
              category={box.category}
              index={i}
            />
          ))}
        </div>
      )}

      {/* Weakness tips */}
      {weaknessTips.length > 0 && (
        <Card padding="md" className="border-emerald-500/20">
          <div className="text-xs text-emerald-400 uppercase tracking-wider font-medium mb-2">
            Weakness Opportunities
          </div>
          <ul className="space-y-1">
            {weaknessTips.map((tip, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-emerald-400 mt-0.5">•</span>
                {tip}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* DM Notes */}
      <Card padding="md">
        <div className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-2">
          DM Notes
        </div>
        <textarea
          value={localNotes}
          onChange={(e) => setLocalNotes(e.target.value)}
          placeholder="Add your notes for this encounter..."
          className="w-full bg-surface-2 text-sm text-gray-300 p-3 rounded-lg resize-none h-24 focus:outline-none focus:ring-1 focus:ring-accent/40 placeholder-gray-600"
        />
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          variant="secondary"
          icon={<Save size={16} />}
          onClick={handleSaveNotes}
          loading={saving}
        >
          Save Notes
        </Button>
        <Select
          label=""
          value={envOverride}
          onChange={(e) => setEnvOverride(e.target.value)}
        >
          <option value="">Auto environment</option>
          {ENVIRONMENTS.map((env) => (
            <option key={env.key} value={env.key}>
              {env.label}
            </option>
          ))}
        </Select>
        <Button
          variant="secondary"
          icon={<RefreshCw size={16} />}
          onClick={handleRegenerate}
          loading={regenerating}
        >
          Regenerate
        </Button>
      </div>
    </div>
  );
}
