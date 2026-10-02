<div align="center">
  <h1>🛡️ Safe Bend Vision</h1>
  <p><b>AI-powered vehicle detection and warning system for blind curves on rural roads.</b></p>
  <p><i>Developed as a first-year Mechanical Engineering Technology project at the Faculty of Technology, Sabaragamuwa University of Sri Lanka (SUSL).</i></p>
</div>

<hr>

## 📖 Overview

Safe Bend Vision uses two USB cameras and a YOLOv8 object detection model running on a Raspberry Pi 5 to detect approaching vehicles on both sides of a blind road curve. When a vehicle is detected, the system activates a 12V LED warning light visible to oncoming drivers — green for clear, yellow for a distant vehicle, red for a close-range danger.

A Flask API streams both camera feeds (MJPEG) and exposes live detection state to a React dashboard accessible on any device on the local network.

<hr>

## ⚙️ System Architecture

<details>
<summary><b>View Architecture Diagram</b></summary>
<br>

```text
┌─────────────────────────────────────────────────────────┐
│                    Raspberry Pi 5                       │
│                                                         │
│   USB Camera A ──► detection.py (YOLOv8n)               │
│   USB Camera B ──► detection.py (YOLOv8n)               │
│                        │                                │
│               shared state (threading)                  │
│                        │                                │
│              backend/app.py (Flask)                     │
│               /api/status  (JSON)                       │
│               /api/stream/a  (MJPEG)                    │
│               /api/stream/b  (MJPEG)                    │
│                        │                                │
│           GPIO BCM 17,27,22 → Side A LEDs               │
│           GPIO BCM  5, 6,13 → Side B LEDs               │
└─────────────────────────────────────────────────────────┘
                         │
              React Dashboard (any browser)
```
</details>

<hr>

## 🛠 Hardware Components

<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>SBC</b></td>
      <td>Raspberry Pi 5 (4 GB)</td>
    </tr>
    <tr>
      <td><b>Cameras</b></td>
      <td>2× USB webcam (640×480)</td>
    </tr>
    <tr>
      <td><b>Warning lights</b></td>
      <td>6× 12V LED (Red, Green, Blue × 2 sides)</td>
    </tr>
    <tr>
      <td><b>GPIO driver</b></td>
      <td>NPN transistor array (BC547) or relay module</td>
    </tr>
    <tr>
      <td><b>Power</b></td>
      <td>5V/5A USB-C (Pi) + 12V for LEDs</td>
    </tr>
  </tbody>
</table>

### 🔌 GPIO Pin Map

<div align="center">
  <table>
    <thead>
      <tr>
        <th>Side</th>
        <th>Color</th>
        <th>BCM</th>
        <th>Physical</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>A</td><td>🔴 Red</td><td>17</td><td>11</td></tr>
      <tr><td>A</td><td>🟢 Green</td><td>27</td><td>13</td></tr>
      <tr><td>A</td><td>🔵 Blue</td><td>22</td><td>15</td></tr>
      <tr><td>B</td><td>🔴 Red</td><td>5</td><td>29</td></tr>
      <tr><td>B</td><td>🟢 Green</td><td>6</td><td>31</td></tr>
      <tr><td>B</td><td>🔵 Blue</td><td>13</td><td>33</td></tr>
    </tbody>
  </table>
</div>
<p align="center"><i>See <code><a href="docs/wiring.md">docs/wiring.md</a></code> for the full wiring diagram.</i></p>

<hr>

## 🚦 LED Warning Logic

<table>
  <thead>
    <tr>
      <th>Detection State</th>
      <th>Side A LED</th>
      <th>Side B LED</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>No vehicle</td><td>🟢 Green</td><td>🟢 Green</td></tr>
    <tr><td>Vehicle far (>3% bbox)</td><td>🟡 Yellow (R+G)</td><td>🟡 Yellow (R+G)</td></tr>
    <tr><td>Vehicle close (>15% bbox)</td><td>🔴 Red</td><td>🔴 Red</td></tr>
    <tr><td>Camera fault / boot</td><td>🔵 Blue</td><td>🔵 Blue</td></tr>
  </tbody>
