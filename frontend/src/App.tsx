import { useCallback, useEffect, useRef, useState } from "react";
import { ConnectionControls } from "./components/ConnectionControls";
import { ConfidenceTimeline } from "./components/ConfidenceTimeline";
import { DetectionStage } from "./components/DetectionStage";
import { EventStream } from "./components/EventStream";
import { StatsCards } from "./components/StatsCards";
import { defaultStreamUrl, emptyMetrics } from "./lib/streamClient";
import type { ConnectionStatus, Detection, DetectionResult, Metrics, SourceMode, StreamEvent } from "./types";

function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const overlayRef = useRef<HTMLCanvasElement>(null);
  const captureRef = useRef<HTMLCanvasElement>(document.createElement("canvas"));
  const socketRef = useRef<WebSocket | null>(null);
  const inFlightRef = useRef(false);
  const frameIdRef = useRef(0);
  const lastSentAtRef = useRef(0);

  const [streamUrl, setStreamUrl] = useState(defaultStreamUrl);
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [sourceMode, setSourceMode] = useState<SourceMode>("demo");
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [targetFps, setTargetFps] = useState(8);
  const [detectorName, setDetectorName] = useState("mock-yolo");
  const [detections, setDetections] = useState<Detection[]>([]);
  const [metrics, setMetrics] = useState<Metrics>(emptyMetrics);
  const [events, setEvents] = useState<StreamEvent[]>([]);

  const disconnect = useCallback(() => {
    socketRef.current?.close();
    socketRef.current = null;
    inFlightRef.current = false;
    setStatus("disconnected");
  }, []);

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus("connecting");
    const socket = new WebSocket(streamUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus("connected");
      inFlightRef.current = false;
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === "ready") {
        setDetectorName(message.payload.detector);
        setMetrics(message.payload.metrics ?? emptyMetrics);
        return;
      }

      if (message.type === "metrics") {
        setMetrics(message.payload ?? emptyMetrics);
        return;
      }

      if (message.type === "detections") {
        const payload = message.payload as DetectionResult;
        inFlightRef.current = false;
        setDetectorName(payload.detector);
        setDetections(payload.detections);
        setMetrics(payload.metrics);
        setEvents((current) => [toStreamEvent(payload), ...current].slice(0, 28));
      }

      if (message.type === "error") {
        inFlightRef.current = false;
        setStatus("error");
      }
    };

    socket.onerror = () => {
      inFlightRef.current = false;
      setStatus("error");
    };

    socket.onclose = () => {
      inFlightRef.current = false;
      setStatus("disconnected");
    };
  }, [streamUrl]);

  const resetMetrics = useCallback(() => {
    setEvents([]);
    setDetections([]);
    setMetrics(emptyMetrics);
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "reset" }));
    }
  }, []);

  const startCamera = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setSourceMode("demo");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "environment",
        },
        audio: false,
      });

      const video = videoRef.current;
      if (video) {
        video.srcObject = stream;
        await video.play();
      }
      setCameraEnabled(true);
      setSourceMode("camera");
    } catch {
      setCameraEnabled(false);
      setSourceMode("demo");
    }
  }, []);

  const stopCamera = useCallback(() => {
    const video = videoRef.current;
    const stream = video?.srcObject as MediaStream | null;
    stream?.getTracks().forEach((track) => track.stop());
    if (video) {
      video.srcObject = null;
    }
    setCameraEnabled(false);
    setSourceMode("demo");
  }, []);

  const sendFrame = useCallback(() => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN || inFlightRef.current) {
      return;
    }

    const frameId = ++frameIdRef.current;
    let width = 960;
    let height = 540;
    let image: string | undefined;

    const video = videoRef.current;
    if (sourceMode === "camera" && cameraEnabled && video && video.readyState >= 2) {
      width = Math.min(video.videoWidth || 960, 720);
      height = Math.round(width / ((video.videoWidth || 16) / (video.videoHeight || 9)));
      const capture = captureRef.current;
      capture.width = width;
      capture.height = height;
      capture.getContext("2d")?.drawImage(video, 0, 0, width, height);
      image = capture.toDataURL("image/jpeg", 0.68);
    }

    inFlightRef.current = true;
    socket.send(
      JSON.stringify({
        type: "frame",
        frameId,
        timestamp: Date.now() / 1000,
        width,
        height,
        image,
        metadata: { source: sourceMode },
      }),
    );
  }, [cameraEnabled, sourceMode]);

  useEffect(() => {
    let animationId = 0;

    const tick = (now: number) => {
      const interval = 1000 / targetFps;
      if (status === "connected" && now - lastSentAtRef.current >= interval) {
        lastSentAtRef.current = now;
        sendFrame();
      }
      animationId = window.requestAnimationFrame(tick);
    };

    animationId = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(animationId);
  }, [sendFrame, status, targetFps]);

  useEffect(() => {
    drawOverlay(overlayRef.current, detections, sourceMode, cameraEnabled);
  }, [cameraEnabled, detections, sourceMode]);

  useEffect(() => {
    const handleResize = () => drawOverlay(overlayRef.current, detections, sourceMode, cameraEnabled);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [cameraEnabled, detections, sourceMode]);

  useEffect(() => {
    return () => {
      disconnect();
      const stream = videoRef.current?.srcObject as MediaStream | null;
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, [disconnect]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p>Computer Vision Operations</p>
          <h1>Real-Time Object Detection Dashboard</h1>
        </div>
        <div className="topbar-meta">
          <span>YOLO-ready</span>
          <strong>{detectorName}</strong>
        </div>
      </header>

      <ConnectionControls
        status={status}
        streamUrl={streamUrl}
        sourceMode={sourceMode}
        cameraEnabled={cameraEnabled}
        targetFps={targetFps}
        onStreamUrlChange={setStreamUrl}
        onSourceModeChange={setSourceMode}
        onTargetFpsChange={setTargetFps}
        onConnect={connect}
        onDisconnect={disconnect}
        onReset={resetMetrics}
        onStartCamera={startCamera}
        onStopCamera={stopCamera}
      />

      <StatsCards metrics={metrics} />

      <section className="workspace-grid">
        <DetectionStage
          videoRef={videoRef}
          canvasRef={overlayRef}
          sourceMode={sourceMode}
          cameraEnabled={cameraEnabled}
          detectorName={detectorName}
          detections={detections}
        />
        <EventStream events={events} />
        <ConfidenceTimeline points={metrics.timeline} />
      </section>
    </main>
  );
}

function toStreamEvent(payload: DetectionResult): StreamEvent {
  const topDetection = [...payload.detections].sort((a, b) => b.confidence - a.confidence)[0];
  const summary = topDetection
    ? `${topDetection.label} detected`
    : "No detections";
  const confidence = topDetection?.confidence ?? 0;

  return {
    id: `${payload.frameId}-${payload.timestamp}`,
    time: new Date(payload.timestamp * 1000).toLocaleTimeString(),
    frameId: payload.frameId,
    summary,
    confidence,
    count: payload.detections.length,
  };
}

function drawOverlay(
  canvas: HTMLCanvasElement | null,
  detections: Detection[],
  sourceMode: SourceMode,
  cameraEnabled: boolean,
) {
  if (!canvas) {
    return;
  }

  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * dpr));
  canvas.height = Math.max(1, Math.floor(rect.height * dpr));

  const context = canvas.getContext("2d");
  if (!context) {
    return;
  }

  context.setTransform(dpr, 0, 0, dpr, 0, 0);
  context.clearRect(0, 0, rect.width, rect.height);

  if (sourceMode === "demo" || !cameraEnabled) {
    drawDemoFrame(context, rect.width, rect.height);
  }

  detections.forEach((detection) => {
    const x = detection.bbox.x * rect.width;
    const y = detection.bbox.y * rect.height;
    const width = detection.bbox.width * rect.width;
    const height = detection.bbox.height * rect.height;
    const label = `${detection.label} ${Math.round(detection.confidence * 100)}%`;

    context.strokeStyle = detection.color;
    context.lineWidth = 2;
    context.strokeRect(x, y, width, height);
    context.fillStyle = detection.color;
    context.font = "600 12px Inter, system-ui, sans-serif";
    const labelWidth = Math.min(context.measureText(label).width + 14, rect.width - x - 4);
    context.fillRect(x, Math.max(0, y - 24), labelWidth, 22);
    context.fillStyle = "#101311";
    context.fillText(label, x + 7, Math.max(15, y - 8));
  });
}

function drawDemoFrame(context: CanvasRenderingContext2D, width: number, height: number) {
  const gradient = context.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, "#151713");
  gradient.addColorStop(0.52, "#20241d");
  gradient.addColorStop(1, "#111312");
  context.fillStyle = gradient;
  context.fillRect(0, 0, width, height);

  context.strokeStyle = "rgba(255, 255, 255, 0.08)";
  context.lineWidth = 1;
  for (let x = 0; x < width; x += 48) {
    context.beginPath();
    context.moveTo(x, 0);
    context.lineTo(x, height);
    context.stroke();
  }
  for (let y = 0; y < height; y += 48) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(width, y);
    context.stroke();
  }

  context.fillStyle = "rgba(34, 197, 94, 0.1)";
  context.fillRect(0, height * 0.58, width, 2);
  context.fillStyle = "rgba(14, 165, 233, 0.14)";
  context.fillRect(width * 0.18, height * 0.18, width * 0.18, height * 0.52);
  context.fillStyle = "rgba(249, 115, 22, 0.14)";
  context.fillRect(width * 0.62, height * 0.22, width * 0.2, height * 0.44);
}

export default App;
