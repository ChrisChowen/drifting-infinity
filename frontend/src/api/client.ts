import { useToastStore } from "@/stores/useToastStore";

const BASE_URL = "/api";

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: unknown
  ) {
    super(`API Error ${status}: ${statusText}`);
  }
}

function toastApiError(error: ApiError) {
  // Don't toast 422 validation errors — those are handled by forms
  if (error.status === 422) return;

  const messages: Record<number, string> = {
    400: "Invalid request",
    401: "Session expired — please refresh",
    403: "Access denied",
    404: "Resource not found",
    409: "Conflict — please retry",
    500: "Server error — please try again",
  };
  const message = messages[error.status] ?? `Request failed (${error.status})`;
  useToastStore.getState().addToast(message, "error");
}

async function request<T>(
  method: string,
  path: string,
  data?: unknown
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: data ? JSON.stringify(data) : undefined,
    });
  } catch (err) {
    // Network error — backend is unreachable
    const message = err instanceof TypeError ? "Cannot connect to server" : "Network error";
    useToastStore.getState().addToast(message, "error");
    throw new ApiError(0, message, null);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    if (response.status === 422 && body) {
      console.error("[API 422] Validation error:", JSON.stringify(body, null, 2));
    }
    const error = new ApiError(response.status, response.statusText, body);
    toastApiError(error);
    throw error;
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

/**
 * Retry a function up to `maxRetries` times with exponential backoff.
 * Useful for wrapping API calls that may transiently fail.
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 2,
  baseDelayMs = 500,
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (attempt < maxRetries) {
        await new Promise((r) => setTimeout(r, baseDelayMs * 2 ** attempt));
      }
    }
  }
  throw lastError;
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, data?: unknown) => request<T>("POST", path, data),
  put: <T>(path: string, data?: unknown) => request<T>("PUT", path, data),
  patch: <T>(path: string, data?: unknown) => request<T>("PATCH", path, data),
  delete: <T>(path: string) => request<T>("DELETE", path),
};
