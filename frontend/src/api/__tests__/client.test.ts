import { describe, it, expect, vi, beforeEach } from "vitest";
import { api, ApiError, withRetry } from "../client";

describe("api client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("makes a GET request and returns JSON", async () => {
    const mockData = { id: "1", name: "Test" };
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockData), { status: 200 }),
    );

    const result = await api.get<typeof mockData>("/test");
    expect(result).toEqual(mockData);
    expect(fetch).toHaveBeenCalledWith(
      "/api/test",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("makes a POST request with body", async () => {
    const mockData = { id: "1" };
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify(mockData), { status: 200 }),
    );

    await api.post("/test", { name: "New" });
    expect(fetch).toHaveBeenCalledWith(
      "/api/test",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ name: "New" }),
      }),
    );
  });

  it("throws ApiError on non-ok response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Not found" }), { status: 404, statusText: "Not Found" }),
    );

    await expect(api.get("/missing")).rejects.toThrow(ApiError);
  });

  it("throws ApiError on network failure", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new TypeError("Failed to fetch"));

    await expect(api.get("/offline")).rejects.toThrow(ApiError);
  });

  it("returns undefined for 204 responses", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(null, { status: 204 }),
    );

    const result = await api.delete("/test/1");
    expect(result).toBeUndefined();
  });
});

describe("withRetry", () => {
  it("returns on first success", async () => {
    const fn = vi.fn().mockResolvedValue("ok");
    const result = await withRetry(fn, 2, 10);
    expect(result).toBe("ok");
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("retries on failure and returns on success", async () => {
    const fn = vi.fn()
      .mockRejectedValueOnce(new Error("fail"))
      .mockResolvedValueOnce("ok");

    const result = await withRetry(fn, 2, 10);
    expect(result).toBe("ok");
    expect(fn).toHaveBeenCalledTimes(2);
  });

  it("throws after exhausting retries", async () => {
    const fn = vi.fn()
      .mockRejectedValueOnce(new Error("always fail"))
      .mockRejectedValueOnce(new Error("always fail"));

    await expect(withRetry(fn, 1, 10)).rejects.toThrow("always fail");
    expect(fn).toHaveBeenCalledTimes(2); // initial + 1 retry
  });
});
