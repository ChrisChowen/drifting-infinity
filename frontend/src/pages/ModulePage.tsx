import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { useArenaStore } from "@/stores/useArenaStore";
import {
  Card, Button, PageHeader, LoadingState, Select, InsightTooltip,
} from "@/components/ui";
import {
  Swords, RefreshCw, MapPin, Eye, ChevronDown, ChevronUp,
  Target, Shield, CheckCircle, Flag,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import { ENVIRONMENTS } from "@/constants/campaignSettings";
import { getEnvironmentTheme } from "@/lib/environmentThemes";
import { ReadAloudBlock } from "@/components/module/ReadAloudBlock";
import { CreatureCombatCard } from "@/components/module/CreatureCombatCard";
import { CreatureStatusPanel } from "@/components/module/CreatureStatusPanel";
import { DmGuidanceBox } from "@/components/module/DmGuidanceBox";
import { EncounterHookCard } from "@/components/module/EncounterHookCard";
import { ArmillaryPanel } from "@/components/module/ArmillaryPanel";
import { RoguelikeReference } from "@/components/module/RoguelikeReference";
import { DmNotes } from "@/components/combat/DmNotes";
import { SocialEncounterPanel } from "@/components/module/SocialEncounterPanel";
import { socialApi, type SocialEncounterSetup, type CheckResultInput } from "@/api/social";

const DANGER_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  Challenging: { bg: "bg-blue-900/30", text: "text-blue-300", border: "border-blue-500/40" },
  Dangerous: { bg: "bg-yellow-900/30", text: "text-yellow-300", border: "border-yellow-500/40" },
  Brutal: { bg: "bg-orange-900/30", text: "text-orange-300", border: "border-orange-500/40" },
  Lethal: { bg: "bg-red-900/30", text: "text-red-300", border: "border-red-500/40" },
};

function creatureSummary(creatures: { name: string; count: number }[]): string {
  const parts = creatures.map((c) =>
    c.count > 1 ? `${c.count} ${c.name}s` : `a ${c.name}`,
  );
  if (parts.length === 0) return "an empty arena";
  if (parts.length === 1) return parts[0]!;
  if (parts.length === 2) return `${parts[0]} and ${parts[1]}`;
  return `${parts.slice(0, -1).join(", ")}, and ${parts[parts.length - 1]}`;
}

