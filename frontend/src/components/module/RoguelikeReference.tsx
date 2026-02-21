import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BookOpen, ChevronDown, ChevronUp } from "lucide-react";

interface RoguelikeReferenceProps {
  reference: Record<string, string>;
}

export function RoguelikeReference({ reference }: RoguelikeReferenceProps) {
  const [expanded, setExpanded] = useState(false);
  const entries = Object.entries(reference);

  if (entries.length === 0) return null;

  return (
    <div className="rounded-lg border border-surface-3 bg-surface-1">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-sm"
      >
        <div className="flex items-center gap-2 text-gray-400">
          <BookOpen size={14} />
          <span className="font-medium text-xs">Roguelike Rules Quick Reference</span>
        </div>
        {expanded ? (
          <ChevronUp size={14} className="text-gray-500" />
        ) : (
          <ChevronDown size={14} className="text-gray-500" />
        )}
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="border-t border-surface-3 px-3 py-3 space-y-3">
              {entries.map(([key, value]) => (
                <div key={key}>
                  <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                    {key.replace(/_/g, " ")}
                  </div>
                  <p className="text-xs text-gray-300 leading-relaxed whitespace-pre-line">
                    {value}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
