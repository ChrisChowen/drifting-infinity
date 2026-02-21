import { motion } from "framer-motion";
import { Lightbulb, AlertTriangle, Shield } from "lucide-react";
import { clsx } from "clsx";

const CATEGORY_CONFIG: Record<string, { icon: typeof Lightbulb; color: string; bg: string; border: string }> = {
  tactics: { icon: Lightbulb, color: "text-blue-400", bg: "bg-blue-900/10", border: "border-blue-500/20" },
  warning: { icon: AlertTriangle, color: "text-orange-400", bg: "bg-orange-900/10", border: "border-orange-500/20" },
  roguelike: { icon: Shield, color: "text-purple-400", bg: "bg-purple-900/10", border: "border-purple-500/20" },
};

const DEFAULT_CONFIG = { icon: Lightbulb, color: "text-gray-400", bg: "bg-surface-2", border: "border-surface-3" };

interface DmGuidanceBoxProps {
  title: string;
  content: string;
  category?: string;
  index?: number;
}

export function DmGuidanceBox({ title, content, category = "tactics", index = 0 }: DmGuidanceBoxProps) {
  const config = CATEGORY_CONFIG[category] ?? DEFAULT_CONFIG;
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className={clsx("rounded-lg border px-4 py-3", config.bg, config.border)}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <Icon size={14} className={config.color} />
        <span className={clsx("text-xs font-semibold uppercase tracking-wider", config.color)}>
          {title}
        </span>
      </div>
      <p className="text-sm text-gray-300 leading-relaxed">{content}</p>
    </motion.div>
  );
}
