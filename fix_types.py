import re

with open('detection.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('import time', 'import time\nfrom typing import Tuple, Any, Dict')

content = content.replace(
    'def classify_bbox(x1, y1, x2, y2, fw, fh):',
    'def classify_bbox(x1: int, y1: int, x2: int, y2: int, fw: int, fh: int) -> str:'
)

content = content.replace(
    'def process_frame(frame, side_label, led: SideLEDs):',
    'def process_frame(frame: Any, side_label: str, led: SideLEDs) -> Tuple[Any, str, float, int]:'
)

content = content.replace(
    'def camera_loop(cam_index, side_label, led):',
    'def camera_loop(cam_index: int, side_label: str, led: SideLEDs) -> None:'
)

leds_doc = '''class SideLEDs:
    """Manages the three warning LEDs (Red, Green, Blue) for a specific side."""
    def __init__(self, pin_r: int, pin_g: int, pin_b: int, name: str) -> None:'''
content = content.replace(
    'class SideLEDs:\n    def __init__(self, pin_r, pin_g, pin_b, name):',
    leds_doc
)

with open('detection.py', 'w', encoding='utf-8') as f:
    f.write(content)
