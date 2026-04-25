import type { Metrics } from "../types";

export const emptyMetrics: Metrics = {
  framesSeen: 0,
  detectionsSeen: 0,
  activeDetections: 0,
  avgConfidence: 0,
  avgLatencyMs: 0,
  fps: 0,
  classCounts: {},
  topLabels: [],
  timeline: [],
};

export function defaultStreamUrl(): string {
  const configured = import.meta.env.VITE_STREAM_URL as string | undefined;
  if (configured) {
    return configured;
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const host = window.location.hostname || "localhost";
  return `${protocol}://${host}:8000/ws/detect`;
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function formatNumber(value: number, digits = 0): string {
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(Number.isFinite(value) ? value : 0);
}
