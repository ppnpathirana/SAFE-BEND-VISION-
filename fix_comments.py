import re

def update_file(filename, replacements, docstring=None):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for k, v in replacements.items():
            pattern = r'#.*?' + k + r'.*?\n'
            content = re.sub(pattern, v + '\n', content, flags=re.IGNORECASE)
            
        if docstring:
            content = re.sub(r'\"\"\"[\s\S]*?\"\"\"', docstring, content, count=1)
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f'Error updating {filename}: {e}')

det_repl = {
    'Logging': '# Setup basic logging so we can see what is happening in the terminal',
    'Config': '# Project Configuration (Camera indices, model paths, and thresholds)',
    'GPIO': '# Hardware setup: Define how we talk to the warning LEDs via GPIO',
    'Shared state': '# A thread-safe dictionary to share camera data with the Flask API',
    'Model': '# Load up our YOLOv8 model for vehicle detection',
    'Detection helpers': '# Helper functions to figure out how close the vehicles actually are',
    'Camera thread': '# The main loop for each camera: grabs frames, runs YOLO, updates LEDs and state',
    'Entry point': '# Spin up everything when we run the script directly'
}
det_doc = '\"\"\"\nSafe Bend Vision - Object detection script\nThis script runs the YOLOv8 model on two USB cameras and controls the GPIO LED warnings.\n\"\"\"'
update_file('detection.py', det_repl, det_doc)

app_repl = {}
app_doc = '\"\"\"\nSafe Bend Vision - Backend API\nThis Flask app serves the MJPEG streams and status JSON to the React frontend.\n\"\"\"'
update_file('backend/app.py', app_repl, app_doc)

run_repl = {}
run_doc = '\"\"\"\nSafe Bend Vision - Unified Launcher\nThis script starts both the camera detection threads and the Flask server at once.\n\"\"\"'
update_file('run.py', run_repl, run_doc)