export function ModulePage() {
  const navigate = useNavigate();
  const {
    encounter, arena, floor, phase,
    generateEncounter, approveEncounter, completeArena, loading,
  } = useRunStore();
  const {
    creatures, armillaryEffects, armillaryRound,
    loadCreatures, updateCreatureStatus,
    loadArmillaryEffects, rollArmillaryEffect, rerollArmillaryEffect,
    reset: resetArenaStore,
  } = useArenaStore();

  const [envOverride, setEnvOverride] = useState("");
  const [showDmNotes, setShowDmNotes] = useState(false);
  const [approving, setApproving] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [ending, setEnding] = useState(false);

  // Social encounter state
  const [socialSetup, setSocialSetup] = useState<SocialEncounterSetup | null>(null);
  const [socialChecked, setSocialChecked] = useState(false);

  const isActive = phase === "encounter-active";
  const isBrief = phase === "encounter-brief";
  const isSocial = !!socialSetup;

  // Check for social encounter first, then fall back to combat
  useEffect(() => {
    if (arena && isBrief && !socialChecked && !encounter) {
      setSocialChecked(true);
      socialApi.generate(arena.id).then((setup) => {
        if (setup) {
          setSocialSetup(setup);
        } else {
          generateEncounter();
        }
      }).catch(() => {
        generateEncounter();
      });
    }
  }, [arena, isBrief, socialChecked, encounter, generateEncounter]);

  // Trigger reveal animation
  useEffect(() => {
    if (encounter) {
      setRevealed(false);
      const timer = setTimeout(() => setRevealed(true), 100);
      return () => clearTimeout(timer);
    }
  }, [encounter]);

  // Load creatures when entering active phase
  useEffect(() => {
    if (isActive && arena && floor) {
      loadCreatures(floor.id, arena.id);
      loadArmillaryEffects(arena.id);
    }
  }, [isActive, arena, floor, loadCreatures, loadArmillaryEffects]);

  // Cleanup on unmount
  useEffect(() => resetArenaStore, [resetArenaStore]);

  const handleReroll = () => {
    setRevealed(false);
    generateEncounter(envOverride ? { environment: envOverride } : undefined);
  };

  const handleApprove = async () => {
    setApproving(true);
    try {
      await approveEncounter();
    } finally {
      setApproving(false);
    }
  };

  const handleEndEncounter = async () => {
    setEnding(true);
    try {
      await completeArena();
      navigate("/run/summary");
    } finally {
      setEnding(false);
    }
  };

  const handleSocialResolve = useCallback(async (checkResults: CheckResultInput[]) => {
    if (!arena) throw new Error("No arena");
    return socialApi.resolve(arena.id, checkResults);
  }, [arena]);

  const handleSocialComplete = useCallback(async () => {
    setEnding(true);
    try {
      await completeArena();
      navigate("/run/summary");
    } finally {
      setEnding(false);
    }
  }, [completeArena, navigate]);

  const handleCreatureStatusChange = useCallback(
    (creatureId: string, status: "alive" | "bloodied" | "defeated") => {
      if (floor && arena) {
        updateCreatureStatus(floor.id, arena.id, creatureId, status);
      }
    },
    [floor, arena, updateCreatureStatus],
  );

  const handleArmillaryRoll = useCallback(async () => {
    if (!arena) return null;
    return rollArmillaryEffect(arena.id);
  }, [arena, rollArmillaryEffect]);

  const handleArmillaryReroll = useCallback(
    async (effectId: string) => {
      if (!arena) return null;
      return rerollArmillaryEffect(arena.id, effectId);
    },
    [arena, rerollArmillaryEffect],
  );

  if (!arena) {
    return (
      <div className="py-8">
        <LoadingState message="Preparing the arena..." />
      </div>
    );
  }

  // Build creature flavor lookup from encounter data
  const flavorMap = new Map(
    (encounter?.creature_flavor ?? []).map((f) => [f.monster_id, f]),
  );

  return (
    <div className={clsx("max-w-4xl mx-auto", isActive ? "space-y-4" : "space-y-6")}>
      <PageHeader
        title={isSocial ? "Social Encounter" : isActive ? "Combat Reference" : "Encounter Brief"}
        subtitle={`Floor ${floor?.floor_number ?? "?"} — Arena ${arena.arena_number}`}
        backTo="/run/setup"
        backLabel="Run"
      />

      {loading && !encounter && !isSocial && (
        <LoadingState message="The Armillary conjures your encounter..." />
      )}

      {/* ═══════ SOCIAL ENCOUNTER ═══════ */}
      {isSocial && socialSetup && (
        <SocialEncounterPanel
          setup={socialSetup}
          onResolve={handleSocialResolve}
          onComplete={handleSocialComplete}
        />
      )}

      {/* ═══════ COMBAT ENCOUNTER ═══════ */}
      <AnimatePresence mode="wait">
        {encounter && !isSocial && (
          <motion.div
            key={`${encounter.template}-${isActive ? "active" : "brief"}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-5"
          >
            {/* ═══════ BRIEF PHASE: Read-aloud, environment, summary ═══════ */}
            {isBrief && (
              <>
                {/* Read-aloud text */}
                {encounter.read_aloud_text && (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={revealed ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6 }}
                  >
                    <ReadAloudBlock text={encounter.read_aloud_text} />
                  </motion.div>
                )}

                {/* Environment card */}
                {encounter.environment_name && (() => {
                  const envTheme = getEnvironmentTheme(encounter.environment);
                  return (
                    <motion.div
                      initial={{ opacity: 0, y: 16 }}
                      animate={revealed ? { opacity: 1, y: 0 } : {}}
                      transition={{ duration: 0.6, delay: 0.2 }}
                    >
                      <Card padding="lg" className="text-center overflow-hidden relative">
                        <div
                          className="absolute inset-0 opacity-20 pointer-events-none"
                          style={{ background: envTheme.gradient }}
                        />
                        <MapPin
                          size={20}
                          className="mx-auto mb-2 relative"
                          style={{ color: envTheme.accent }}
                        />
                        <h2
                          className="text-2xl font-display font-bold relative"
                          style={{ color: envTheme.accent }}
                        >
                          {encounter.environment_name}
                        </h2>
                        {encounter.terrain_features.length > 0 && (
                          <div className="mt-3 flex flex-wrap justify-center gap-2 relative">
                            {encounter.terrain_features.map((f, i) => (
                              <span
                                key={i}
                                className="text-xs bg-surface-2 text-gray-400 px-2 py-1 rounded"
                              >
                                {f}
                              </span>
                            ))}
                          </div>
                        )}
                      </Card>
                    </motion.div>
                  );
                })()}

                {/* Encounter hook */}
                {encounter.encounter_hook && (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={revealed ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5, delay: 0.35 }}
                  >
                    <EncounterHookCard hook={encounter.encounter_hook} />
                  </motion.div>
                )}

                {/* Natural language summary with danger badge */}
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={revealed ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.5, delay: 0.5 }}
                >
                  <Card padding="lg" glow>
                    <p className="text-lg text-center font-display text-white leading-relaxed">
                      You face{" "}
                      <span className="text-accent font-semibold">
                        {creatureSummary(encounter.creatures)}
                      </span>
                    </p>
                    {encounter.danger_rating && (() => {
                      const style = DANGER_STYLES[encounter.danger_rating] ?? DANGER_STYLES["Dangerous"]!;
                      const isIntense = encounter.danger_rating === "Lethal" || encounter.danger_rating === "Brutal";
                      return (
                        <div className="flex justify-center mt-3">
                          <motion.span
                            className={clsx(
                              "text-xs font-semibold uppercase tracking-wider px-3 py-1 rounded-full border",
                              style.bg, style.text, style.border,
                            )}
                            animate={isIntense ? { scale: [1, 1.05, 1], opacity: [1, 0.8, 1] } : {}}
                            transition={isIntense ? { duration: 2, repeat: Infinity, ease: "easeInOut" } : {}}
                          >
                            {encounter.danger_rating}
                          </motion.span>
                        </div>
                      );
                    })()}
                    {encounter.tactical_brief && (
                      <p className="text-sm text-gray-400 text-center mt-3 italic">
                        {encounter.tactical_brief}
                      </p>
                    )}
                    <div className="flex justify-center gap-4 mt-3">
                      <InsightTooltip
                        question="Why this difficulty?"
                        answer={`XP budget: ${encounter.xp_budget} (adjusted ${encounter.adjusted_xp}). Template: ${encounter.template.replace(/_/g, " ")}. Tier: ${encounter.difficulty_tier}.`}
                      />
                    </div>
                  </Card>
                </motion.div>

                {/* Creature cards */}
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={revealed ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.5, delay: 0.65 }}
                  className="space-y-2"
                >
                  {encounter.creatures.map((c, i) => (
                    <CreatureCombatCard
                      key={i}
                      creature={c}
                      flavor={flavorMap.get(c.monster_id)}
                      index={i}
                    />
                  ))}
                </motion.div>

                {/* Objective card */}
                {encounter.objective_name && (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={revealed ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5, delay: 0.8 }}
                  >
                    <Card padding="lg" className="border-accent/30">
                      <div className="flex items-center gap-2 mb-3">
                        <Target size={18} className="text-accent" />
                        <h3 className="font-display font-semibold text-accent text-lg">
                          {encounter.objective_name}
                        </h3>
                      </div>
                      <p className="text-gray-300 text-sm leading-relaxed italic mb-4">
                        {encounter.objective_description}
                      </p>
                      {encounter.objective_win_conditions.length > 0 && (
                        <div className="mb-3">
                          <div className="text-xs text-gray-500 uppercase font-medium mb-1">
                            Win Conditions
                          </div>
                          <ul className="space-y-1">
                            {encounter.objective_win_conditions.map((cond, i) => (
                              <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                                <CheckCircle size={14} className="text-emerald-400 flex-shrink-0" />
                                {cond}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {encounter.objective_special_rules.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {encounter.objective_special_rules.map((rule, i) => (
                            <span
                              key={i}
                              className="text-xs bg-surface-2 text-gray-400 px-2 py-1 rounded border border-surface-3"
                            >
                              {rule}
                            </span>
                          ))}
                        </div>
                      )}
                      {encounter.objective_dm_instructions && (
                        <details className="mt-3 text-sm">
                          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-300 transition-colors flex items-center gap-1">
                            <Eye size={12} />
                            DM Instructions
                          </summary>
                          <p className="text-gray-400 mt-2 text-sm leading-relaxed bg-surface-2 p-3 rounded-lg">
                            {encounter.objective_dm_instructions}
                          </p>
                        </details>
                      )}
                    </Card>
                  </motion.div>
                )}

                {/* Floor affixes */}
                {encounter.affix_details && encounter.affix_details.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={revealed ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.5, delay: 0.85 }}
                  >
                    <Card padding="md" className="border-purple-500/20">
                      <div className="flex items-center gap-2 mb-3">
                        <Shield size={16} className="text-purple-400" />
                        <span className="text-sm font-medium text-purple-300">
                          Active Floor Affixes
                        </span>
                      </div>
                      <div className="space-y-2">
                        {encounter.affix_details.map((affix, i) => (
                          <div
                            key={i}
                            className="bg-purple-500/10 rounded-lg px-3 py-2 border border-purple-500/20"
                          >
                            <div className="flex items-center gap-2 mb-0.5">
                              <span className="text-sm font-display font-semibold text-purple-300">
                                {affix.name}
                              </span>
                              <span className="text-[10px] text-purple-400/60 capitalize">
                                {affix.category.replace(/_/g, " ")}
                              </span>
                            </div>
                            <p className="text-xs text-gray-400 leading-relaxed">
                              {affix.description}
                            </p>
                          </div>
                        ))}
                      </div>
                    </Card>
                  </motion.div>
                )}

                {/* Warnings */}
                {encounter.warnings.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={revealed ? { opacity: 1 } : {}}
                    transition={{ delay: 0.9 }}
                    className="space-y-1"
                  >
                    {encounter.warnings.map((w, i) => (
                      <div
                        key={i}
                        className={clsx(
                          "text-sm px-4 py-2 rounded-lg border",
                          w.level === "reject"
                            ? "bg-red-900/20 text-red-300 border-red-700/30"
                            : "bg-yellow-900/20 text-yellow-300 border-yellow-700/30",
                        )}
                      >
                        {w.message}
                      </div>
                    ))}
                  </motion.div>
                )}

                {/* DM Notes (collapsed) */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={revealed ? { opacity: 1 } : {}}
                  transition={{ delay: 0.95 }}
                >
                  <button
                    className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors w-full"
                    onClick={() => setShowDmNotes(!showDmNotes)}
                  >
                    <Eye size={14} />
                    <span>DM Notes</span>
                    {showDmNotes ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                  <AnimatePresence>
                    {showDmNotes && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <Card padding="sm" className="mt-2 space-y-3">
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>
                              Template:{" "}
                              <span className="text-gray-400 capitalize">
                                {encounter.template.replace(/_/g, " ")}
                              </span>
                            </span>
                            <span>
                              XP Budget: <span className="text-gray-400">{encounter.xp_budget}</span>
                            </span>
                            <span>
                              Adjusted: <span className="text-gray-400">{encounter.adjusted_xp}</span>
                            </span>
                          </div>
                          {encounter.map_suggestions.length > 0 && (
                            <div>
                              <div className="text-xs text-gray-500 mb-1">Map Suggestions</div>
                              <div className="flex flex-wrap gap-1">
                                {encounter.map_suggestions.map((s, i) => (
                                  <span
                                    key={i}
                                    className="text-xs bg-surface-2 text-gray-400 px-2 py-0.5 rounded"
                                  >
                                    {s}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          <Select
                            label="Override Environment"
                            description="Reroll with a specific environment"
                            value={envOverride}
                            onChange={(e) => setEnvOverride(e.target.value)}
                          >
                            <option value="">Auto-select</option>
                            {ENVIRONMENTS.map((env) => (
                              <option key={env.key} value={env.key}>
                                {env.label}
                              </option>
                            ))}
                          </Select>
                        </Card>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>

                {/* Actions */}
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={revealed ? { opacity: 1, y: 0 } : {}}
                  transition={{ delay: 1.0 }}
                  className="flex gap-3"
                >
                  <Button
                    variant="primary"
                    size="lg"
                    glow
                    icon={<Swords size={18} />}
                    onClick={handleApprove}
                    loading={approving}
                    className="flex-1"
                  >
                    Begin Encounter
                  </Button>
                  <Button
                    variant="secondary"
                    size="lg"
                    icon={<RefreshCw size={16} />}
                    onClick={handleReroll}
                    loading={loading}
                  >
                    Reroll
                  </Button>
                </motion.div>
              </>
            )}

            {/* ═══════ ACTIVE PHASE: Combat reference ═══════ */}
            {isActive && (
              <>
                {/* Two-column layout: main content + sidebar */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  {/* Main column (2/3) */}
                  <div className="lg:col-span-2 space-y-4">
                    {/* Creature combat cards with flavor */}
                    <div className="space-y-2">
                      <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium">
                        Creatures
                      </h3>
                      {encounter.creatures.map((c, i) => (
                        <CreatureCombatCard
                          key={i}
                          creature={c}
                          flavor={flavorMap.get(c.monster_id)}
                          index={i}
                        />
                      ))}
                    </div>

                    {/* Tactical brief */}
                    {encounter.tactical_brief && (
                      <Card padding="md">
                        <div className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-2">
                          Tactical Brief
                        </div>
                        <p className="text-sm text-gray-300 leading-relaxed">
                          {encounter.tactical_brief}
                        </p>
                      </Card>
                    )}

                    {/* DM Guidance boxes */}
                    {(encounter.dm_guidance_boxes?.length ?? 0) > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-xs text-gray-500 uppercase tracking-wider font-medium">
                          DM Guidance
                        </h3>
                        {encounter.dm_guidance_boxes.map((box, i) => (
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
                    {(encounter.weakness_tips?.length ?? 0) > 0 && (
                      <Card padding="md" className="border-emerald-500/20">
                        <div className="text-xs text-emerald-400 uppercase tracking-wider font-medium mb-2">
                          Weakness Exploit Opportunities
                        </div>
                        <ul className="space-y-1">
                          {encounter.weakness_tips.map((tip, i) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                              <span className="text-emerald-400 mt-0.5">•</span>
                              {tip}
                            </li>
                          ))}
                        </ul>
                      </Card>
                    )}

                    {/* Objective reminder (compact) */}
                    {encounter.objective_name && (
                      <Card padding="sm" className="border-accent/20">
                        <div className="flex items-center gap-2">
                          <Target size={14} className="text-accent" />
                          <span className="text-sm font-medium text-accent">
                            {encounter.objective_name}
                          </span>
                        </div>
                        {encounter.objective_win_conditions.length > 0 && (
                          <div className="mt-1.5 flex flex-wrap gap-1">
                            {encounter.objective_win_conditions.map((cond, i) => (
                              <span
                                key={i}
                                className="text-[10px] bg-accent/10 text-accent/80 px-2 py-0.5 rounded"
                              >
                                {cond}
                              </span>
                            ))}
                          </div>
                        )}
                      </Card>
                    )}

                    {/* Roguelike reference */}
                    {encounter.roguelike_reference && (
                      <RoguelikeReference reference={encounter.roguelike_reference} />
                    )}
                  </div>

                  {/* Sidebar (1/3) */}
                  <div className="space-y-4">
                    {/* Creature status toggles */}
                    <CreatureStatusPanel
                      creatures={creatures}
                      onStatusChange={handleCreatureStatusChange}
                    />

                    {/* Armillary panel */}
                    <ArmillaryPanel
                      effects={armillaryEffects}
                      currentRound={armillaryRound}
                      onRoll={handleArmillaryRoll}
                      onReroll={handleArmillaryReroll}
                    />

                    {/* DM Notes */}
                    <DmNotes arenaId={arena.id} />
                  </div>
                </div>

                {/* End Encounter button */}
                <div className="flex justify-center pt-4">
                  <Button
                    variant="primary"
                    size="lg"
                    icon={<Flag size={18} />}
                    onClick={handleEndEncounter}
                    loading={ending}
                  >
                    End Encounter
                  </Button>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
