import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, X } from "lucide-react";
import { Button } from "./Button";

interface ConfirmModalProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "warning" | "default";
  onConfirm: () => void;
  onCancel: () => void;
}

const VARIANT_STYLES = {
  danger: {
    icon: "text-red-400",
    border: "border-red-500/30",
    confirmVariant: "danger" as const,
  },
  warning: {
    icon: "text-amber-400",
    border: "border-amber-500/30",
    confirmVariant: "primary" as const,
  },
  default: {
    icon: "text-accent",
    border: "border-accent/30",
    confirmVariant: "primary" as const,
  },
};

export function ConfirmModal({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "default",
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  const styles = VARIANT_STYLES[variant];

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-[80] flex items-center justify-center bg-black/60 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={onCancel}
        >
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-modal-title"
            className={`bg-surface-1 border ${styles.border} rounded-xl p-6 shadow-2xl max-w-sm w-full mx-4`}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <AlertTriangle size={20} className={styles.icon} />
                <h2 id="confirm-modal-title" className="font-display text-lg text-white">{title}</h2>
              </div>
              <button
                onClick={onCancel}
                className="text-gray-500 hover:text-gray-300 transition-colors"
                aria-label="Close dialog"
              >
                <X size={18} />
              </button>
            </div>

            <p className="text-sm text-gray-400 mb-6 leading-relaxed">
              {description}
            </p>

            <div className="flex gap-3 justify-end">
              <Button variant="secondary" size="md" onClick={onCancel}>
                {cancelLabel}
              </Button>
              <Button variant={styles.confirmVariant} size="md" onClick={onConfirm}>
                {confirmLabel}
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
