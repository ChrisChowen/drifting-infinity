import { motion } from "framer-motion";
import { clsx } from "clsx";

interface ArmillarySpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZES = {
  sm: "w-8 h-8",
  md: "w-12 h-12",
  lg: "w-20 h-20",
};

/**
 * Armillary-themed loading spinner with concentric rotating circles.
 */
export function ArmillarySpinner({ size = "md", className }: ArmillarySpinnerProps) {
  return (
    <div className={clsx("relative", SIZES[size], className)}>
      {/* Outer ring */}
      <motion.div
        className="absolute inset-0 rounded-full border-2 border-purple-500/40"
        animate={{ rotate: 360 }}
        transition={{ duration: 3, ease: "linear", repeat: Infinity }}
      />
      {/* Middle ring (counter-rotating) */}
      <motion.div
        className="absolute inset-[15%] rounded-full border border-accent/30"
        animate={{ rotate: -360 }}
        transition={{ duration: 2, ease: "linear", repeat: Infinity }}
      />
      {/* Core glow */}
      <motion.div
        className="absolute inset-[30%] rounded-full bg-purple-500/20"
        animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0.6, 0.3] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}
