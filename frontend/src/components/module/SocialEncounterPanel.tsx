import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare, Dice6, CheckCircle, XCircle, ChevronDown, ChevronUp,
  Award, AlertTriangle, BookOpen,
} from "lucide-react";
import { clsx } from "clsx";
import { Card, Button } from "@/components/ui";
import { TypewriterText } from "@/components/transitions/TypewriterText";
import type {
  SocialEncounterSetup,
  SkillCheckSetup,
  CheckResultInput,
  SocialEncounterResult,
} from "@/api/social";

interface SkillCheckCardProps {
  check: SkillCheckSetup;
  index: number;
  result?: { roll: number; modifier: number };
  outcome?: { success: boolean; total: number; result_text: string };
  resolved: boolean;
  onUpdateResult: (index: number, field: "roll" | "modifier", value: number) => void;
}

function SkillCheckCard({ check, index, result, outcome, resolved, onUpdateResult }: SkillCheckCardProps) {
  const [expanded, setExpanded] = useState(!resolved);
  const roll = result?.roll ?? 0;
  const modifier = result?.modifier ?? 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.15, duration: 0.4 }}
    >
      <Card
        padding="md"
        className={clsx(
          "transition-all",
          resolved && outcome?.success && "border-emerald-500/30",
          resolved && outcome && !outcome.success && "border-red-500/30",
        )}
      >
        <button
          className="w-full flex items-center justify-between"
          onClick={() => setExpanded(!expanded)}
        >
          <div className="flex items-center gap-3">
            <div
              className={clsx(
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold",
                resolved && outcome?.success && "bg-emerald-500/20 text-emerald-400",
                resolved && outcome && !outcome.success && "bg-red-500/20 text-red-400",
                !resolved && "bg-accent/20 text-accent",
              )}
            >
              {resolved && outcome ? (
                outcome.success ? <CheckCircle size={16} /> : <XCircle size={16} />
              ) : (
                index + 1
              )}
            </div>
            <div className="text-left">
              <span className="text-sm font-display font-semibold text-white capitalize">
                {check.skill.replace(/_/g, " ")}
              </span>
              <span className="text-xs text-gray-500 ml-2">DC {check.dc}</span>
            </div>
          </div>
          {expanded ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
        </button>

        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-3 pt-3 border-t border-surface-3 space-y-3">
                {!resolved ? (
                  <div className="flex items-center gap-3">
                    <div className="flex-1">
                      <label htmlFor={`roll-${index}`} className="text-xs text-gray-500 block mb-1">d20 Roll</label>
                      <input
                        id={`roll-${index}`}
                        type="number"
                        min={1}
                        max={20}
                        value={roll || ""}
                        onChange={(e) => onUpdateResult(index, "roll", parseInt(e.target.value) || 0)}
                        className="w-full bg-surface-2 border border-surface-3 rounded-lg px-3 py-2 text-sm text-white focus:border-accent/50 focus:outline-none"
                        placeholder="1-20"
                      />
                    </div>
                    <div className="flex-1">
                      <label htmlFor={`mod-${index}`} className="text-xs text-gray-500 block mb-1">Modifier</label>
                      <input
                        id={`mod-${index}`}
                        type="number"
                        min={-10}
                        max={20}
                        value={modifier || ""}
                        onChange={(e) => onUpdateResult(index, "modifier", parseInt(e.target.value) || 0)}
                        className="w-full bg-surface-2 border border-surface-3 rounded-lg px-3 py-2 text-sm text-white focus:border-accent/50 focus:outline-none"
                        placeholder="+0"
                      />
                    </div>
                    <div className="pt-5">
                      <span className="text-sm font-mono text-accent">
                        = {roll + modifier}
                      </span>
                    </div>
                  </div>
                ) : outcome ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-gray-400">Roll: {outcome.total}</span>
                      <span className="text-gray-600">vs</span>
                      <span className="text-gray-400">DC {check.dc}</span>
                      <span className={clsx(
                        "font-semibold",
                        outcome.success ? "text-emerald-400" : "text-red-400",
                      )}>
                        {outcome.success ? "Success" : "Failure"}
                      </span>
                    </div>
                    <p className={clsx(
                      "text-sm italic leading-relaxed",
                      outcome.success ? "text-emerald-300/80" : "text-red-300/80",
                    )}>
                      {outcome.result_text}
                    </p>
                  </div>
                ) : null}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
}

interface SocialEncounterPanelProps {
  setup: SocialEncounterSetup;
  onResolve: (results: CheckResultInput[]) => Promise<SocialEncounterResult>;
  onComplete: () => void;
}

