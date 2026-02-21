import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronUp, BookOpen } from "lucide-react";
import { Card, Badge } from "@/components/ui";
import { StatBlockPanel } from "@/components/StatBlockPanel";
import type { EncounterCreature } from "@/api/encounters";

const ROLE_COLORS: Record<string, "red" | "blue" | "gold" | "purple" | "emerald" | "gray"> = {
  brute: "red",
  soldier: "blue",
  artillery: "gold",
  controller: "purple",
  skirmisher: "emerald",
  lurker: "gray",
};

interface CreatureCombatCardProps {
  creature: EncounterCreature;
  flavor?: { personality: string; behavior: string; arena_reason: string };
  index: number;
}

export function CreatureCombatCard({ creature, flavor, index }: CreatureCombatCardProps) {
  const [expanded, setExpanded] = useState(false);
  const hasStatblock = creature.statblock && Object.keys(creature.statblock).length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Card padding="md">
        <button
          className="w-full text-left"
          onClick={() => hasStatblock && setExpanded(!expanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="font-display font-semibold text-white">
                {creature.count > 1 ? `${creature.count}× ` : ""}
                {creature.name}
              </span>
              <Badge color={ROLE_COLORS[creature.tactical_role] ?? "gray"}>
                {creature.tactical_role}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <div className="text-center">
                <div className="font-bold text-white">{creature.ac}</div>
                <div className="text-[10px] text-gray-500">AC</div>
              </div>
              <div className="text-center">
                <div className="font-bold text-hp-full">{creature.hp}</div>
                <div className="text-[10px] text-gray-500">HP</div>
              </div>
              <div className="text-center">
                <div className="font-bold text-gray-400">CR {creature.cr}</div>
                <div className="text-[10px] text-gray-500">{creature.xp_each} XP</div>
              </div>
              {hasStatblock && (
                <div className="text-gray-500 ml-1">
                  {expanded ? <ChevronUp size={16} /> : <BookOpen size={16} />}
                </div>
              )}
            </div>
          </div>
        </button>

        {/* Creature flavor text (always visible in combat reference) */}
        {flavor && (
          <div className="mt-2 text-xs text-gray-400 space-y-0.5">
            <p><span className="text-gray-500">Personality:</span> {flavor.personality}</p>
            <p><span className="text-gray-500">Behavior:</span> {flavor.behavior}</p>
          </div>
        )}

        <AnimatePresence>
          {expanded && hasStatblock && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-3 pt-3 border-t border-[var(--surface-3)]">
                <StatBlockPanel statblock={creature.statblock} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
}
