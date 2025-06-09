#!/usr/bin/python3

import subprocess
import os
import sys
import time
from datetime import datetime

# Function to send desktop notifications
def send_notification(message: str) -> None:
    subprocess.run([
        '/usr/bin/notify-send',
        '-t',
        '5000',
        'Audio Recording',
        message,
    ])

# Use local tmp directory - uncomment to save in tmp folder
# tmp_dir = os.path.abspath("tmp")
# if not os.path.exists(tmp_dir):
#     os.makedirs(tmp_dir)
#     send_notification(f"Created directory: {tmp_dir}")
# output_file = os.path.join(tmp_dir, f"recording_{timestamp}.wav")

# Generate unique filename based on timestamp in current directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = os.path.abspath(f"recording_{timestamp}.wav")
stop_file = "/home/jk/tmp/stop_recording"

# Notify before starting recording
send_notification("Starting audio recording...")
#send_notification(f"Will save to: {output_file}")

# Start recording in background
try:
    arecord_process = subprocess.Popen(['/usr/bin/arecord', '-f', 'cd', '-t', 'wav', output_file],
                                      stderr=subprocess.DEVNULL)
except Exception as e:
    error_msg = f"Failed to start recording: {str(e)}"
    send_notification(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

# Check for stop file
try:
    while not os.path.exists(stop_file):
        # Check if arecord is still running
        if arecord_process.poll() is not None:
            error_msg = f"Recording process failed with return code: {arecord_process.returncode}"
            send_notification(error_msg)
            print(error_msg, file=sys.stderr)
            sys.exit(1)
        time.sleep(0.5)

    # Stop recording
    arecord_process.terminate()
    arecord_process.wait()

    # Verify recording was created successfully
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        # Notify of successful recording
        send_notification(f"Recording completed: {output_file}")
        # Print the absolute path to stdout so transcribe.py can find it
        print(output_file)
        sys.stdout.flush()
    else:
        error_msg = f"Failed to create recording file: {output_file}"
        send_notification(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

except KeyboardInterrupt:
    # Handle Ctrl+C
    send_notification("Recording interrupted by user")
    arecord_process.terminate()
    arecord_process.wait()

    # Verify recording was created successfully
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        # Notify of successful recording (interrupted)
        send_notification(f"Recording interrupted but saved: {output_file}")
        # Print the absolute path to stdout so transcribe.py can find it
        print(output_file)
        sys.stdout.flush()
    else:
        error_msg = f"Recording interrupted and file not created properly: {output_file}"
        send_notification(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

except Exception as e:
    error_msg = f"Unexpected error occurred: {str(e)}"
    send_notification(error_msg)
    print(error_msg, file=sys.stderr)
    sys.exit(1)

finally:
    # Clean up stop file
    if os.path.exists(stop_file):
        os.remove(stop_file)