export function SocialEncounterPanel({ setup, onResolve, onComplete }: SocialEncounterPanelProps) {
  const [results, setResults] = useState<{ roll: number; modifier: number }[]>(
    setup.skill_checks.map(() => ({ roll: 0, modifier: 0 })),
  );
  const [resolution, setResolution] = useState<SocialEncounterResult | null>(null);
  const [resolving, setResolving] = useState(false);
  const [showDmPrompt, setShowDmPrompt] = useState(false);

  const handleUpdateResult = useCallback((index: number, field: "roll" | "modifier", value: number) => {
    setResults((prev) => {
      const next = [...prev];
      next[index] = { ...next[index]!, [field]: value };
      return next;
    });
  }, []);

  const allFilled = results.every((r) => r.roll > 0);

  const handleResolve = async () => {
    setResolving(true);
    try {
      const checkResults: CheckResultInput[] = results.map((r, i) => ({
        skill: setup.skill_checks[i]!.skill,
        roll: r.roll,
        modifier: r.modifier,
      }));
      const result = await onResolve(checkResults);
      setResolution(result);
    } finally {
      setResolving(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card padding="lg" className="border-purple-500/20 text-center">
          <div className="flex justify-center mb-3">
            <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center">
              <MessageSquare size={24} className="text-purple-400" />
            </div>
          </div>
          <h2 className="text-2xl font-display font-bold text-purple-300 mb-2">
            {setup.name}
          </h2>
          <p className="text-sm text-gray-400 leading-relaxed max-w-md mx-auto">
            {setup.description}
          </p>
        </Card>
      </motion.div>

      {/* DM Prompt (collapsible) */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card padding="md" className="border-amber-500/20">
          <button
            className="w-full flex items-center gap-2 text-left"
            onClick={() => setShowDmPrompt(!showDmPrompt)}
          >
            <BookOpen size={16} className="text-amber-400 flex-shrink-0" />
            <span className="text-sm font-display font-semibold text-amber-300 flex-1">
              DM Instructions
            </span>
            {showDmPrompt ? <ChevronUp size={14} className="text-gray-500" /> : <ChevronDown size={14} className="text-gray-500" />}
          </button>
          <AnimatePresence>
            {showDmPrompt && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="mt-3 pt-3 border-t border-surface-3">
                  <TypewriterText text={setup.dm_prompt} speed={15} className="text-sm text-gray-300 leading-relaxed" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </motion.div>

      {/* Skill Checks */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs text-gray-500 uppercase tracking-wider font-medium">
          <Dice6 size={14} />
          <span>Skill Checks</span>
        </div>
        {setup.skill_checks.map((check, i) => (
          <SkillCheckCard
            key={check.skill}
            check={check}
            index={i}
            result={results[i]}
            outcome={resolution?.checks[i]}
            resolved={!!resolution}
            onUpdateResult={handleUpdateResult}
          />
        ))}
      </div>

      {/* Resolve / Results */}
      {!resolution ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex justify-center"
        >
          <Button
            variant="primary"
            size="lg"
            glow
            icon={<Dice6 size={18} />}
            onClick={handleResolve}
            loading={resolving}
            disabled={!allFilled}
          >
            Resolve Encounter
          </Button>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card
            padding="lg"
            className={clsx(
              "text-center",
              resolution.overall_success ? "border-emerald-500/30" : "border-red-500/30",
            )}
          >
            <div className="flex justify-center mb-3">
              {resolution.overall_success ? (
                <Award size={32} className="text-emerald-400" />
              ) : (
                <AlertTriangle size={32} className="text-red-400" />
              )}
            </div>
            <h3 className={clsx(
              "text-xl font-display font-bold mb-2",
              resolution.overall_success ? "text-emerald-300" : "text-red-300",
            )}>
              {resolution.overall_success ? "Success!" : "Failure"}
            </h3>
            <p className="text-sm text-gray-400 mb-4">
              {resolution.successes} of {resolution.total_checks} checks passed
            </p>

            {/* Rewards */}
            {resolution.overall_success && Object.keys(resolution.rewards).length > 0 && (
              <div className="bg-emerald-500/10 rounded-lg px-4 py-3 mb-4">
                <div className="text-xs text-emerald-400 uppercase font-medium mb-2">Rewards</div>
                <div className="flex flex-wrap justify-center gap-2">
                  {Object.entries(resolution.rewards).map(([key, value]) => (
                    <span key={key} className="text-xs bg-emerald-500/20 text-emerald-300 px-2 py-1 rounded">
                      {key.replace(/_/g, " ")}: {String(value)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Consequences */}
            {!resolution.overall_success && Object.keys(resolution.consequences).length > 0 && (
              <div className="bg-red-500/10 rounded-lg px-4 py-3 mb-4">
                <div className="text-xs text-red-400 uppercase font-medium mb-2">Consequences</div>
                <div className="flex flex-wrap justify-center gap-2">
                  {Object.entries(resolution.consequences).map(([key, value]) => (
                    <span key={key} className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">
                      {key.replace(/_/g, " ")}: {String(value)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Lore fragment */}
            {resolution.lore_fragment_id && (
              <div className="text-xs text-purple-400 mt-2">
                Lore fragment discovered!
              </div>
            )}

            <Button
              variant="primary"
              size="lg"
              className="mt-4"
              onClick={onComplete}
            >
              Continue
            </Button>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
