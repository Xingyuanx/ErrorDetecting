type TelemetryLevel = "debug" | "info" | "warn" | "error";

type TelemetryEvent = {
  name: string;
  level: TelemetryLevel;
  ts: number;
  context?: Record<string, unknown>;
};

type TelemetryConfig = {
  enabled: boolean;
  endpoint: string;
  sampleRate: number;
  getContext?: () => Record<string, unknown>;
};

let config: TelemetryConfig = {
  enabled: false,
  endpoint: "",
  sampleRate: 1,
};

function clamp01(n: number) {
  if (Number.isNaN(n)) return 1;
  return Math.max(0, Math.min(1, n));
}

function safeString(v: unknown, maxLen = 400) {
  const s = typeof v === "string" ? v : JSON.stringify(v);
  return s.length > maxLen ? s.slice(0, maxLen) : s;
}

function normalizeError(e: unknown) {
  if (e instanceof Error) {
    return {
      name: e.name,
      message: safeString(e.message, 800),
      stack: safeString(e.stack || "", 2000),
    };
  }
  return { message: safeString(e, 800) };
}

function shouldSend() {
  if (!config.enabled) return false;
  const r = clamp01(config.sampleRate);
  if (r >= 1) return true;
  return Math.random() < r;
}

function mergeContext(extra?: Record<string, unknown>) {
  const base = config.getContext ? config.getContext() : {};
  return { ...base, ...(extra || {}) };
}

function postEvent(evt: TelemetryEvent) {
  if (!config.endpoint) return;
  const payload = JSON.stringify(evt);

  try {
    if (typeof navigator !== "undefined" && typeof navigator.sendBeacon === "function") {
      const blob = new Blob([payload], { type: "application/json" });
      navigator.sendBeacon(config.endpoint, blob);
      return;
    }
  } catch (e) {
    void e;
  }

  try {
    fetch(config.endpoint, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: payload,
      keepalive: true,
    }).catch(() => {});
  } catch (e) {
    void e;
  }
}

export function initTelemetry(next: Partial<TelemetryConfig>) {
  config = {
    ...config,
    ...next,
    enabled: !!next.enabled,
    sampleRate: clamp01(Number(next.sampleRate ?? config.sampleRate)),
    endpoint: String(next.endpoint ?? config.endpoint),
  };
}

export function trackEvent(name: string, context?: Record<string, unknown>, level: TelemetryLevel = "info") {
  if (!shouldSend()) return;
  postEvent({ name, level, ts: Date.now(), context: mergeContext(context) });
}

export function trackError(name: string, error: unknown, context?: Record<string, unknown>) {
  postEvent({
    name,
    level: "error",
    ts: Date.now(),
    context: mergeContext({ error: normalizeError(error), ...(context || {}) }),
  });
}

export function installGlobalErrorHandlers() {
  window.addEventListener("error", (ev) => {
    trackError("window_error", ev.error || ev.message, {
      filename: ev.filename,
      lineno: ev.lineno,
      colno: ev.colno,
    });
  });

  window.addEventListener("unhandledrejection", (ev) => {
    trackError("unhandledrejection", ev.reason);
  });
}
