import { useState, useEffect, useCallback } from "react";
import { llmApi, type LlmFeature } from "@/api/llm";

interface UseLlmOptions {
  /** Auto-generate on mount */
  autoGenerate?: boolean;
  /** Context data for the prompt */
  context?: Record<string, unknown>;
}

interface UseLlmResult {
  text: string | null;
  isMock: boolean;
  loading: boolean;
  generate: () => Promise<void>;
  /** Whether any LLM features are available (real or mock) */
  available: boolean;
}

/**
 * Hook for consuming LLM-generated text.
 * Automatically falls back to mock responses when the LLM service
 * is not configured.
 */
export function useLlm(
  feature: LlmFeature,
  options: UseLlmOptions = {},
): UseLlmResult {
  const { autoGenerate = false, context } = options;
  const [text, setText] = useState<string | null>(null);
  const [isMock, setIsMock] = useState(true);
  const [loading, setLoading] = useState(false);
  const [available, setAvailable] = useState(true);

  useEffect(() => {
    llmApi.status().then((s) => setAvailable(s.available || s.mock_mode)).catch(() => {
      /* service unavailable */
    });
  }, []);

  const generate = useCallback(async () => {
    setLoading(true);
    try {
      const res = await llmApi.generate(feature, context);
      setText(res.text);
      setIsMock(res.is_mock);
    } catch {
      setText(null);
    } finally {
      setLoading(false);
    }
  }, [feature, context]);

  useEffect(() => {
    if (autoGenerate) {
      generate();
    }
  }, [autoGenerate, generate]);

  return { text, isMock, loading, generate, available };
}
