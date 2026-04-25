export type SourceMode = "camera" | "demo";

export type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export type Detection = {
  label: string;
  confidence: number;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  trackId: string | null;
  color: string;
};

export type MetricPoint = {
  frameId: number;
  timestamp: number;
  detections: number;
  avgConfidence: number;
};

export type Metrics = {
  framesSeen: number;
  detectionsSeen: number;
  activeDetections: number;
  avgConfidence: number;
  avgLatencyMs: number;
  fps: number;
  classCounts: Record<string, number>;
  topLabels: [string, number][];
  timeline: MetricPoint[];
};

export type DetectionResult = {
  frameId: number;
  timestamp: number;
  detector: string;
  latencyMs: number;
  detections: Detection[];
  metrics: Metrics;
};

export type StreamEvent = {
  id: string;
  time: string;
  frameId: number;
  summary: string;
  confidence: number;
  count: number;
};
