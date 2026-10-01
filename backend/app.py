"""
Safe Bend Vision - Backend API
This Flask app serves the MJPEG streams and status JSON to the React frontend.
"""

from flask import Flask, Response, jsonify
from flask_cors import CORS
import sys, os, time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from detection import state, state_lock

app = Flask(__name__)
CORS(app)


@app.route("/api/status")
def get_status():
    with state_lock:
        return jsonify({
            "timestamp": time.time(),
            "side_a": {
                "status":        state["a"]["status"],
                "confidence":    state["a"]["confidence"],
                "vehicle_count": state["a"]["vehicle_count"],
            },
            "side_b": {
                "status":        state["b"]["status"],
                "confidence":    state["b"]["confidence"],
                "vehicle_count": state["b"]["vehicle_count"],
            },
            "alert": (
                state["a"]["status"] in ("close", "far") or
                state["b"]["status"] in ("close", "far")
            ),
        })


def _mjpeg(side_key):
    while True:
        with state_lock:
            frame = state[side_key]["frame"]
        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        time.sleep(0.04)


@app.route("/api/stream/a")
def stream_a():
    return Response(_mjpeg("a"), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/stream/b")
def stream_b():
    return Response(_mjpeg("b"), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
