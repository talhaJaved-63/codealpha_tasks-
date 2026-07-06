"""
Object Detection and Tracking System
Uses YOLOv8 for detection and Deep SORT-inspired tracker for tracking.
"""
import argparse
import time
import cv2
import numpy as np
from ultralytics import YOLO
from tracker import CentroidTracker, TrackableObject


def parse_args():
    parser = argparse.ArgumentParser(description="Real-time Object Detection and Tracking")
    parser.add_argument(
        "--source", type=str, default="0",
        help="Video source: 0 for webcam, or path to video file"
    )
    parser.add_argument(
        "--model", type=str, default="yolov8n.pt",
        help="YOLOv8 model variant (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)"
    )
    parser.add_argument(
        "--confidence", type=float, default=0.5,
        help="Minimum confidence threshold for detections"
    )
    parser.add_argument(
        "--classes", type=str, default=None,
        help="Comma-separated class IDs to detect (e.g., 0,2,7 for person,car,truck)"
    )
    parser.add_argument(
        "--max-disappeared", type=int, default=50,
        help="Maximum frames an object can disappear before being deregistered"
    )
    parser.add_argument(
        "--max-distance", type=int, default=50,
        help="Maximum pixel distance for centroid matching"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Path to save output video (e.g., output.mp4)"
    )
    parser.add_argument(
        "--show-fps", action="store_true", default=True,
        help="Display FPS on the output frame"
    )
    return parser.parse_args()


class DetectionTracker:
    def __init__(self, model_path, confidence, classes, max_disappeared, max_distance):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.classes = [int(c) for c in classes.split(",")] if classes else None
        self.tracker = CentroidTracker(
            max_disappeared=max_disappeared,
            max_distance=max_distance
        )

    def detect(self, frame):
        results = self.model(frame, verbose=False)
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                if self.classes and cls not in self.classes:
                    continue
                if conf < self.confidence:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append((x1, y1, x2, y2, conf, cls))
        return detections

    def update(self, frame):
        detections = self.detect(frame)
        rects = []
        for det in detections:
            x1, y1, x2, y2 = det[:4]
            rects.append((x1, y1, x2, y2))

        objects = self.tracker.update(rects)
        return detections, objects


def draw_detections(frame, detections, objects, class_names, show_fps=True, fps=0):
    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label_text = f"{class_names.get(cls, 'N/A')}: {conf:.2f}"
        color = _get_color(cls)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame, label_text, (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
        )

    for object_id, centroid in objects.items():
        cv2.putText(
            frame, f"ID {object_id}",
            (centroid[0] - 10, centroid[1] - 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2
        )
        cv2.circle(frame, (centroid[0], centroid[1]), 6, (0, 255, 255), -1)

    if show_fps:
        cv2.putText(
            frame, f"FPS: {fps:.1f}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
        )

    info_y = 60
    cv2.putText(
        frame, f"Objects tracked: {len(objects)}", (10, info_y),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
    )
    return frame


def _get_color(cls_id):
    np.random.seed(cls_id * 42)
    return tuple(np.random.randint(0, 255, 3).tolist())


def main():
    args = parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video source: {args.source}")
        return

    detector = DetectionTracker(
        model_path=args.model,
        confidence=args.confidence,
        classes=args.classes,
        max_disappeared=args.max_disappeared,
        max_distance=args.max_distance
    )

    class_names = detector.model.names

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_src = cap.get(cv2.CAP_PROP_FPS) or 30.0
    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(args.output, fourcc, int(fps_src), (width, height))

    print("[INFO] Starting detection and tracking...")
    print(f"[INFO] Source: {args.source}, Model: {args.model}")
    print("[INFO] Press 'q' to quit")

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of video stream or cannot read frame.")
            break

        detections, objects = detector.update(frame)

        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        output_frame = draw_detections(
            frame, detections, objects, class_names,
            show_fps=args.show_fps, fps=fps
        )

        if writer:
            writer.write(output_frame)

        cv2.imshow("Object Detection & Tracking", output_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print("[INFO] Session ended.")


if __name__ == "__main__":
    main()
