"""
Safe Bend Vision — Unified Launcher
=====================================
Starts detection threads + Flask API in one process.

Usage:
    python run.py
"""

import threading
from detection import camera_loop, led_a, led_b, CAMERA_A_INDEX, CAMERA_B_INDEX, log
from backend.app import app


def main():
    t_a = threading.Thread(target=camera_loop, args=(CAMERA_A_INDEX, "a", led_a), daemon=True)
    t_b = threading.Thread(target=camera_loop, args=(CAMERA_B_INDEX, "b", led_b), daemon=True)
    t_a.start()
    t_b.start()
    log.info("Detection threads started — Camera A and Camera B")
    log.info("Flask API starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
