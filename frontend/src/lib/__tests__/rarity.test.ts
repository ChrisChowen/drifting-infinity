import { describe, it, expect } from "vitest";
import { getRarityConfig } from "../rarity";

describe("getRarityConfig", () => {
  it("returns config for common rarity", () => {
    const config = getRarityConfig("common");
    expect(config.label).toBe("Common");
    expect(config.text).toContain("gray");
  });

  it("returns config for legendary rarity", () => {
    const config = getRarityConfig("legendary");
    expect(config.label).toBe("Legendary");
    expect(config.glow).toBeTruthy();
  });

  it("returns config for all valid rarities", () => {
    const rarities = ["common", "uncommon", "rare", "very_rare", "legendary"] as const;
    for (const rarity of rarities) {
      const config = getRarityConfig(rarity);
      expect(config.label).toBeTruthy();
      expect(config.text).toBeTruthy();
      expect(config.border).toBeTruthy();
    }
  });

  it("returns fallback for unknown rarity", () => {
    const config = getRarityConfig("mythic");
    expect(config.label).toBe("Common");
  });

  it("normalizes spaced rarity names", () => {
    const config = getRarityConfig("very rare");
    expect(config.label).toBe("Very Rare");
  });
});
