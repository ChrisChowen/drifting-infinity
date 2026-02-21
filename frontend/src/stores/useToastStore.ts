import { create } from "zustand";

export type ToastVariant = "success" | "error" | "warning" | "info" | "armillary";

export interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
  duration: number;
}

interface ToastStoreState {
  toasts: Toast[];
  addToast: (message: string, variant?: ToastVariant, duration?: number) => void;
  removeToast: (id: string) => void;
}

let nextId = 0;

export const useToastStore = create<ToastStoreState>()((set) => ({
  toasts: [],

  addToast: (message, variant = "info", duration = 4000) => {
    const id = `toast-${++nextId}`;
    set((s) => ({
      toasts: [...s.toasts.slice(-4), { id, message, variant, duration }],
    }));
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, duration);
  },

  removeToast: (id) => {
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
  },
}));
