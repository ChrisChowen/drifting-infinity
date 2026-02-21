import { useToastStore, type ToastVariant } from "@/stores/useToastStore";
import { motion, AnimatePresence } from "framer-motion";
import { X, CheckCircle, AlertTriangle, AlertCircle, Info, Sparkles } from "lucide-react";
import { clsx } from "clsx";

const VARIANT_STYLES: Record<ToastVariant, { bg: string; border: string; icon: React.ReactNode }> = {
  success: {
    bg: "bg-emerald-950/90",
    border: "border-emerald-700/50",
    icon: <CheckCircle size={16} className="text-emerald-400 flex-shrink-0" />,
  },
  error: {
    bg: "bg-red-950/90",
    border: "border-red-700/50",
    icon: <AlertCircle size={16} className="text-red-400 flex-shrink-0" />,
  },
  warning: {
    bg: "bg-yellow-950/90",
    border: "border-yellow-700/50",
    icon: <AlertTriangle size={16} className="text-yellow-400 flex-shrink-0" />,
  },
  info: {
    bg: "bg-surface-2/90",
    border: "border-surface-3",
    icon: <Info size={16} className="text-blue-400 flex-shrink-0" />,
  },
  armillary: {
    bg: "bg-purple-950/90",
    border: "border-purple-700/50",
    icon: <Sparkles size={16} className="text-purple-400 flex-shrink-0" />,
  },
};

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none" role="status" aria-live="polite">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => {
          const style = VARIANT_STYLES[toast.variant];
          return (
            <motion.div
              key={toast.id}
              layout
              initial={{ opacity: 0, x: 80, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 80, scale: 0.95 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
              className={clsx(
                "pointer-events-auto flex items-start gap-2.5 px-4 py-3 rounded-lg border",
                "backdrop-blur-md shadow-lg max-w-sm text-sm text-gray-200",
                style.bg,
                style.border,
              )}
            >
              {style.icon}
              <span className="flex-1 leading-snug">{toast.message}</span>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-gray-500 hover:text-gray-300 transition-colors flex-shrink-0"
                aria-label="Dismiss notification"
              >
                <X size={14} />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
