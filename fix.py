
import os
for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith(('.py', '.jsx', '.css', '.md', '.html')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                text = text.replace('\ufffd', '-')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                print(e)

