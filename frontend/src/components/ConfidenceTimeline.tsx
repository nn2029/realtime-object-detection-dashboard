import type { MetricPoint } from "../types";

type Props = {
  points: MetricPoint[];
};

export function ConfidenceTimeline({ points }: Props) {
  const width = 640;
  const height = 180;
  const padded = points.slice(-48);
  const maxDetections = Math.max(1, ...padded.map((point) => point.detections));
  const step = padded.length > 1 ? width / (padded.length - 1) : width;
  const confidenceLine = padded
    .map((point, index) => {
      const x = index * step;
      const y = height - point.avgConfidence * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <section className="timeline-panel" aria-label="confidence timeline">
      <div className="section-heading">
        <h2>Confidence Timeline</h2>
        <span>{padded.length} frames</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="confidence timeline chart">
        <defs>
          <linearGradient id="timelineFill" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="#22c55e" />
            <stop offset="55%" stopColor="#0ea5e9" />
            <stop offset="100%" stopColor="#f97316" />
          </linearGradient>
        </defs>
        {[0.25, 0.5, 0.75].map((line) => (
          <line
            className="grid-line"
            key={line}
            x1="0"
            x2={width}
            y1={height - line * height}
            y2={height - line * height}
          />
        ))}
        {padded.map((point, index) => {
          const barWidth = Math.max(4, step * 0.42);
          const barHeight = (point.detections / maxDetections) * height * 0.68;
          return (
            <rect
              className="detection-bar"
              key={point.frameId}
              x={index * step - barWidth / 2}
              y={height - barHeight}
              width={barWidth}
              height={barHeight}
              rx="3"
            />
          );
        })}
        {confidenceLine && <polyline className="confidence-line" points={confidenceLine} />}
      </svg>
    </section>
  );
}
