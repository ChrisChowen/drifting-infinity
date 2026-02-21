import { motion } from "framer-motion";

interface ArmillaryOrbProps {
  size?: "sm" | "md" | "lg";
  /** 0-1 intensity, used to scale glow brightness */
  intensity?: number;
}

const SIZES = {
  sm: { outer: 16, inner: 8, glow: 10 },
  md: { outer: 28, inner: 14, glow: 16 },
  lg: { outer: 44, inner: 22, glow: 24 },
};

export function ArmillaryOrb({ size = "md", intensity = 0.5 }: ArmillaryOrbProps) {
  const s = SIZES[size];
  const glowOpacity = 0.2 + intensity * 0.4;

  return (
    <div
      className="relative inline-flex items-center justify-center flex-shrink-0"
      style={{ width: s.outer, height: s.outer }}
    >
      {/* Outer ring */}
      <motion.div
        className="absolute inset-0 rounded-full border border-purple-500/30"
        animate={{ rotate: 360 }}
        transition={{ duration: 8, ease: "linear", repeat: Infinity }}
      />

      {/* Inner ring (counter-rotate) */}
      <motion.div
        className="absolute rounded-full border border-purple-400/20"
        style={{
          width: s.inner + 4,
          height: s.inner + 4,
        }}
        animate={{ rotate: -360 }}
        transition={{ duration: 5, ease: "linear", repeat: Infinity }}
      />

      {/* Core */}
      <motion.div
        className="rounded-full bg-purple-500"
        style={{
          width: s.inner,
          height: s.inner,
          boxShadow: `0 0 ${s.glow}px rgba(168, 85, 247, ${glowOpacity})`,
        }}
        animate={{
          scale: [1, 1.15, 1],
          boxShadow: [
            `0 0 ${s.glow}px rgba(168, 85, 247, ${glowOpacity})`,
            `0 0 ${s.glow * 1.5}px rgba(168, 85, 247, ${glowOpacity * 1.3})`,
            `0 0 ${s.glow}px rgba(168, 85, 247, ${glowOpacity})`,
          ],
        }}
        transition={{
          duration: 2.5,
          ease: "easeInOut",
          repeat: Infinity,
        }}
      />
    </div>
  );
}
