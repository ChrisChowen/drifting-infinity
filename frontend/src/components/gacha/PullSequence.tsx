import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getRarityConfig, type Rarity, RARITY_ORDER } from "@/lib/rarity";
import { Badge } from "@/components/ui";

interface PullResult {
  id: string;
  rarity: string;
  item_name?: string;
  item_description?: string;
  result_type: string;
  pull_number: number;
  was_pity: boolean;
  was_duplicate: boolean;
}

interface PullSequenceProps {
  results: PullResult[];
  onComplete: () => void;
}

/** Get the "best" pull from a list by rarity */
function getBestPull(results: PullResult[]): PullResult | null {
  let best: PullResult | null = null;
  let bestIdx = -1;
  for (const r of results) {
    const normalized = r.rarity.toLowerCase().replace(/\s+/g, "_") as Rarity;
    const idx = RARITY_ORDER.indexOf(normalized);
    if (idx > bestIdx) {
      bestIdx = idx;
      best = r;
    }
  }
  return best;
}

/** Duration each card is shown before flipping (ms). Higher rarity = longer pause. */
function getFlipDelay(rarity: string): number {
  const key = rarity.toLowerCase().replace(/\s+/g, "_");
  switch (key) {
    case "legendary": return 1200;
    case "very_rare": return 800;
    case "rare": return 500;
    default: return 250;
  }
}

export function PullSequence({ results, onComplete }: PullSequenceProps) {
  const [phase, setPhase] = useState<"charging" | "revealing" | "summary">("charging");
  const [revealIdx, setRevealIdx] = useState(-1);
  const [skipped, setSkipped] = useState(false);

  // Phase 1: Charging (1.5s)
  useEffect(() => {
    const t = setTimeout(() => setPhase("revealing"), 1500);
    return () => clearTimeout(t);
  }, []);

  // Phase 2: Sequential reveal
  useEffect(() => {
    if (phase !== "revealing") return;
    if (revealIdx >= results.length - 1) {
      // All revealed, go to summary
      const t = setTimeout(() => setPhase("summary"), 800);
      return () => clearTimeout(t);
    }

    const nextIdx = revealIdx + 1;
    const result = results[nextIdx];
    if (!result) return;
    const delay = getFlipDelay(result.rarity);
    const t = setTimeout(() => setRevealIdx(nextIdx), delay);
    return () => clearTimeout(t);
  }, [phase, revealIdx, results]);

  const handleSkip = useCallback(() => {
    setSkipped(true);
    setRevealIdx(results.length - 1);
    setPhase("summary");
  }, [results.length]);

  const bestPull = getBestPull(results);

  return (
    <div className="space-y-6">
      {/* Phase 1: Charging animation */}
      <AnimatePresence>
        {phase === "charging" && (
          <motion.div
            className="flex flex-col items-center justify-center py-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Spinning rune */}
            <div className="relative w-20 h-20 mb-6">
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-purple-500/40"
                animate={{ rotate: 360 }}
                transition={{ duration: 2, ease: "linear", repeat: Infinity }}
              />
              <motion.div
                className="absolute inset-3 rounded-full border border-purple-400/30"
                animate={{ rotate: -360 }}
                transition={{ duration: 1.5, ease: "linear", repeat: Infinity }}
              />
              <motion.div
                className="absolute inset-6 rounded-full bg-purple-500/20"
                animate={{ scale: [1, 1.4, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            </div>
            <span className="text-purple-400 font-display text-sm tracking-widest uppercase animate-pulse">
              The Armillary resonates...
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Phase 2: Card reveals */}
      {(phase === "revealing" || phase === "summary") && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {results.map((result, i) => {
              const isRevealed = skipped || i <= revealIdx;
              const config = getRarityConfig(result.rarity);

              return (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={isRevealed
                    ? { opacity: 1, scale: 1, rotateY: 0 }
                    : { opacity: 0.6, scale: 0.95, rotateY: 180 }
                  }
                  transition={{
                    duration: isRevealed ? 0.5 : 0.3,
                    ease: [0.22, 1, 0.36, 1],
                  }}
                  style={{ perspective: 800 }}
                >
                  <div
                    className={`rounded-xl border-2 p-4 text-center transition-all duration-500 ${
                      isRevealed
                        ? `bg-surface-1 ${config.border} ${config.glow}`
                        : "bg-surface-2 border-surface-3"
                    }`}
                  >
                    {isRevealed ? (
                      <>
                        <div className={`text-sm font-bold ${config.text}`}>
                          {result.item_name ?? result.result_type}
                        </div>
                        <div className={`text-xs mt-1 ${config.text}`}>
                          {config.label}
                        </div>
                        {result.item_description && (
                          <p className="text-xs text-gray-400 mt-2 line-clamp-2">
                            {result.item_description}
                          </p>
                        )}
                        <div className="flex items-center justify-center gap-1 mt-2">
                          {result.was_pity && <Badge color="gold">PITY</Badge>}
                          {result.was_duplicate && <Badge color="gray">DUP</Badge>}
                        </div>
                      </>
                    ) : (
                      <div className="py-4">
                        <div className="w-8 h-8 mx-auto rounded-full border border-purple-500/30 flex items-center justify-center">
                          <span className="text-purple-400 text-lg">?</span>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Skip button (only during reveal, and only for x10) */}
          {phase === "revealing" && results.length > 3 && revealIdx >= 2 && !skipped && (
            <motion.div
              className="flex justify-center mt-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <button
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-300 transition-colors underline underline-offset-2"
              >
                Reveal All
              </button>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* Phase 3: Best Pull Summary */}
      <AnimatePresence>
        {phase === "summary" && bestPull && (
          <motion.div
            className="flex justify-center"
            initial={{ opacity: 0, scale: 0.9, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          >
            {(() => {
              const config = getRarityConfig(bestPull.rarity);
              return (
                <div
                  className={`bg-surface-1 rounded-xl border-2 p-8 text-center max-w-sm w-full ${config.border} ${config.glow}`}
                >
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">
                    Best Pull
                  </div>
                  <div className={`text-2xl font-bold font-display ${config.text}`}>
                    {bestPull.item_name ?? bestPull.result_type}
                  </div>
                  <div className={`text-sm mt-1 ${config.text}`}>
                    {config.label}
                  </div>
                  {bestPull.item_description && (
                    <p className="text-gray-400 text-sm mt-4 leading-relaxed">
                      {bestPull.item_description}
                    </p>
                  )}
                  <button
                    onClick={onComplete}
                    className="mt-6 text-sm text-accent hover:text-accent-bright transition-colors underline underline-offset-2"
                  >
                    Continue
                  </button>
                </div>
              );
            })()}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
