import { useState, useCallback } from "react";

interface ConfirmOptions {
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "warning" | "default";
}

/**
 * Hook that replaces window.confirm with a themed modal.
 * Returns [modalProps, confirm] where confirm() returns a promise
 * that resolves true/false based on user choice.
 */
export function useConfirm() {
  const [state, setState] = useState<{
    open: boolean;
    options: ConfirmOptions;
    resolve: ((value: boolean) => void) | null;
  }>({
    open: false,
    options: { title: "", description: "" },
    resolve: null,
  });

  const confirm = useCallback((options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      setState({ open: true, options, resolve });
    });
  }, []);

  const handleConfirm = useCallback(() => {
    state.resolve?.(true);
    setState((s) => ({ ...s, open: false, resolve: null }));
  }, [state.resolve]);

  const handleCancel = useCallback(() => {
    state.resolve?.(false);
    setState((s) => ({ ...s, open: false, resolve: null }));
  }, [state.resolve]);

  return {
    modalProps: {
      open: state.open,
      title: state.options.title,
      description: state.options.description,
      confirmLabel: state.options.confirmLabel,
      cancelLabel: state.options.cancelLabel,
      variant: state.options.variant,
      onConfirm: handleConfirm,
      onCancel: handleCancel,
    },
    confirm,
  };
}
