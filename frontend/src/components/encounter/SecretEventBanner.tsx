import { motion } from "framer-motion";
import {
  Sparkles, Key, Swords, ShoppingBag, Puzzle, Zap,
  ChevronDown, ChevronUp, BookOpen,
} from "lucide-react";
import { useState } from "react";
import { clsx } from "clsx";
import { Card } from "@/components/ui";
import type { SecretEvent } from "@/api/secretEvents";

const CONTENT_TYPE_CONFIG: Record<string, { icon: typeof Sparkles; color: string; label: string }> = {
  treasure: { icon: Key, color: "text-amber-400", label: "Treasure Room" },
  combat: { icon: Swords, color: "text-red-400", label: "Secret Battle" },
  shop: { icon: ShoppingBag, color: "text-emerald-400", label: "Hidden Shop" },
  puzzle: { icon: Puzzle, color: "text-blue-400", label: "Enigma" },
  mixed: { icon: Zap, color: "text-purple-400", label: "Anomaly" },
  special: { icon: Sparkles, color: "text-yellow-400", label: "Secret Event" },
};

interface SecretEventBannerProps {
  event: SecretEvent;
  onDismiss?: () => void;
}

export function SecretEventBanner({ event, onDismiss }: SecretEventBannerProps) {
  const [showInstructions, setShowInstructions] = useState(false);
  const config = CONTENT_TYPE_CONFIG[event.content_type] ?? CONTENT_TYPE_CONFIG["special"]!;
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <Card padding="lg" className="border-yellow-500/30 relative overflow-hidden">
        {/* Background shimmer */}
        <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/5 via-transparent to-purple-500/5 pointer-events-none" />

        <div className="relative">
          {/* Header */}
          <div className="flex items-center justify-center gap-3 mb-4">
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              <Sparkles size={20} className="text-yellow-400" />
            </motion.div>
            <span className="text-xs uppercase tracking-widest text-yellow-400 font-semibold">
              Secret Discovered
            </span>
            <motion.div
              animate={{ rotate: [0, -10, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              <Sparkles size={20} className="text-yellow-400" />
            </motion.div>
          </div>

          {/* Event name + icon */}
          <div className="text-center mb-4">
            <div className="flex justify-center mb-2">
              <div className={clsx(
                "w-14 h-14 rounded-full bg-surface-2 flex items-center justify-center",
              )}>
                <Icon size={28} className={config.color} />
              </div>
            </div>
            <h2 className="text-2xl font-display font-bold text-white mb-1">
              {event.name}
            </h2>
            <span className={clsx("text-xs font-semibold uppercase tracking-wider", config.color)}>
              {config.label}
            </span>
          </div>

          {/* Description */}
          <p className="text-sm text-gray-300 text-center leading-relaxed max-w-md mx-auto mb-4">
            {event.description}
          </p>

          {/* Rewards preview */}
          {Object.keys(event.rewards).length > 0 && (
            <div className="flex flex-wrap justify-center gap-2 mb-4">
              {Object.entries(event.rewards).map(([key, value]) => (
                <span
                  key={key}
                  className="text-xs bg-yellow-500/15 text-yellow-300 px-2.5 py-1 rounded-full border border-yellow-500/20"
                >
                  {key.replace(/_/g, " ")}: {String(value)}
                </span>
              ))}
            </div>
          )}

          {/* DM Instructions (collapsible) */}
          <div className="mt-3">
            <button
              className="w-full flex items-center justify-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
              onClick={() => setShowInstructions(!showInstructions)}
            >
              <BookOpen size={12} />
              <span>DM Instructions</span>
              {showInstructions ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            {showInstructions && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                className="mt-2"
              >
                <div className="bg-surface-2 rounded-lg p-3 text-sm text-gray-300 leading-relaxed">
                  {event.dm_instructions}
                </div>
              </motion.div>
            )}
          </div>

          {/* Lore fragment hint */}
          {event.lore_fragment_id && (
            <div className="mt-3 text-center text-xs text-purple-400">
              A lore fragment hides within...
            </div>
          )}

          {/* Dismiss */}
          {onDismiss && (
            <div className="flex justify-center mt-4">
              <button
                onClick={onDismiss}
                className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
              >
                Acknowledge
              </button>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
