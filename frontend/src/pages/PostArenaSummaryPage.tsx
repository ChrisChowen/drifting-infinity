import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { campaignsApi, type CharacterResponse } from "@/api/campaigns";
import { snapshotsApi, type CharacterSnapshotPayload } from "@/api/snapshots";
import { Card, Badge, Button, PageHeader, ProgressBar } from "@/components/ui";
import { Coins, ArrowRight, SkipForward, Smile, Frown, Skull } from "lucide-react";
import { motion } from "framer-motion";
import { clsx } from "clsx";
import type { HealthSnapshot, CharacterSnapshot } from "@/types/run";

type DmAssessment = HealthSnapshot["dmAssessment"];
type HpCategory = CharacterSnapshot["hpCategory"];

const ASSESSMENT_OPTIONS: { value: DmAssessment; label: string; icon: typeof Smile; color: string }[] = [
  { value: "too_easy", label: "Too Easy", icon: Smile, color: "text-emerald-400 border-emerald-500/40 bg-emerald-900/20" },
  { value: "just_right", label: "Just Right", icon: Smile, color: "text-accent border-accent/40 bg-accent/10" },
  { value: "too_hard", label: "Too Hard", icon: Frown, color: "text-orange-400 border-orange-500/40 bg-orange-900/20" },
  { value: "near_tpk", label: "Near TPK", icon: Skull, color: "text-red-400 border-red-500/40 bg-red-900/20" },
];

const HP_CATEGORIES: { value: HpCategory; label: string; color: string }[] = [
  { value: "full", label: "Full", color: "bg-hp-full text-white" },
  { value: "above_half", label: "Above Half", color: "bg-hp-high text-white" },
  { value: "below_half", label: "Below Half", color: "bg-hp-mid text-white" },
  { value: "critical", label: "Critical", color: "bg-hp-critical text-white" },
  { value: "down", label: "Down", color: "bg-gray-600 text-white" },
];

const RESOURCE_LEVELS: { value: number; label: string }[] = [
  { value: 0.0, label: "Full" },
  { value: 0.25, label: "Most" },
  { value: 0.5, label: "Half" },
  { value: 0.75, label: "Few" },
  { value: 1.0, label: "Empty" },
];

