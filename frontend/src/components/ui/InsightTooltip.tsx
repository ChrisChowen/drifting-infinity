import { useState } from "react";
import { Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";

interface InsightTooltipProps {
  question: string;
  answer: string;
  className?: string;
}

export function InsightTooltip({ question, answer, className }: InsightTooltipProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className={clsx("relative inline-block", className)}>
      <button
        className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors cursor-pointer"
        onClick={() => setOpen(!open)}
        aria-label={question}
      >
        <Info size={12} />
        <span>{question}</span>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            className="absolute z-50 mt-1 left-0 w-64 bg-surface-2 border border-surface-3 rounded-lg p-3 text-xs text-gray-300 leading-relaxed shadow-lg"
          >
            {answer}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
