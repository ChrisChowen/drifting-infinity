import { api } from "./client";

export type LlmFeature =
  | "tactical_brief"
  | "armillary_voice"
  | "lore_fragment"
  | "post_arena_narration";

export interface LlmGenerateResponse {
  text: string;
  feature: string;
  is_mock: boolean;
}

export interface LlmStatusResponse {
  available: boolean;
  mock_mode: boolean;
}

export const llmApi = {
  status: () => api.get<LlmStatusResponse>("/llm/status"),

  generate: (feature: LlmFeature, context?: Record<string, unknown>) =>
    api.post<LlmGenerateResponse>("/llm/generate", { feature, context }),
};