export function PostArenaSummaryPage() {
  const navigate = useNavigate();
  const { arena, floor, run, completeFloor, setPhase } = useRunStore();
  const { characters } = useCampaignStore();

  const [step, setStep] = useState<"assess" | "party" | "results">("assess");
  const [assessment, setAssessment] = useState<DmAssessment | null>(null);
  const [finalStandChars, setFinalStandChars] = useState<Set<string>>(new Set());
  const [hpCategories, setHpCategories] = useState<Record<string, HpCategory>>({});
  const [resourceLevels, setResourceLevels] = useState<Record<string, number>>({});
  const [xpCharacters, setXpCharacters] = useState<CharacterResponse[]>([]);

  useEffect(() => {
    const campaignId = run?.campaign_id;
    if (campaignId) {
      campaignsApi.listCharacters(campaignId).then(setXpCharacters).catch(console.error);
    }
  }, [run?.campaign_id]);

  if (!arena || !floor) {
    return (
      <div className="py-8 text-center text-gray-400">No active arena data.</div>
    );
  }

  const allHpAssessed = characters.every((c) => hpCategories[c.id]);

  const handleSetHp = (charId: string, category: HpCategory) => {
    setHpCategories((prev) => ({ ...prev, [charId]: category }));
  };

  const handleAssess = (value: DmAssessment) => {
    setAssessment(value);
    // Auto-advance after a brief delay
    setTimeout(() => setStep("party"), 300);
  };

  const handlePartyDone = async () => {
    if (!floor || !assessment) return;

    // HP category → percentage mapping
    const HP_TO_PCT: Record<string, number> = {
      full: 1.0,
      above_half: 0.75,
      below_half: 0.35,
      critical: 0.15,
      down: 0.0,
    };

    const anyOnFinalStand = finalStandChars.size > 0;

    // Build per-character snapshot payloads
    const characterPayloads: CharacterSnapshotPayload[] = characters.map((c) => {
      const cat = hpCategories[c.id] || "full";
      return {
        character_id: c.id,
        name: c.name,
        hp_percentage: HP_TO_PCT[cat] ?? 1.0,
        is_on_final_stand: finalStandChars.has(c.id),
        is_dead: cat === "down",
        resources_depleted: resourceLevels[c.id] ?? 0.0,
      };
    });

    // Derive dm_assessment (health state) from DM perception + HP data
    const criticalCount = characterPayloads.filter((c) => c.hp_percentage <= 0.15 && !c.is_dead).length;
    const belowHalfCount = characterPayloads.filter((c) => c.hp_percentage < 0.5).length;
    let dmAssessment: string;
    if (assessment === "near_tpk" || criticalCount >= 2) {
      dmAssessment = "dire";
    } else if (assessment === "too_hard" || anyOnFinalStand) {
      dmAssessment = "critical";
    } else if (belowHalfCount > characterPayloads.length / 2) {
      dmAssessment = "strained";
    } else {
      dmAssessment = "healthy";
    }

    // POST snapshot to backend
    try {
      await snapshotsApi.submit(floor.id, {
        dm_assessment: dmAssessment,
        dm_combat_perception: assessment,
        any_on_final_stand: anyOnFinalStand,
        character_snapshots: characterPayloads,
      });
    } catch (err) {
      console.error("[PostArenaSummary] Failed to submit snapshot:", err);
    }

    setStep("results");
  };

  const handleContinueToRewards = () => {
    setPhase("reward");
    navigate("/run/rewards");
  };

  const handleSkipRewards = async () => {
    const arenasOnFloor = floor.arena_count;
    const completed = floor.arenas_completed + 1;
    if (completed >= arenasOnFloor) {
      await completeFloor();
      navigate("/run/floor-transition");
    } else {
      setPhase("encounter-brief");
      navigate("/run/encounter");
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader
        title="Arena Complete"
        subtitle={`Arena ${arena.arena_number}`}
      />

      {/* Step 1: How Did That Go? */}
      {step === "assess" && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h2 className="text-lg font-display font-semibold text-white text-center">
            How Did That Go?
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {ASSESSMENT_OPTIONS.map((opt) => {
              const Icon = opt.icon;
              const isSelected = assessment === opt.value;
              return (
                <button
                  key={opt.value}
                  className={clsx(
                    "rounded-xl border-2 p-5 text-center transition-all cursor-pointer",
                    isSelected ? opt.color : "border-surface-3 bg-surface-1 hover:border-gray-500"
                  )}
                  onClick={() => handleAssess(opt.value)}
                >
                  <Icon size={28} className={clsx("mx-auto mb-2", isSelected ? "" : "text-gray-500")} />
                  <div className={clsx(
                    "font-display font-semibold text-sm",
                    isSelected ? "" : "text-gray-300"
                  )}>
                    {opt.label}
                  </div>
                </button>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Step 2: Party Status */}
      {step === "party" && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h2 className="text-lg font-display font-semibold text-white text-center">
            Party Status
          </h2>
          <p className="text-xs text-gray-500 text-center">Tap the HP status for each character</p>

          <div className="space-y-3">
            {characters.map((char) => (
              <Card key={char.id} padding="sm">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">{char.name}</span>
                    <span className="text-xs text-gray-500 capitalize">{char.character_class}</span>
                  </div>
                  <div className="flex gap-1">
                    {HP_CATEGORIES.map((hp) => (
                      <button
                        key={hp.value}
                        className={clsx(
                          "flex-1 py-1.5 rounded text-xs font-medium transition-all cursor-pointer",
                          hpCategories[char.id] === hp.value
                            ? hp.color
                            : "bg-surface-2 text-gray-500 hover:text-gray-300"
                        )}
                        onClick={() => handleSetHp(char.id, hp.value)}
                      >
                        {hp.label}
                      </button>
                    ))}
                  </div>
                  {/* Resource depletion */}
                  <div className="pt-1">
                    <div className="text-xs text-gray-500 mb-1">Resources Used</div>
                    <div className="flex gap-1">
                      {RESOURCE_LEVELS.map((rl) => (
                        <button
                          key={rl.value}
                          className={clsx(
                            "flex-1 py-1 rounded text-xs font-medium transition-all cursor-pointer",
                            resourceLevels[char.id] === rl.value
                              ? "bg-purple-600 text-white"
                              : "bg-surface-2 text-gray-500 hover:text-gray-300"
                          )}
                          onClick={() => setResourceLevels((prev) => ({ ...prev, [char.id]: rl.value }))}
                        >
                          {rl.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Final Stand — per character */}
          <Card padding="sm" className="border-red-500/20">
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <Skull size={14} className="text-red-400" />
                <span className="text-xs font-medium text-red-300">Final Stand</span>
                <span className="text-[10px] text-gray-500 italic ml-auto">Revived once — next 0 HP = death</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {characters.map((char) => {
                  const isOnFinalStand = finalStandChars.has(char.id);
                  return (
                    <button
                      key={char.id}
                      className={clsx(
                        "px-3 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer",
                        isOnFinalStand
                          ? "bg-red-900/40 border-red-500/50 text-red-300"
                          : "bg-surface-2 border-surface-3 text-gray-500 hover:text-gray-300"
                      )}
                      onClick={() => {
                        setFinalStandChars((prev) => {
                          const next = new Set(prev);
                          if (next.has(char.id)) next.delete(char.id);
                          else next.add(char.id);
                          return next;
                        });
                      }}
                    >
                      {char.name}
                      {isOnFinalStand && " — FINAL STAND"}
                    </button>
                  );
                })}
              </div>
            </div>
          </Card>

          <Button
            variant="primary"
            size="lg"
            onClick={handlePartyDone}
            disabled={!allHpAssessed}
            className="w-full"
          >
            Continue
          </Button>
        </motion.div>
      )}

      {/* Step 3: Results */}
      {step === "results" && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-5"
        >
          {/* Gold earned */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Card glow padding="lg" className="text-center">
              <Coins size={28} className="mx-auto text-gold mb-2" />
              <div className="text-3xl font-bold text-gold font-display">
                {arena.gold_earned_per_player}
              </div>
              <div className="text-sm text-gray-400">gold per player</div>
              {characters.length > 1 && (
                <div className="text-xs text-gray-500 mt-1">
                  Party total: {arena.gold_earned_per_player * characters.length}
                </div>
              )}
            </Card>
          </motion.div>

          {/* XP progress */}
          {xpCharacters.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="space-y-2"
            >
              {xpCharacters.map((char) => {
                const canLevelUp = char.xp_total >= char.xp_to_next_level && char.level < 20;
                return (
                  <Card key={char.id} padding="sm">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-white">{char.name}</span>
                        <Badge color="gold">Lv {char.level}</Badge>
                      </div>
                      {canLevelUp && (
                        <Badge color="emerald">Level Up!</Badge>
                      )}
                    </div>
                    <ProgressBar
                      value={char.xp_total}
                      max={char.xp_to_next_level}
                      label={`XP: ${char.xp_total} / ${char.xp_to_next_level}`}
                      color="green"
                      size="sm"
                    />
                  </Card>
                );
              })}
            </motion.div>
          )}

          {/* Assessment recap */}
          <div className="text-center text-xs text-gray-500">
            Assessment: <span className="text-gray-400 capitalize">{assessment?.replace(/_/g, " ")}</span>
          </div>

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="flex gap-3"
          >
            <Button
              variant="primary"
              size="lg"
              icon={<ArrowRight size={18} />}
              onClick={handleContinueToRewards}
              className="flex-1"
            >
              Continue to Rewards
            </Button>
            <Button
              variant="secondary"
              size="lg"
              icon={<SkipForward size={16} />}
              onClick={handleSkipRewards}
            >
              Skip
            </Button>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
