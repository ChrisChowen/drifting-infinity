import { useEffect, useCallback } from "react";

interface HotkeyBinding {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  handler: () => void;
  description: string;
}

/**
 * Register keyboard shortcuts. Only fires when no input/textarea/select is focused.
 * Returns the bindings array for display in a cheat sheet.
 */
export function useHotkeys(bindings: HotkeyBinding[], enabled = true) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return;

      // Don't fire when typing in inputs
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.tagName === "SELECT") {
        // Exception: still allow Ctrl+Z in inputs
        if (!(e.ctrlKey && e.key === "z") && !(e.metaKey && e.key === "z")) {
          return;
        }
      }

      for (const binding of bindings) {
        const keyMatch = e.key.toLowerCase() === binding.key.toLowerCase();
        const ctrlMatch = binding.ctrl ? (e.ctrlKey || e.metaKey) : !(e.ctrlKey || e.metaKey);
        const shiftMatch = binding.shift ? e.shiftKey : !e.shiftKey;

        if (keyMatch && ctrlMatch && shiftMatch) {
          e.preventDefault();
          binding.handler();
          return;
        }
      }
    },
    [bindings, enabled],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return bindings;
}
