import { describe, it, expect, beforeEach, vi } from "vitest";
import { useToastStore } from "../useToastStore";

describe("useToastStore", () => {
  beforeEach(() => {
    useToastStore.setState({ toasts: [] });
    vi.useFakeTimers();
  });

  it("starts with empty toasts", () => {
    expect(useToastStore.getState().toasts).toEqual([]);
  });

  it("adds a toast with default variant and duration", () => {
    useToastStore.getState().addToast("Hello");
    const toasts = useToastStore.getState().toasts;
    expect(toasts).toHaveLength(1);
    expect(toasts[0]!.message).toBe("Hello");
    expect(toasts[0]!.variant).toBe("info");
    expect(toasts[0]!.duration).toBe(4000);
  });

  it("adds a toast with custom variant", () => {
    useToastStore.getState().addToast("Error!", "error");
    expect(useToastStore.getState().toasts[0]!.variant).toBe("error");
  });

  it("removes a toast by id", () => {
    useToastStore.getState().addToast("Test");
    const id = useToastStore.getState().toasts[0]!.id;
    useToastStore.getState().removeToast(id);
    expect(useToastStore.getState().toasts).toHaveLength(0);
  });

  it("auto-removes toast after duration", () => {
    useToastStore.getState().addToast("Temporary", "info", 2000);
    expect(useToastStore.getState().toasts).toHaveLength(1);
    vi.advanceTimersByTime(2000);
    expect(useToastStore.getState().toasts).toHaveLength(0);
  });

  it("limits to 5 toasts max", () => {
    for (let i = 0; i < 7; i++) {
      useToastStore.getState().addToast(`Toast ${i}`);
    }
    expect(useToastStore.getState().toasts.length).toBeLessThanOrEqual(5);
  });
});
