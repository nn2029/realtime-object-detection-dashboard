import type { RefObject } from "react";
import { ScanSearch } from "lucide-react";
import type { Detection, SourceMode } from "../types";

type Props = {
  videoRef: RefObject<HTMLVideoElement>;
  canvasRef: RefObject<HTMLCanvasElement>;
  sourceMode: SourceMode;
  cameraEnabled: boolean;
  detectorName: string;
  detections: Detection[];
};

export function DetectionStage({
  videoRef,
  canvasRef,
  sourceMode,
  cameraEnabled,
  detectorName,
  detections,
}: Props) {
  return (
    <section className="stage-shell" aria-label="detection viewport">
      <div className="stage-toolbar">
        <div>
          <ScanSearch size={18} />
          <span>{detectorName}</span>
        </div>
        <strong>{detections.length} boxes</strong>
      </div>
      <div className="detection-stage">
        <video
          ref={videoRef}
          className={sourceMode === "camera" && cameraEnabled ? "visible" : ""}
          playsInline
          muted
        />
        <canvas ref={canvasRef} />
      </div>
    </section>
  );
}
