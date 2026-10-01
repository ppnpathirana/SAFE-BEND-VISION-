"""
Safe Bend Vision - Object detection script
This script runs the YOLOv8 model on two USB cameras and controls the GPIO LED warnings.
"""

import cv2
import threading
import time
from typing import Tuple, Any, Dict
import logging
from ultralytics import YOLO
from gpiozero import LED

# Setup basic logging so we can see what is happening in the terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("SafeBend")

# Load up our YOLOv8 model for vehicle detection
MODEL_PATH        = "models/yolov8n.pt"
CAMERA_A_INDEX    = 0
CAMERA_B_INDEX    = 2
FRAME_WIDTH       = 640
FRAME_HEIGHT      = 480
CONFIDENCE_THRESH = 0.45
VEHICLE_CLASSES   = {2, 3, 5, 7}   # car, motorcycle, bus, truck

# Bounding-box area ratio thresholds
CLOSE_THRESH = 0.15   # > 15% of frame → RED
FAR_THRESH   = 0.03   # 3–15%          → YELLOW
                       # < 3% / none    → GREEN

# Hardware setup: Define how we talk to the warning LEDs via GPIO
class SideLEDs:
    """Manages the three warning LEDs (Red, Green, Blue) for a specific side."""
    def __init__(self, pin_r: int, pin_g: int, pin_b: int, name: str) -> None:
        self.name = name
        self.r = LED(pin_r)
        self.g = LED(pin_g)
        self.b = LED(pin_b)
        self.set_green()

    def _all_off(self):
        self.r.off(); self.g.off(); self.b.off()

    def set_green(self):
        self._all_off(); self.g.on()
        log.debug(f"{self.name} → GREEN")

    def set_yellow(self):
        self._all_off(); self.r.on(); self.g.on()
        log.debug(f"{self.name} → YELLOW")

    def set_red(self):
        self._all_off(); self.r.on()
        log.debug(f"{self.name} → RED")

    def set_blue(self):
        self._all_off(); self.b.on()

    def cleanup(self):
        self._all_off()


led_a = SideLEDs(17, 27, 22, "Side-A")
led_b = SideLEDs( 5,  6, 13, "Side-B")

# A thread-safe dictionary to share camera data with the Flask API
state = {
    "a": {"status": "clear", "confidence": 0.0, "vehicle_count": 0, "frame": None},
    "b": {"status": "clear", "confidence": 0.0, "vehicle_count": 0, "frame": None},
}
state_lock = threading.Lock()

# Load up our YOLOv8 model for vehicle detection
model = YOLO(MODEL_PATH)
log.info(f"YOLOv8 model loaded: {MODEL_PATH}")

# Helper functions to figure out how close the vehicles actually are
def classify_bbox(x1: int, y1: int, x2: int, y2: int, fw: int, fh: int) -> str:
    ratio = ((x2 - x1) * (y2 - y1)) / (fw * fh)
    if ratio >= CLOSE_THRESH:
        return "close"
    elif ratio >= FAR_THRESH:
        return "far"
    return "clear"


def process_frame(frame: Any, side_label: str, led: SideLEDs) -> Tuple[Any, str, float, int]:
    h, w = frame.shape[:2]
    results = model(frame, conf=CONFIDENCE_THRESH, verbose=False)[0]

    worst     = "clear"
    best_conf = 0.0
    count     = 0

    for box in results.boxes:
        if int(box.cls[0]) not in VEHICLE_CLASSES:
            continue
        count += 1
        conf  = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        severity = classify_bbox(x1, y1, x2, y2, w, h)

        color = {"close": (0, 0, 255), "far": (0, 165, 255), "clear": (0, 255, 0)}.get(severity)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{severity.upper()} {conf:.2f}",
                    (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        if severity == "close":
            worst = "close"; best_conf = max(best_conf, conf)
        elif severity == "far" and worst != "close":
            worst = "far"; best_conf = max(best_conf, conf)

    if worst == "close":
        led.set_red()
    elif worst == "far":
        led.set_yellow()
    else:
        led.set_green()

    cv2.putText(frame, f"SIDE {side_label.upper()} | {worst.upper()}",
                (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return frame, worst, best_conf, count


# The main loop for each camera: grabs frames, runs YOLO, updates LEDs and state
def camera_loop(cam_index: int, side_label: str, led: SideLEDs) -> None:
    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        log.error(f"Cannot open camera {cam_index} (Side {side_label})")
        led.set_blue()
        return

    log.info(f"Camera {cam_index} opened → Side {side_label.upper()}")

    while True:
        ret, frame = cap.read()
        if not ret:
            log.warning(f"Side {side_label}: frame grab failed, retrying…")
            time.sleep(0.1)
            continue

        annotated, status, conf, count = process_frame(frame, side_label, led)
        _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 75])

        with state_lock:
            state[side_label]["status"]        = status
            state[side_label]["confidence"]    = round(conf, 3)
            state[side_label]["vehicle_count"] = count
            state[side_label]["frame"]         = buf.tobytes()

        time.sleep(0.03)

    cap.release()


# Spin up everything when we run the script directly
if __name__ == "__main__":
    log.info("Safe Bend Vision — starting detection threads")

    t_a = threading.Thread(target=camera_loop, args=(CAMERA_A_INDEX, "a", led_a), daemon=True)
    t_b = threading.Thread(target=camera_loop, args=(CAMERA_B_INDEX, "b", led_b), daemon=True)
    t_a.start()
    t_b.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Shutting down…")
        led_a.cleanup()
        led_b.cleanup()
