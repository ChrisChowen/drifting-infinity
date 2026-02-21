import { motion } from "framer-motion";
import { clsx } from "clsx";
import type { ArenaCreatureStatus } from "@/api/runs";

const STATUS_STYLES: Record<string, { bg: string; text: string; ring: string }> = {
  alive: { bg: "bg-emerald-900/20", text: "text-emerald-400", ring: "ring-emerald-500/30" },
  bloodied: { bg: "bg-orange-900/20", text: "text-orange-400", ring: "ring-orange-500/30" },
  defeated: { bg: "bg-red-900/20", text: "text-red-400 line-through opacity-60", ring: "ring-red-500/30" },
};

interface CreatureStatusPanelProps {
  creatures: ArenaCreatureStatus[];
  onStatusChange: (creatureId: string, status: "alive" | "bloodied" | "defeated") => void;
}

const STATUS_CYCLE: ("alive" | "bloodied" | "defeated")[] = ["alive", "bloodied", "defeated"];

export function CreatureStatusPanel({ creatures, onStatusChange }: CreatureStatusPanelProps) {
  const handleCycle = (creature: ArenaCreatureStatus) => {
    const currentIdx = STATUS_CYCLE.indexOf(creature.status);
    const nextStatus = STATUS_CYCLE[(currentIdx + 1) % STATUS_CYCLE.length]!;
    onStatusChange(creature.id, nextStatus);
  };

  return (
    <div className="space-y-1.5">
      <div className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-2">
        Creature Status
      </div>
      {creatures.map((c) => {
        const style = STATUS_STYLES[c.status] ?? STATUS_STYLES["alive"]!;
        return (
          <motion.button
            key={c.id}
            onClick={() => handleCycle(c)}
            className={clsx(
              "w-full flex items-center justify-between px-3 py-2 rounded-lg ring-1 transition-colors text-left",
              style.bg,
              style.ring,
            )}
            whileTap={{ scale: 0.98 }}
          >
            <span className={clsx("text-sm font-medium", style.text)}>
              {c.instance_label}
            </span>
            <span
              className={clsx(
                "text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded",
                style.text,
              )}
            >
              {c.status}
            </span>
          </motion.button>
        );
      })}
      <p className="text-[10px] text-gray-600 mt-1">Click to cycle: alive → bloodied → defeated</p>
    </div>
  );
}
