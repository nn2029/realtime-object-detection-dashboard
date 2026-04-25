import { Activity, Boxes, Gauge, TimerReset } from "lucide-react";
import { formatNumber, formatPercent } from "../lib/streamClient";
import type { Metrics } from "../types";

type Props = {
  metrics: Metrics;
};

export function StatsCards({ metrics }: Props) {
  const cards = [
    {
      label: "Active",
      value: metrics.activeDetections,
      detail: `${metrics.detectionsSeen} total`,
      icon: Boxes,
    },
    {
      label: "Confidence",
      value: formatPercent(metrics.avgConfidence),
      detail: `${metrics.topLabels[0]?.[0] ?? "none"} top label`,
      icon: Gauge,
    },
    {
      label: "Throughput",
      value: formatNumber(metrics.fps, 1),
      detail: `${metrics.framesSeen} frames`,
      icon: Activity,
    },
    {
      label: "Latency",
      value: `${formatNumber(metrics.avgLatencyMs, 1)}ms`,
      detail: "rolling average",
      icon: TimerReset,
    },
  ];

  return (
    <section className="stats-grid" aria-label="detection metrics">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <article className="metric-card" key={card.label}>
            <div className="metric-icon">
              <Icon size={18} />
            </div>
            <div>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
              <small>{card.detail}</small>
            </div>
          </article>
        );
      })}
    </section>
  );
}
