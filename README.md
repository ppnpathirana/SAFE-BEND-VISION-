# Safe Bend Vision

**AI-powered vehicle detection and warning system for blind curves on rural roads.**

Developed as a final-year engineering project at the Faculty of Technology, Sabaragamuwa University of Sri Lanka (SUSL).

---

## Overview

Safe Bend Vision uses two USB cameras and a YOLOv8 object detection model running on a Raspberry Pi 5 to detect approaching vehicles on both sides of a blind road curve. When a vehicle is detected, the system activates a 12V LED warning light visible to oncoming drivers — green for clear, yellow for a distant vehicle, red for a close-range danger.

A Flask API streams both camera feeds (MJPEG) and exposes live detection state to a React dashboard accessible on any device on the local network.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Raspberry Pi 5                        │
│                                                         │
│   USB Camera A ──► detection.py (YOLOv8n)              │
│   USB Camera B ──► detection.py (YOLOv8n)              │
│                        │                               │
│               shared state (threading)                  │
│                        │                               │
│              backend/app.py (Flask)                     │
│               /api/status  (JSON)                       │
│               /api/stream/a  (MJPEG)                    │
│               /api/stream/b  (MJPEG)                    │
│                        │                               │
│           GPIO BCM 17,27,22 → Side A LEDs              │
│           GPIO BCM  5, 6,13 → Side B LEDs              │
└─────────────────────────────────────────────────────────┘
                         │
              React Dashboard (any browser)
```

---

## Hardware

| Component            | Details                              |
|----------------------|--------------------------------------|
| SBC                  | Raspberry Pi 5 (4 GB)               |
| Cameras              | 2× USB webcam (640×480)             |
| Warning lights       | 6× 12V LED (Red, Green, Blue × 2 sides) |
| GPIO driver          | NPN transistor array (BC547) or relay module |
| Power                | 5V/5A USB-C (Pi) + 12V for LEDs    |

### GPIO Pin Map

| Side | Color | BCM | Physical |
|------|-------|-----|----------|
| A    | Red   | 17  | 11       |
| A    | Green | 27  | 13       |
| A    | Blue  | 22  | 15       |
| B    | Red   | 5   | 29       |
| B    | Green | 6   | 31       |
| B    | Blue  | 13  | 33       |

See [`docs/wiring.md`](docs/wiring.md) for the full wiring diagram.

---

## LED Warning Logic

| Detection State        | Side A LED       | Side B LED       |
|------------------------|------------------|------------------|
| No vehicle             | Green            | Green            |
| Vehicle far (>3% bbox) | Yellow (R+G)     | Yellow (R+G)     |
| Vehicle close (>15% bbox) | Red           | Red              |
| Camera fault / boot    | Blue             | Blue             |

---

## Project Structure

```
safe-bend-vision/
├── detection.py          # YOLOv8 detection + GPIO LED driver (threaded)
├── run.py                # Unified launcher: detection + Flask
├── requirements.txt      # Python dependencies
├── .gitignore
│
├── backend/
│   └── app.py            # Flask REST API + MJPEG stream
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx       # React dashboard
│       └── App.css
│
├── models/
│   └── .gitkeep          # Place yolov8n.pt here (not tracked by git)
│
└── docs/
    └── wiring.md         # GPIO wiring reference
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/safe-bend-vision.git
cd safe-bend-vision
```

### 2. Install Python dependencies (on Raspberry Pi 5)

```bash
pip install -r requirements.txt --break-system-packages
```

### 3. Download the YOLOv8 model

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
mv yolov8n.pt models/
```

### 4. Verify camera indices

```bash
ls /dev/video*
```

Update `CAMERA_A_INDEX` and `CAMERA_B_INDEX` in `detection.py` if needed.

### 5. Run the system

```bash
python run.py
```

Flask API will start at `http://0.0.0.0:5000`.

---

## Dashboard (React)

```bash
cd frontend
npm install
npm run dev
```

Open `http://<PI_IP>:3000` in any browser on the same network.

Change the `API` constant in `frontend/src/App.jsx` to your Pi's IP address:

```js
const API = "http://192.168.1.xxx:5000";
```

---

## API Endpoints

| Method | Endpoint         | Description                        |
|--------|------------------|------------------------------------|
| GET    | `/api/status`    | JSON: live detection state, alert flag |
| GET    | `/api/stream/a`  | MJPEG stream — Camera A            |
| GET    | `/api/stream/b`  | MJPEG stream — Camera B            |
| GET    | `/api/health`    | Health check                       |

### Example `/api/status` response

```json
{
  "timestamp": 1748000000.0,
  "alert": true,
  "side_a": {
    "status": "close",
    "confidence": 0.912,
    "vehicle_count": 1
  },
  "side_b": {
    "status": "clear",
    "confidence": 0.0,
    "vehicle_count": 0
  }
}
```

---

## Detection Config

Edit these constants in `detection.py`:

| Constant          | Default | Description                                 |
|-------------------|---------|---------------------------------------------|
| `MODEL_PATH`      | `models/yolov8n.pt` | YOLOv8 model path             |
| `CONFIDENCE_THRESH` | `0.45` | Minimum detection confidence               |
| `CLOSE_THRESH`    | `0.15`  | Bbox area ratio → RED alert                |
| `FAR_THRESH`      | `0.03`  | Bbox area ratio → YELLOW alert             |
| `VEHICLE_CLASSES` | `{2,3,5,7}` | COCO: car, motorcycle, bus, truck     |

---

## Research Context

Submitted as part of URSTech 2026 — University Research Symposium on Technology, SUSL.

**Problem:** Blind curves on rural mountain roads cause high rates of head-on collisions due to zero visibility of oncoming vehicles.

**Solution:** Low-cost, edge-deployed AI system that warns drivers in real time using visible LED signals, without requiring network connectivity or cloud infrastructure.

---

## Author

**P. Pathirana**
Faculty of Technology — Mechanical Technology
Sabaragamuwa University of Sri Lanka
IAENG Member No. 566684

---

## License

MIT License — see `LICENSE` for details.
