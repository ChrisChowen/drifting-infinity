import { motion } from "framer-motion";
import { Scroll } from "lucide-react";
import { Card } from "@/components/ui";

interface EncounterHookCardProps {
  hook: string;
}

export function EncounterHookCard({ hook }: EncounterHookCardProps) {
  if (!hook) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card padding="md" className="border-gray-700/40">
        <div className="flex items-start gap-3">
          <Scroll size={16} className="text-gray-500 mt-0.5 flex-shrink-0" />
          <div>
            <div className="text-[10px] text-gray-500 uppercase tracking-wider font-medium mb-1">
              Encounter Hook
            </div>
            <p className="text-sm text-gray-300 leading-relaxed italic">{hook}</p>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
