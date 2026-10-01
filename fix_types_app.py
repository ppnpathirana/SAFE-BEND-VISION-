import re

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('import sys, os, time', 'import sys, os, time\nfrom typing import Any, Generator')

content = content.replace(
    'def get_status():',
    'def get_status() -> Any:'
)

content = content.replace(
    'def _mjpeg(side_key):',
    'def _mjpeg(side_key: str) -> Generator[bytes, None, None]:'
)

content = content.replace(
    'def stream_a():',
    'def stream_a() -> Response:'
)

content = content.replace(
    'def stream_b():',
    'def stream_b() -> Response:'
)

content = content.replace(
    'def health():',
    'def health() -> Any:'
)

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
