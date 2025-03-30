#!/bin/bash
# Record audio (using something like arecord or parecord)
audio=$(/home/jk/repos/gists/s2t/record_audio.py)

source /home/jk/repos/gists/s2t/.env && /home/jk/repos/gists/s2t/transcribe.py --debug $audio > /tmp/dictation.txt

# Use wtype to input the text
text=$(cat /tmp/dictation.txt)
wl-copy -p "$text"
