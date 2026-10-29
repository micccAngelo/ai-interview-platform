import { useEffect, useRef } from "react";

export function usePolling(
  fn: () => void | Promise<void>,
  intervalMs: number,
  active: boolean
) {
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    if (!active) return;
    let stopped = false;
    let id: ReturnType<typeof setTimeout>;
    const tick = async () => {
      try { await fnRef.current(); }
      catch { /* The polling owner presents request errors; keep the timer recoverable. */ }
      finally { if (!stopped) id = setTimeout(tick, intervalMs); }
    };
    id = setTimeout(tick, intervalMs);
    return () => { stopped = true; clearTimeout(id); };
  }, [intervalMs, active]);
}
