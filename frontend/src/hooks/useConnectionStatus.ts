import { useState, useEffect, useCallback, useRef } from "react";

type ConnectionStatus = "connected" | "disconnected" | "checking";

const HEALTH_URL = "/api/health";
const CHECK_INTERVAL = 30_000; // 30 seconds
const RETRY_INTERVAL = 5_000; // 5 seconds when disconnected

export function useConnectionStatus() {
  const [status, setStatus] = useState<ConnectionStatus>("checking");
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const checkConnection = useCallback(async () => {
    try {
      const res = await fetch(HEALTH_URL, { method: "GET", signal: AbortSignal.timeout(5000) });
      setStatus(res.ok ? "connected" : "disconnected");
    } catch {
      setStatus("disconnected");
    }
  }, []);

  useEffect(() => {
    checkConnection();

    const scheduleCheck = () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = setInterval(() => {
        checkConnection();
      }, status === "disconnected" ? RETRY_INTERVAL : CHECK_INTERVAL);
    };

    scheduleCheck();
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [checkConnection, status]);

  return { status, retry: checkConnection };
}
