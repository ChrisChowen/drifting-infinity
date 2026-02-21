import { useState, useRef, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  /** Position relative to trigger */
  position?: "top" | "bottom";
  /** Max width of tooltip */
  maxWidth?: number;
}

export function Tooltip({ content, children, position = "top", maxWidth = 280 }: TooltipProps) {
  const [show, setShow] = useState(false);
  const triggerRef = useRef<HTMLSpanElement>(null);

  return (
    <span
      ref={triggerRef}
      className="relative inline-flex"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      <AnimatePresence>
        {show && (
          <motion.div
            initial={{ opacity: 0, y: position === "top" ? 4 : -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="absolute z-[90] pointer-events-none"
            style={{
              [position === "top" ? "bottom" : "top"]: "calc(100% + 6px)",
              left: "50%",
              transform: "translateX(-50%)",
              maxWidth,
            }}
          >
            <div className="bg-surface-1 border border-surface-3 rounded-lg px-3 py-2 shadow-xl text-xs text-gray-300 leading-relaxed whitespace-normal">
              {content}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  );
}
