import { describe, it, expect } from "vitest";
import { getEnvironmentTheme } from "../environmentThemes";

describe("getEnvironmentTheme", () => {
  it("returns default theme for null", () => {
    const theme = getEnvironmentTheme(null);
    expect(theme.label).toBe("The Nexus");
    expect(theme.particles).toBe("arcane_dust");
  });

  it("returns default theme for undefined", () => {
    const theme = getEnvironmentTheme(undefined);
    expect(theme.label).toBe("The Nexus");
  });

  it("returns default theme for unknown environment", () => {
    const theme = getEnvironmentTheme("nonexistent_biome_xyz");
    expect(theme.label).toBe("The Nexus");
  });

  it("returns arctic theme for arctic environment", () => {
    const theme = getEnvironmentTheme("arctic");
    expect(theme.label).toBe("Frozen Wastes");
    expect(theme.particles).toBe("frost_motes");
  });

  it("returns volcanic theme for lava_tubes", () => {
    const theme = getEnvironmentTheme("lava_tubes");
    expect(theme.label).toBe("Volcanic");
    expect(theme.particles).toBe("combat_embers");
  });

  it("returns feywild theme for feywild_glade", () => {
    const theme = getEnvironmentTheme("feywild_glade");
    expect(theme.label).toBe("Feywild");
    expect(theme.particles).toBe("fey_sparkle");
  });

  it("returns aquatic theme for coastal", () => {
    const theme = getEnvironmentTheme("coastal");
    expect(theme.label).toBe("Aquatic");
    expect(theme.particles).toBe("aquatic_bubbles");
  });

  it("returns planar theme for planar", () => {
    const theme = getEnvironmentTheme("planar");
    expect(theme.label).toBe("Planar Rift");
    expect(theme.particles).toBe("planar_rift");
  });

  it("returns an EnvironmentTheme with required fields", () => {
    const theme = getEnvironmentTheme("forest");
    expect(theme).toHaveProperty("gradient");
    expect(theme).toHaveProperty("particles");
    expect(theme).toHaveProperty("accent");
    expect(theme).toHaveProperty("label");
    expect(theme.gradient).toContain("radial-gradient");
    expect(theme.accent).toMatch(/^#[0-9A-Fa-f]{6}$/);
  });
});
