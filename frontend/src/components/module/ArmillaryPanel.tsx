import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";
import { Card, Button } from "@/components/ui";
import { ArmillaryOrb } from "@/components/combat/ArmillaryOrb";
import { ArmillaryRollAnimation } from "@/components/combat/ArmillaryRollAnimation";

interface ArmillaryEffect {
  id: string;
  round_number: number;
  category: string;
  effect_key: string;
  effect_description: string;
  xp_cost: number;
  was_rerolled: boolean;
}

interface ArmillaryPanelProps {
  effects: ArmillaryEffect[];
  currentRound: number;
  onRoll: () => Promise<ArmillaryEffect | null>;
  onReroll: (effectId: string) => Promise<ArmillaryEffect | null>;
}

const CATEGORY_COLORS: Record<string, string> = {
  hostile: "text-red-400",
  beneficial: "text-emerald-400",
  neutral: "text-yellow-400",
  chaos: "text-purple-400",
};

export function ArmillaryPanel({ effects, currentRound, onRoll, onReroll }: ArmillaryPanelProps) {
  const [rolling, setRolling] = useState(false);
  const [animatingEffect, setAnimatingEffect] = useState<ArmillaryEffect | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleRoll = useCallback(async () => {
    setRolling(true);
    const effect = await onRoll();
    setRolling(false);
    if (effect) {
      setAnimatingEffect(effect);
    }
  }, [onRoll]);

  const handleReroll = useCallback(
    async (effectId: string) => {
      setRolling(true);
      const effect = await onReroll(effectId);
      setRolling(false);
      if (effect) {
        setAnimatingEffect(effect);
      }
    },
    [onReroll],
  );

  const latestEffect = effects.length > 0 ? effects[effects.length - 1] : null;
  const pastEffects = effects.slice(0, -1);

  return (
    <Card padding="md" className="border-purple-500/20">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <ArmillaryOrb size="sm" intensity={0.7} />
          <span className="text-sm font-display font-semibold text-purple-300">
            The Armillary
          </span>
        </div>
        <span className="text-[10px] text-gray-500">Round {currentRound}</span>
      </div>

      {/* Animation overlay */}
      <AnimatePresence>
        {animatingEffect && (
          <ArmillaryRollAnimation
            category={animatingEffect.category as "hostile" | "beneficial" | "neutral" | "chaos"}
            effectKey={animatingEffect.effect_key}
            effectDescription={animatingEffect.effect_description}
            onComplete={() => setAnimatingEffect(null)}
          />
        )}
      </AnimatePresence>

      {/* Latest effect display */}
      {latestEffect && !animatingEffect && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-3 p-2 rounded-lg bg-surface-2 border border-surface-3"
        >
          <div className="flex items-center justify-between mb-1">
            <span
              className={`text-xs font-semibold uppercase tracking-wider ${CATEGORY_COLORS[latestEffect.category] ?? "text-gray-400"}`}
            >
              {latestEffect.category}
            </span>
            <span className="text-[10px] text-gray-500">R{latestEffect.round_number}</span>
          </div>
          <div className="text-sm font-medium text-white mb-0.5">
            {latestEffect.effect_key.replace(/_/g, " ")}
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            {latestEffect.effect_description}
          </p>
          {!latestEffect.was_rerolled && (
            <button
              onClick={() => handleReroll(latestEffect.id)}
              disabled={rolling}
              className="mt-2 flex items-center gap-1 text-[10px] text-purple-400 hover:text-purple-300 transition-colors"
            >
              <RefreshCw size={10} />
              Reroll
            </button>
          )}
        </motion.div>
      )}

      {/* Roll button */}
      <Button
        variant="secondary"
        size="sm"
        icon={<Zap size={14} />}
        onClick={handleRoll}
        loading={rolling}
        className="w-full border-purple-500/30 hover:border-purple-500/50"
      >
        Roll Armillary Effect
      </Button>

      {/* History toggle */}
      {pastEffects.length > 0 && (
        <div className="mt-3">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-1 text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
          >
            {showHistory ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
            {pastEffects.length} previous effect{pastEffects.length > 1 ? "s" : ""}
          </button>
          <AnimatePresence>
            {showHistory && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="mt-2 space-y-1.5">
                  {pastEffects.map((e) => (
                    <div
                      key={e.id}
                      className="text-xs p-2 rounded bg-surface-2/50 border border-surface-3"
                    >
                      <span className={CATEGORY_COLORS[e.category] ?? "text-gray-400"}>
                        R{e.round_number}
                      </span>{" "}
                      <span className="text-gray-300">
                        {e.effect_key.replace(/_/g, " ")}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </Card>
  );
}
