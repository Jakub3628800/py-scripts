#!/usr/bin/env python3
import os
import subprocess
import time

# Setup history directory
HISTORY_DIR = os.path.join(os.path.expanduser('~'), '.clipboard_history')
os.makedirs(HISTORY_DIR, exist_ok=True)

while True:

   print("startloop")
   # Wait for clipboard change
   subprocess.run(['clipnotify'], check=True)

   try:
       # Get clipboard content
       clip = subprocess.run(
           ['xclip', '-sel', 'clip', '-o'],
           capture_output=True,
           text=True
       ).stdout
       print(clip)

       # Skip if empty
       if not clip.strip():
           continue

       # Save to file with timestamp
       timestamp = str(int(time.time()))
       file_path = os.path.join(HISTORY_DIR, timestamp)
       with open(file_path, 'w') as f:
           f.write(clip)

   except subprocess.CalledProcessError:
       continue