</table>

<hr>

## 📂 Project Structure

```bash
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

<hr>

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ppnpathirana/SAFE-BEND-VISION-.git
cd safe-bend-vision
```

### 2️⃣ Install Python Dependencies
<i>(Run on Raspberry Pi 5)</i>
```bash
pip install -r requirements.txt --break-system-packages
```

### 3️⃣ Download YOLOv8 Model
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
mv yolov8n.pt models/
```

### 4️⃣ Verify Camera Indices
```bash
ls /dev/video*
```
> Update `CAMERA_A_INDEX` and `CAMERA_B_INDEX` in `detection.py` if needed.

### 5️⃣ Run the System
```bash
python run.py
```
> The Flask API will start at `http://0.0.0.0:5000`.

<hr>

## 💻 Dashboard (React)

```bash
cd frontend
npm install
npm run dev
```
> Open `http://<PI_IP>:3000` in any browser on the same network.

<b>Note:</b> Change the `API` constant in `frontend/src/App.jsx` to your Pi's IP address:
```javascript
const API = "http://192.168.1.xxx:5000";
```

<hr>

## 🌐 API Endpoints

<table>
  <thead>
    <tr>
      <th>Method</th>
      <th>Endpoint</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>GET</code></td><td><code>/api/status</code></td><td>JSON: live detection state, alert flag</td></tr>
    <tr><td><code>GET</code></td><td><code>/api/stream/a</code></td><td>MJPEG stream — Camera A</td></tr>
    <tr><td><code>GET</code></td><td><code>/api/stream/b</code></td><td>MJPEG stream — Camera B</td></tr>
    <tr><td><code>GET</code></td><td><code>/api/health</code></td><td>Health check</td></tr>
  </tbody>
</table>

<details>
<summary><b>Example <code>/api/status</code> Response</b></summary>
<br>

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
</details>

<hr>

## ⚙️ Detection Configuration

Edit these constants in `detection.py`:

<table>
  <thead>
    <tr>
      <th>Constant</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>MODEL_PATH</code></td><td><code>models/yolov8n.pt</code></td><td>YOLOv8 model path</td></tr>
    <tr><td><code>CONFIDENCE_THRESH</code></td><td><code>0.45</code></td><td>Minimum detection confidence</td></tr>
    <tr><td><code>CLOSE_THRESH</code></td><td><code>0.15</code></td><td>Bbox area ratio → RED alert</td></tr>
    <tr><td><code>FAR_THRESH</code></td><td><code>0.03</code></td><td>Bbox area ratio → YELLOW alert</td></tr>
    <tr><td><code>VEHICLE_CLASSES</code></td><td><code>{2,3,5,7}</code></td><td>COCO: car, motorcycle, bus, truck</td></tr>
  </tbody>
</table>

<hr>

## 🔬 Research Context

<blockquote>
<p>Submitted as part of <b>URSTech 2026</b> — University Research Symposium on Technology, SUSL.</p>
<p><b>Problem:</b> Blind curves on rural mountain roads cause high rates of head-on collisions due to zero visibility of oncoming vehicles.</p>
<p><b>Solution:</b> Low-cost, edge-deployed AI system that warns drivers in real time using visible LED signals, without requiring network connectivity or cloud infrastructure.</p>
</blockquote>

<hr>

## ✍️ Author

<p align="center">
  <b>P.P.N. PATHIRANA</b><br>
  <i>Faculty of Technology — Mechanical Technology</i><br>
  <i>Sabaragamuwa University of Sri Lanka</i><br>
  <b>IAENG Member No.</b> 566684
</p>

<hr>

## 📜 License

<p align="center">
  This project is licensed under the <b>MIT License</b> — see the <code>LICENSE</code> file for details.
</p>
