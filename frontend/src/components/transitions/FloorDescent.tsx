import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface FloorDescentProps {
  fromFloor: number;
  toFloor: number;
  /** Called when the descent animation finishes */
  onComplete: () => void;
}

/**
 * Full-screen descent animation — current floor number drops away
 * while the new floor number rises from below.
 */
export function FloorDescent({ fromFloor, toFloor, onComplete }: FloorDescentProps) {
  const [phase, setPhase] = useState<"hold" | "descend" | "arrive">("hold");

  useEffect(() => {
    // Brief hold, then descend, then arrive
    const t1 = setTimeout(() => setPhase("descend"), 600);
    const t2 = setTimeout(() => setPhase("arrive"), 1600);
    const t3 = setTimeout(onComplete, 2800);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [onComplete]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm pointer-events-none overflow-hidden">
      <AnimatePresence mode="wait">
        {(phase === "hold" || phase === "descend") && (
          <motion.div
            key="from"
            className="absolute text-center"
            initial={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 200, scale: 0.6 }}
            transition={{ duration: 0.8, ease: [0.55, 0, 1, 0.45] }}
          >
            <div className="text-xs text-gray-500 uppercase tracking-[0.3em] mb-2">
              Floor
            </div>
            <div className="text-8xl font-display font-bold text-white/40">
              {fromFloor}
            </div>
          </motion.div>
        )}

        {phase === "arrive" && (
          <motion.div
            key="to"
            className="absolute text-center"
            initial={{ opacity: 0, y: -200, scale: 0.6 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.8, ease: [0, 0.55, 0.45, 1] }}
          >
            <div className="text-xs text-accent uppercase tracking-[0.3em] mb-2">
              Descending to
            </div>
            <div className="text-8xl font-display font-bold text-accent">
              {toFloor}
            </div>
            <motion.div
              className="mt-4 text-sm text-gray-400 tracking-widest uppercase"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              The depths await...
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Falling particles / lines to sell the descent */}
      <div className="absolute inset-0 overflow-hidden">
        {Array.from({ length: 12 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-px bg-gradient-to-b from-transparent via-accent/20 to-transparent"
            style={{
              left: `${8 + (i * 7.5)}%`,
              height: "30%",
            }}
            animate={{
              y: ["-30%", "130%"],
            }}
            transition={{
              duration: 1.5 + (i % 3) * 0.3,
              repeat: Infinity,
              delay: i * 0.12,
              ease: "linear",
            }}
          />
        ))}
      </div>
    </div>
  );
}
