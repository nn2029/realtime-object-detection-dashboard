import { Camera, CircleStop, Plug, RotateCcw, Signal, Unplug } from "lucide-react";
import type { ConnectionStatus, SourceMode } from "../types";

type Props = {
  status: ConnectionStatus;
  streamUrl: string;
  sourceMode: SourceMode;
  cameraEnabled: boolean;
  targetFps: number;
  onStreamUrlChange: (value: string) => void;
  onSourceModeChange: (value: SourceMode) => void;
  onTargetFpsChange: (value: number) => void;
  onConnect: () => void;
  onDisconnect: () => void;
  onReset: () => void;
  onStartCamera: () => void;
  onStopCamera: () => void;
};

export function ConnectionControls({
  status,
  streamUrl,
  sourceMode,
  cameraEnabled,
  targetFps,
  onStreamUrlChange,
  onSourceModeChange,
  onTargetFpsChange,
  onConnect,
  onDisconnect,
  onReset,
  onStartCamera,
  onStopCamera,
}: Props) {
  const connected = status === "connected";

  return (
    <section className="control-strip" aria-label="stream controls">
      <label className="field field-url">
        <span>Stream URL</span>
        <input
          value={streamUrl}
          onChange={(event) => onStreamUrlChange(event.target.value)}
          spellCheck={false}
        />
      </label>

      <div className="segmented" aria-label="source mode">
        <button
          className={sourceMode === "camera" ? "active" : ""}
          onClick={() => onSourceModeChange("camera")}
          type="button"
        >
          Camera
        </button>
        <button
          className={sourceMode === "demo" ? "active" : ""}
          onClick={() => onSourceModeChange("demo")}
          type="button"
        >
          Demo
        </button>
      </div>

      <label className="field field-fps">
        <span>FPS</span>
        <input
          type="range"
          min="1"
          max="15"
          value={targetFps}
          onChange={(event) => onTargetFpsChange(Number(event.target.value))}
        />
        <strong>{targetFps}</strong>
      </label>

      <div className="button-row">
        <button
          className="icon-button"
          onClick={connected ? onDisconnect : onConnect}
          title={connected ? "Disconnect stream" : "Connect stream"}
          type="button"
        >
          {connected ? <Unplug size={18} /> : <Plug size={18} />}
          <span>{connected ? "Disconnect" : "Connect"}</span>
        </button>
        <button
          className="icon-button"
          onClick={cameraEnabled ? onStopCamera : onStartCamera}
          title={cameraEnabled ? "Stop camera" : "Start camera"}
          type="button"
        >
          {cameraEnabled ? <CircleStop size={18} /> : <Camera size={18} />}
          <span>{cameraEnabled ? "Stop" : "Camera"}</span>
        </button>
        <button className="icon-button ghost" onClick={onReset} title="Reset metrics" type="button">
          <RotateCcw size={18} />
          <span>Reset</span>
        </button>
      </div>

      <div className={`status-pill status-${status}`}>
        <Signal size={16} />
        <span>{status}</span>
      </div>
    </section>
  );
}
