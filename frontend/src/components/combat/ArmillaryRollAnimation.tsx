import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

type Category = "hostile" | "neutral" | "beneficial" | "chaos";

const CATEGORY_COLORS: Record<Category, string> = {
  hostile: "#EF4444",
  beneficial: "#22C55E",
  neutral: "#EAB308",
  chaos: "#A855F7",
};

const CATEGORY_LABELS: Record<Category, string> = {
  hostile: "Hostile",
  beneficial: "Beneficial",
  neutral: "Neutral",
  chaos: "Chaos",
};

const CATEGORY_BG: Record<Category, string> = {
  hostile: "bg-red-900/30 border-red-700/50",
  beneficial: "bg-green-900/30 border-green-700/50",
  neutral: "bg-yellow-900/30 border-yellow-700/50",
  chaos: "bg-purple-900/30 border-purple-700/50",
};

interface ArmillaryRollAnimationProps {
  category: Category;
  effectKey: string;
  effectDescription: string;
  onComplete: () => void;
  isReroll?: boolean;
}

export function ArmillaryRollAnimation({
  category,
  effectKey,
  effectDescription,
  onComplete,
  isReroll = false,
}: ArmillaryRollAnimationProps) {
  const [phase, setPhase] = useState<"spinning" | "reveal-category" | "typewriter" | "done">("spinning");
  const [displayedText, setDisplayedText] = useState("");
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Phase timing
  useEffect(() => {
    const spinDuration = isReroll ? 600 : 1200;
    const categoryRevealDuration = 600;

    // Phase 1: Spinning
    timerRef.current = setTimeout(() => {
      setPhase("reveal-category");

      // Phase 2: Category revealed
      timerRef.current = setTimeout(() => {
        setPhase("typewriter");
      }, categoryRevealDuration);
    }, spinDuration);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isReroll]);

  // Phase 3: Typewriter effect
  useEffect(() => {
    if (phase !== "typewriter") return;

    let idx = 0;
    const interval = setInterval(() => {
      idx++;
      setDisplayedText(effectDescription.slice(0, idx));
      if (idx >= effectDescription.length) {
        clearInterval(interval);
        setTimeout(() => setPhase("done"), 500);
      }
    }, 30);

    return () => clearInterval(interval);
  }, [phase, effectDescription]);

  // Auto-complete
  useEffect(() => {
    if (phase === "done") {
      const t = setTimeout(onComplete, 800);
      return () => clearTimeout(t);
    }
  }, [phase, onComplete]);

  const color = CATEGORY_COLORS[category];

  return (
    <AnimatePresence>
      <motion.div
        className={`rounded-lg p-4 border ${CATEGORY_BG[category]} overflow-hidden relative`}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* Spinning rune phase */}
        {phase === "spinning" && (
          <div className="flex flex-col items-center justify-center py-4 gap-3">
            {/* Spinning concentric circles */}
            <div className="relative w-12 h-12">
              <motion.div
                className="absolute inset-0 rounded-full border-2"
                style={{ borderColor: `${color}66` }}
                animate={{ rotate: 360 }}
                transition={{ duration: 1, ease: "linear", repeat: Infinity }}
              />
              <motion.div
                className="absolute inset-2 rounded-full border"
                style={{ borderColor: `${color}44` }}
                animate={{ rotate: -360 }}
                transition={{ duration: 0.7, ease: "linear", repeat: Infinity }}
              />
              <motion.div
                className="absolute inset-[14px] rounded-full"
                style={{ backgroundColor: `${color}33` }}
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ duration: 0.6, repeat: Infinity }}
              />
            </div>
            <span className="text-xs text-gray-500 uppercase tracking-widest animate-pulse">
              The Armillary stirs...
            </span>
          </div>
        )}

        {/* Category reveal + typewriter */}
        {(phase === "reveal-category" || phase === "typewriter" || phase === "done") && (
          <div>
            <motion.div
              className="flex items-center justify-between mb-2"
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <span
                className="text-xs font-semibold uppercase tracking-wider"
                style={{ color }}
              >
                {CATEGORY_LABELS[category]}
              </span>
            </motion.div>

            <motion.div
              className="text-sm font-medium text-white mb-1"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.15, duration: 0.3 }}
            >
              {effectKey.replace(/_/g, " ")}
            </motion.div>

            {(phase === "typewriter" || phase === "done") && (
              <p className="text-xs text-gray-300 leading-relaxed">
                {displayedText}
                {phase === "typewriter" && (
                  <motion.span
                    className="inline-block w-0.5 h-3.5 ml-0.5 align-text-bottom"
                    style={{ backgroundColor: color }}
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                  />
                )}
              </p>
            )}
          </div>
        )}

        {/* Expanding ring pulse on complete */}
        {phase === "done" && (
          <motion.div
            className="absolute inset-0 rounded-lg pointer-events-none"
            initial={{ boxShadow: `inset 0 0 0 2px ${color}00` }}
            animate={{ boxShadow: [`inset 0 0 0 2px ${color}40`, `inset 0 0 0 2px ${color}00`] }}
            transition={{ duration: 0.8 }}
          />
        )}
      </motion.div>
    </AnimatePresence>
  );
}
